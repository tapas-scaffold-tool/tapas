from typing import Any, List, Callable

from tapas.context import ContextHolder


def prompt(var_name: str, default_value: Any = None, prompt_string: str = None, validators: List[Callable] = None):
    if not validators:
        validators = []

    stored_value = ContextHolder.CONTEXT.get(var_name)
    if stored_value is not None:

        errors = []
        for validator in validators:
            error = validator(stored_value)
            if error is not None:
                errors.append(error)

        if len(errors) != 0:
            print('Value {} is invalid'.format(stored_value))
            for error in errors:
                print(error)
            exit(1)

        return stored_value

    while True:
        value = _user_input(var_name, prompt_string, default_value)

        errors = []
        for validator in validators:
            error = validator(value)
            if error is not None:
                errors.append(error)

        if len(errors) == 0:
            break
        else:
            print('Value {} is invalid'.format(value))
            for error in errors:
                print(error)

    ContextHolder.CONTEXT.put(var_name, value)

    return value


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
