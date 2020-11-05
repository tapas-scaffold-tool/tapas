from typing import Tuple, Callable, Optional
import os
import sys
import json
import pkg_resources
from inspect import Parameter, signature
from encodings import utf_8
from pathlib import Path
from argparse import ArgumentParser

from jinja2 import Environment, StrictUndefined
from tabulate import tabulate

from tapas.context import ContextHolder, PromptMode
from tapas.index import (
    find_tapa_in_index,
    load_tapas_index,
    TapaSchema,
    parse_tapa_location,
    parse_index_location,
    DEFAULT_INDEX_LOCATION,
    load_tapa_from_gitthub,
)

TAPA_FILE = "tapa.py"
TEMPLATE_DIR = "template"

ASK_FUNCTION = "ask"
POST_INIT_FUNCTION = "post_init"

UTF_8 = utf_8.getregentry().name


def parse_path(path: str) -> Path:
    return Path(path).expanduser().resolve().absolute()


class App:
    def __init__(self, args):
        self.version = self._load_version()
        parser = self._init_parser(self.version)
        parser.parse_args(args, self)

        if not self.list and self.tapa is None:
            parser.error("Missing tapa name")

    def run(self) -> int:
        if self.list:
            return self._show_available_tapas()

        return self._apply_tapa()

    def _show_available_tapas(self) -> int:
        index = load_tapas_index(self.index)
        table = []
        for tapa_key in sorted(index.keys()):
            table.append([tapa_key, index[tapa_key].description])

        print(tabulate(table, headers=["Tapa name", "Description"]))
        return 0

    def _apply_tapa(self) -> int:
        if self.tapa.schema is TapaSchema.INDEX:
            tapa_dir = find_tapa_in_index(self.index, self.tapa.location)
            if tapa_dir is None:
                index_name = "default index" if self.index is DEFAULT_INDEX_LOCATION else f"index {self.index.location}"
                print(f'Tapa "{self.tapa.location}" not found in {index_name}')
                return 1
        elif self.tapa.schema is TapaSchema.GITHUB:
            tapa_dir = load_tapa_from_gitthub(self.tapa.location)
        elif self.tapa.schema is TapaSchema.DIRECTORY:
            tapa_dir = parse_path(self.tapa.location)
        else:
            raise NotImplementedError(f"Not implemented for schema {self.tapa.schema}")

        ask, post_init = _load_tapa(tapa_dir / TAPA_FILE)
        ContextHolder.init_context(prompt_mode=PromptMode.USER, values=_json_string_to_dict(self.params))
        if ask is not None:
            ask()

        params = ContextHolder.CONTEXT.dict

        self.target.mkdir(parents=True, exist_ok=True)
        code = _walk(tapa_dir / TEMPLATE_DIR, self.target, params, self.force)
        if code:
            return code

        if post_init is not None:
            sig = signature(post_init)

            post_init_params = {}
            for param in sig.parameters.values():
                if param.kind == Parameter.VAR_KEYWORD:
                    post_init_params = params
                    break
                elif param.kind in [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]:
                    if param.name in params:
                        post_init_params[param.name] = params[param.name]
                    else:
                        if param.default == Parameter.empty:
                            raise Exception(
                                "Post init function can contain only params asked in ask function or with default value"
                            )
                else:
                    raise Exception("Post init function can contain only named params and **kwargs")

            cwd = os.getcwd()
            os.chdir(self.target)
            code = post_init(**post_init_params)
            os.chdir(cwd)

        if code is None:
            code = 0
        return code

    @staticmethod
    def _load_version() -> str:
        version = pkg_resources.resource_string("tapas", "tapas.version")
        version = version.decode(UTF_8).strip()
        return version

    @staticmethod
    def _init_parser(version: str) -> ArgumentParser:
        parser = ArgumentParser()
        parser.add_argument("--version", action="version", version=version)
        parser.add_argument("-l", "--list", action="store_true", help="show list of available tapas and exit")
        parser.add_argument(
            "-i",
            "--index",
            type=parse_index_location,
            default=DEFAULT_INDEX_LOCATION,
            help="custom index",
            metavar="INDEX",
        )
        parser.add_argument("-f", "--force", action="store_true", help="rewrite files in target directory")
        parser.add_argument("-p", "--params", type=str, default=None, help="parameters json", metavar="JSON_OBJECT")
        parser.add_argument("tapa", type=parse_tapa_location, nargs="?", help="tapa name", metavar="TAPA")
        parser.add_argument(
            "target", type=parse_path, default=Path(os.getcwd()), nargs="?", help="target directory", metavar="TARGET"
        )
        return parser


def _walk(template_dir: Path, destination_dir: Path, params: dict, force: bool) -> int:
    if not template_dir.exists():
        print(f'Incorrect tapa. Template dir "{template_dir}" not found.')
        return 1

    env = Environment(undefined=StrictUndefined)

    for child in template_dir.glob("**/*"):
        relative = child.relative_to(template_dir)

        rendered = destination_dir / Path(*map(lambda p: env.from_string(p).render(params), relative.parts))

        if child.is_dir():
            rendered.mkdir(parents=True, exist_ok=True)
        elif child.is_file():
            # NB: Read such way to save \n in the end of file
            text = ""
            with open(child, "r", encoding=UTF_8) as f:
                text = "".join(f.readlines())

            content = env.from_string(text).render(params)

            # NB: Fix \n at the end after rendering
            if text.endswith("\n"):
                content += "\n"

            if rendered.exists() and not force:
                print("File {} exists. Aborting.".format(rendered))
                return 1
            rendered.write_text(content, encoding=UTF_8)
        else:
            raise NotImplementedError()

    return 0


def _load_tapa(tapa_file_path: Path) -> Tuple[Optional[Callable], Optional[Callable]]:
    if not tapa_file_path.exists():
        return None, None

    scope = {}
    exec(tapa_file_path.read_text(encoding="utf-8"), scope)

    ask = scope.get(ASK_FUNCTION, None)
    post_init = scope.get(POST_INIT_FUNCTION, None)

    return ask, post_init


def _json_string_to_dict(json_string: Optional[str]) -> dict:
    if json_string is None:
        return {}
    else:
        return json.loads(json_string)


def main():
    app = App(sys.argv[1:])
    sys.exit(app.run())


if __name__ == "__main__":
    main()
