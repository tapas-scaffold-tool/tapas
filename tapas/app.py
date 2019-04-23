from typing import Tuple, Callable, Optional
import click
import os
import json
from encodings import utf_8
from pathlib import Path
from jinja2 import Environment, StrictUndefined

from tapas.context import ContextHolder, PromptMode


TAPA_FILE = 'tapa.py'
TEMPLATE_DIR = 'template'

ASK_FUNCTION = 'ask'
POST_INIT_FUNCTION = 'post_init'

UTF_8 = utf_8.getregentry().name


@click.command()
@click.option('--target', '-t', default=None, help='Target directory')
@click.option('--params', '-p', type=str, default=None, help='Parameters json')
@click.argument('tapa')
def main(tapa, target, params):
    if target is None:
        target = os.getcwd()

    tapa_dir = _get_path(tapa)
    target_dir = Path(target)

    ask, post_init = _load_tapa(tapa_dir.joinpath(TAPA_FILE))

    ContextHolder.init_context(prompt_mode=PromptMode.USER, values=_json_string_to_dict(params))

    if ask is not None:
        ask()

    params = ContextHolder.CONTEXT.dict

    code = _walk(tapa_dir.joinpath(TEMPLATE_DIR), target_dir, params)
    if code:
        return code

    if post_init is not None:
        cwd = os.getcwd()
        os.chdir(target)
        code = post_init()
        os.chdir(cwd)

    if code is None:
        code = 0
    return code


def _walk(template_dir: Path, destination_dir: Path, params: dict) -> int:
    env = Environment(undefined=StrictUndefined)

    for child in template_dir.glob('**/*'):
        relative = child.relative_to(template_dir)

        rendered = destination_dir / Path(*map(lambda p: env.from_string(p).render(params), relative.parts))

        if child.is_dir():
            rendered.mkdir(parents=True, exist_ok=True)
        elif child.is_file():
            content = env.from_string(child.read_text(encoding=UTF_8)).render(params)
            rendered.write_text(content, encoding=UTF_8)
        else:
            raise NotImplementedError()

    return 0


def _get_path(path: str) -> Path:
    return Path(path).resolve().expanduser().absolute()


def _load_tapa(tapa_file_path: Path) -> Tuple[Callable, Callable]:
    scope = {}
    exec(tapa_file_path.read_text(encoding='utf-8'), scope)

    ask = scope.get(ASK_FUNCTION, None)
    post_init = scope.get(POST_INIT_FUNCTION, None)

    return ask, post_init


def _json_string_to_dict(json_string: Optional[str]) -> dict:
    if json_string is None:
        return {}
    else:
        return json.loads(json_string)


if __name__ == '__main__':
    main()
