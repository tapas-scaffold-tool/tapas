import re
from enum import Enum
from typing import Tuple


class TapaSchema(Enum):
    INDEX = 1
    DIRECTORY = 2
    DIR = 2
    GITHUB = 3
    GH = 3


SCHEMA_PATTERN = '^(' + '|'.join(map(str.lower, TapaSchema.__members__.keys())) + '):.+$'


def parse_schema(value: str) -> Tuple[TapaSchema, str]:
    if re.match(SCHEMA_PATTERN, value):
        schema, name = tuple(value.split(':', maxsplit=1))
        schema = TapaSchema[schema.upper()]
        return schema, name
    else:
        return TapaSchema.INDEX, value
