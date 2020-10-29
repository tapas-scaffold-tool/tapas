from pathlib import Path
from typing import Tuple, Optional, Dict
from dataclasses import dataclass

import yaml
from appdirs import user_cache_dir
from gitsnapshot import load_repo

from tapas.schema import TapaSchema, parse_schema


CACHE_DIR = Path(user_cache_dir("tapas"))
INDEX_REPOSITORY = "https://github.com/tapas-scaffold-tool/tapas-index"
INDEX_FILE = "index.yml"


@dataclass
class TapaRecord:
    repository: str
    description: Optional[str]


def _get_tapa_from_index(name: str) -> Tuple[Optional[TapaSchema], Optional[str]]:
    index = _load_tapas_index()
    record = index.get(name)
    if record:
        return parse_schema(record.repository)
    else:
        return None, None


def _load_tapas_index() -> Dict[str, TapaRecord]:
    index_dir = CACHE_DIR / "index"
    index_file = index_dir / INDEX_FILE

    load_repo(index_dir, INDEX_REPOSITORY, use_existing=True)
    index_dict = yaml.load(index_file.read_bytes(), Loader=yaml.BaseLoader)
    result = {}
    for name, record_dict in index_dict.items():
        result[name] = TapaRecord(**record_dict)
    return result
