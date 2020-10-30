from typing import Tuple, Callable, Optional
import click
import os
import json
import pkg_resources
from inspect import Parameter, signature
from encodings import utf_8
from pathlib import Path

from jinja2 import Environment, StrictUndefined
from gitsnapshot import load_repo
from tabulate import tabulate

from tapas.context import ContextHolder, PromptMode
from tapas.index import CACHE_DIR, _get_tapa_from_index, _load_tapas_index
from tapas.schema import TapaSchema, parse_schema


TAPA_FILE = "tapa.py"
TEMPLATE_DIR = "template"

ASK_FUNCTION = "ask"
POST_INIT_FUNCTION = "post_init"

UTF_8 = utf_8.getregentry().name


def _load_version():
    version = pkg_resources.resource_string("tapas", "tapas.version")
    version = version.decode(UTF_8).strip()
    return version


def _list(ctx, param, value) -> None:
    if not value:
        return

    index = _load_tapas_index()
    table = []
    for tapa_key in sorted(index.keys()):
        table.append([tapa_key, index[tapa_key].description])

    print(tabulate(table, headers=["Tapa name", "Description"]))

    ctx.exit()


@click.command()
@click.version_option(version=_load_version(), message="%(version)s")
@click.option(
    "--list", "-l", is_flag=True, default=False, help="Show list of available tapas", callback=_list, is_eager=True
)
@click.option("--params", "-p", type=str, default=None, help="Parameters json", metavar="<json>")
@click.option("--force", "-f", is_flag=True, default=False, help="Rewrite files in target directory")
@click.argument("tapa", type=str)
@click.argument("target", type=str, default=".")
def main(tapa, target, params, force, list) -> int:
    schema, name = parse_schema(tapa)

    if schema is TapaSchema.INDEX:
        schema, name = _get_tapa_from_index(name)

    if name is None:
        print('Unknown tapa "{}"'.format(tapa))
        return 1

    if schema is TapaSchema.DIRECTORY:
        tapa_dir = _get_path(name)
    elif schema is TapaSchema.GITHUB:
        tapa_dir = _resolve_tapa_dir_from_github(name)
    else:
        raise NotImplementedError("Not implemented for {}".format(schema))

    if tapa_dir is None:
        print("Unknown tapa name {}".format(tapa))
        return 1

    target_dir = _get_path(target)

    ask, post_init = _load_tapa(tapa_dir / TAPA_FILE)

    ContextHolder.init_context(prompt_mode=PromptMode.USER, values=_json_string_to_dict(params))

    if ask is not None:
        ask()

    params = ContextHolder.CONTEXT.dict

    code = _walk(tapa_dir / TEMPLATE_DIR, target_dir, params, force)
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
        os.chdir(target_dir)
        code = post_init(**post_init_params)
        os.chdir(cwd)

    if code is None:
        code = 0
    return code


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


def _get_path(path: str) -> Path:
    return Path(path).expanduser().resolve().absolute()


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


def _resolve_tapa_dir_from_github(repo_name: str) -> Optional[Path]:
    repo = "https://github.com/" + repo_name
    parts = repo_name.split("/")
    repo_dir = (CACHE_DIR / "repos-github").joinpath(*parts)
    load_repo(repo_dir, repo, use_existing=True)
    return repo_dir


if __name__ == "__main__":
    main()
