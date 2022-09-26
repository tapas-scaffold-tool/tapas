from rusty_results import Ok, Err, Result


def int_parser(value: str) -> Result[int, str]:
    try:
        return Ok(int(value))
    except ValueError as e:
        return Err(str(e))


def str_parser(value: str) -> Result[str, str]:
    return Ok(value)
