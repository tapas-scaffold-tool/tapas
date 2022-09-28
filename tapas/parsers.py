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
