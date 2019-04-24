from typing import Tuple, Callable, Optional, Dict
import click
import os
import json
import yaml
from encodings import utf_8
from pathlib import Path
from jinja2 import Environment, StrictUndefined
from gitsnapshot import load_repo
from appdirs import user_cache_dir

from tapas.context import ContextHolder, PromptMode


TAPA_FILE = 'tapa.py'
TEMPLATE_DIR = 'template'

ASK_FUNCTION = 'ask'
POST_INIT_FUNCTION = 'post_init'

CACHE_DIR = Path(user_cache_dir('tapas'))

INDEX_REPOSITORY = 'https://github.com/tapas-scaffold-tool/tapas-index'
INDEX_FILE = 'index.yml'

UTF_8 = utf_8.getregentry().name


@click.command()
@click.option('--target', '-t', default=None, help='Target directory')
@click.option('--params', '-p', type=str, default=None, help='Parameters json')
@click.argument('tapa')
def main(tapa, target, params):
    if target is None:
        target = os.getcwd()

    tapa_dir = _get_tapa_dir(tapa)
    if tapa_dir is None:
        print('Unknown tapa name {}'.format(tapa))
        return 1

    target_dir = Path(target)

    ask, post_init = _load_tapa(tapa_dir / TAPA_FILE)

    ContextHolder.init_context(prompt_mode=PromptMode.USER, values=_json_string_to_dict(params))

    if ask is not None:
        ask()

    params = ContextHolder.CONTEXT.dict

    code = _walk(tapa_dir / TEMPLATE_DIR, target_dir, params)
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
    if not template_dir.exists():
        return 1

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


def _load_tapa(tapa_file_path: Path) -> Tuple[Optional[Callable], Optional[Callable]]:
    if not tapa_file_path.exists():
        return None, None

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


def _get_tapa_dir(tapa_name: str) -> Optional[Path]:
    repo = _get_tapa_repo_by_name(tapa_name)
    if repo is not None:
        repo_dir = CACHE_DIR / 'repos' / tapa_name
        load_repo(repo_dir, repo, use_existing=True)
        return repo_dir


def _get_tapa_repo_by_name(tapa_name: str) -> Optional[str]:
    index = _load_tapas_index()
    return index.get(tapa_name)


def _load_tapas_index() -> Dict[str, str]:
    index_dir = CACHE_DIR / 'index'
    index_file = index_dir / INDEX_FILE

    load_repo(index_dir, INDEX_REPOSITORY, use_existing=True)
    return yaml.load(index_file.read_bytes(), Loader=yaml.BaseLoader)


if __name__ == '__main__':
    main()
