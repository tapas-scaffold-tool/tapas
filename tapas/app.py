from typing import Optional, List, Dict, Any
import os
import sys
import json
import pkg_resources
from inspect import signature
from encodings import utf_8
from pathlib import Path
from argparse import ArgumentParser

from jinja2 import Environment, StrictUndefined
from tabulate import tabulate

from tapas.constants import UTF_8
from tapas.index import (
    find_tapa_in_index,
    load_tapas_index,
    TapaSchema,
    parse_tapa_location,
    parse_index_location,
    DEFAULT_INDEX_LOCATION,
    load_tapa_from_gitthub,
)
from tapas.loader import load_tapa
from tapas.params import (
    Parameter, ParamReader,
)
from tapas.io import PromptProvider, PrintProvider, ConsolePromptProvider, ConsolePrintProvider
from tapas.templater import Templater

TAPA_FILE = "tapa.py"
TEMPLATE_DIR = "template"




def parse_path(path: str) -> Path:
    return Path(path).expanduser().resolve().absolute()


class App:
    def __init__(self, args):
        self.version = self._load_version()
        parser = self._init_parser(self.version)
        parser.parse_args(args, self)

        if not self.list and self.tapa is None:
            parser.error("Missing tapa name")

        self.prompt_provider = ConsolePromptProvider()
        self.print_provider = ConsolePrintProvider()

        self.param_reader = ParamReader(
            self.prompt_provider,
            self.print_provider,
        )
        self.templater = Templater(
            self.print_provider
        )

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
        self.print_provider.print("Hi")
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

        get_params, post_init = load_tapa(tapa_dir / TAPA_FILE)
        params_description = get_params() if get_params else {}
        json_params = self.param_reader.parse_json(self.params) if self.params else {}
        params = self.param_reader.read_params(params_description, json_params)

        self.target.mkdir(parents=True, exist_ok=True)
        code = self.templater.walk(tapa_dir / TEMPLATE_DIR, self.target, params, self.force)
        if code:
            return code

        if post_init is not None:
            cwd = os.getcwd()
            os.chdir(self.target)
            code = post_init(params)
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


def main():
    app = App(sys.argv[1:])
    sys.exit(app.run())


if __name__ == "__main__":
    main()
