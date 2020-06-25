import sys
from typing import Any, List, Callable, Tuple, Optional
from pathlib import Path
from subprocess import run, PIPE
from lice.core import LICENSES

import requests
from git import Repo

from tapas.context import ContextHolder


def prompt(
        var_name: str,
        converter: Callable[[str], Tuple[Optional[Any], Optional[str]]],
        default_value: Any = None,
        prompt_string: str = None,
        validators: List[Callable] = None
):
    if not validators:
        validators = []

    stored_value = ContextHolder.CONTEXT.get(var_name)
    if stored_value is not None:
        errors = []

        value, error = converter(stored_value)

        if not error:
            for validator in validators:
                error = validator(value)
                if error is not None:
                    errors.append(error)
        else:
            errors.append(error)

        if len(errors) != 0:
            print('Value {} is invalid'.format(stored_value))
            for error in errors:
                print(error)
            exit(1)

        return stored_value

    while True:
        errors = []
        value = _user_input(var_name, prompt_string, default_value)
        value, error = converter(value)

        if not error:
            for validator in validators:
                error = validator(value)
                if error is not None:
                    errors.append(error)
        else:
            errors.append(error)

        if len(errors) == 0:
            break
        else:
            print('Value {} is invalid'.format(value))
            for error in errors:
                print(error)

    ContextHolder.CONTEXT.put(var_name, value)

    return value


def prompt_str(var_name: str, default_value: Any = None, prompt_string: str = None, validators: List[Callable] = None):
    def string_converter(value: str) -> Tuple[Optional[str], Optional[str]]:
        return value, None

    return prompt(var_name, string_converter, default_value, prompt_string, validators)


def prompt_int(var_name: str, default_value: Any = None, prompt_string: str = None, validators: List[Callable] = None):
    def int_converter(value: str) -> Tuple[Optional[int], Optional[str]]:
        try:
            return int(value), None
        except ValueError as e:
            return None, str(e)


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

BOOL_VALUES = TRUE_VALUES.union(FALSE_VALUES)


def prompt_bool(var_name: str, default_value: Any = None, prompt_string: str = None):
    def bool_converter(value: str) -> Tuple[Optional[bool], Optional[str]]:
        value = (value or "").strip().lower()
        if value in TRUE_VALUES:
            return True, None
        elif value in FALSE_VALUES:
            return False, None
        else:
            return None, f"Illegal boolean value {value}. Allowed values are: [{', '.join(BOOL_VALUES)}]"

    return prompt(var_name, bool_converter, default_value, prompt_string)


def prompt_enum(var_name: str, default_value: str = None, prompt_string: str = None, values: List[str] = None):
    validators = []
    if values is not None:
        def validator(x: str):
            if (x or "").lower() in values:
                return None
            else:
                return f'Unknown value "{x}"'

        validators.append(validator)

    if prompt_string is None:
        allowed = ' | '.join(values)
        if default_value:
            prompt_string = f'Enter {var_name}, allowed values are ({allowed})? [{default_value}]: '
        else:
            prompt_string = f'Enter {var_name}, allowed values are ({allowed}): '

    return prompt_str(var_name, default_value, prompt_string, validators)


def prompt_license():
    values = LICENSES + ['none']
    allowed = ' | '.join(LICENSES)
    return prompt_enum('license', 'none', f'Add license ({allowed})? [none]: ', values)


def _user_input(var_name: str, prompt_string: str, default_value: Any):
    if not prompt_string:
        if default_value is not None:
            prompt_string = 'Enter {} value [{}]: '.format(var_name, default_value)
        else:
            prompt_string = 'Enter {} value: '.format(var_name)

    result = input(prompt_string)
    if len(result) == 0:
        result = default_value
    return result


def download_file(src: str, dst: str):
    resp = requests.get(src)
    with open(dst, 'w') as f:
        f.write(resp.text)


def init_git_repo(commit_message: str = "Initial commit"):
    if not Path('.git').exists():
        repo = Repo.init()
    else:
        repo = Repo('.')
    repo.index.add('*')
    repo.index.add('.gitignore')
    repo.index.commit(commit_message)


def generate_license_text(license_type: str):
    if license_type not in LICENSES:
        raise ValueError(f'Unknown license type "{license_type}"')

    proc = run(['lice', license_type], stdout=PIPE, check=True)
    return proc.stdout.decode(sys.stdout.encoding)


def generate_license_file(licence_type: str, file: str = 'LICENSE'):
    if licence_type.lower() == 'none':
        return

    with open(file, 'w') as f:
        f.write(generate_license_text(licence_type))
