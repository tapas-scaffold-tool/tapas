from typing import Callable, List

from rusty_results import Ok, Err, Result


def int_parser(value: str) -> Result[int, str]:
    try:
        return Ok(int(value))
    except ValueError as e:
        return Err(str(e))


def str_parser(value: str) -> Result[str, str]:
    return Ok(value)


TRUE_VALUES = {
    "true",
    "yes",
    "y",
}
FALSE_VALUES = {
    "false",
    "no",
    "n",
}
BOOL_VALUES = list(sorted(TRUE_VALUES) + sorted(FALSE_VALUES))


def bool_parser(value: str) -> Result[bool, str]:
    value = value.strip().lower()
    if value in TRUE_VALUES:
        return Ok(True)
    elif value in FALSE_VALUES:
        return Ok(False)
    else:
        return Err(f"Illegal boolean value {value}. Allowed values are: [{', '.join(BOOL_VALUES)}]")


def build_str_enum_parser(values: List[str]) -> Callable[[str], Result[str, str]]:
    values_lower = {v.lower() for v in values}

    def str_enum_parser(value: str) -> Result[str, str]:
        if value.lower() in values_lower:
            return Ok(value.lower())
        else:
            return Err(f"Unknown value {value}, allowed values are [{' ,'.join(sorted(values_lower))}]")

    return str_enum_parser
