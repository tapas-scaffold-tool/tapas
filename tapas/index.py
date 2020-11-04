import re
from enum import Enum
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

import yaml
from appdirs import user_cache_dir
from gitsnapshot import load_repo

CACHE_DIR = Path(user_cache_dir("tapas"))
INDEX_FILE = "index.yml"


class TapaSchema(Enum):
    INDEX = 1
    DIRECTORY = 2
    DIR = 2
    GITHUB = 3
    GH = 3


@dataclass
class TapaLocation:
    schema: TapaSchema
    location: str


TAPA_LOCATION_PATTERN = "^(" + "|".join(map(str.lower, TapaSchema.__members__.keys())) + "):.+$"


def parse_tapa_location(value: str) -> TapaLocation:
    if re.match(TAPA_LOCATION_PATTERN, value):
        schema, location = tuple(value.split(":", maxsplit=1))
        schema = TapaSchema[schema.upper()]
        return TapaLocation(schema, location)
    else:
        return TapaLocation(TapaSchema.INDEX, value)


@dataclass
class TapaRecord:
    location: TapaLocation
    description: Optional[str]


class IndexSchema(Enum):
    DIRECTORY = 1
    DIR = 1
    GITHUB = 2
    GH = 2


@dataclass
class IndexLocation:
    schema: IndexSchema
    location: str


DEFAULT_INDEX_LOCATION = IndexLocation(IndexSchema.GITHUB, "tapas-scaffold-tool/tapas-index")

INDEX_SCHEMA_PATTERN = "^(" + "|".join(map(str.lower, IndexSchema.__members__.keys())) + "):.+$"


def parse_index_location(value: str) -> IndexLocation:
    if re.match(INDEX_SCHEMA_PATTERN, value):
        schema, location = tuple(value.split(":", maxsplit=1))
        schema = IndexSchema[schema.upper()]
        return IndexLocation(schema, location)
    else:
        raise ValueError(f"Illegal value {value}")


def load_tapas_index(location: IndexLocation) -> Dict[str, TapaRecord]:
    if location.schema is IndexSchema.DIRECTORY:
        index_dir = Path(location.location).expanduser().resolve()
    elif location.schema is IndexSchema.GITHUB:
        index_dir = CACHE_DIR / location.location
        load_repo(index_dir, f"https://github.com/{location.location}", use_existing=True)
    else:
        raise NotImplementedError(f"Not implemented for schema {location.schema}")

    index_file = index_dir / INDEX_FILE
    index_dict = yaml.load(index_file.read_bytes(), Loader=yaml.BaseLoader)
    result = {}
    for name, record_dict in index_dict.items():
        location = parse_tapa_location(record_dict["repository"])
        if location.schema is TapaSchema.INDEX:
            raise Exception(f"Error for tapa {name}. Index schema is not allowed in index.")
        description = record_dict.get("description")
        result[name] = TapaRecord(location=location, description=description)
    return result


def find_tapa_in_index(index_location: IndexLocation, tapa_name: str) -> Optional[Path]:
    index = load_tapas_index(index_location)
    record = index.get(tapa_name)
    if record:
        if record.location.schema is TapaSchema.DIRECTORY:
            return Path(record.location.location).resolve()
        elif record.location.schema is TapaSchema.GITHUB:
            return load_tapa_from_gitthub(record.location.location)
        else:
            raise NotImplementedError(f"Not implemented for schema {record.location.schema}")
    else:
        return None


def load_tapa_from_gitthub(github_location: str) -> Path:
    tapa_dir = CACHE_DIR / github_location
    load_repo(tapa_dir, f"https://github.com/{github_location}", use_existing=True)
    return tapa_dir
