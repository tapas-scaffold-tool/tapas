import json
from typing import (
    Callable, Optional, TypeVar, Generic, List, Dict, Any
)

from rusty_results import Some, Result

from tapas.io import PromptProvider, PrintProvider
from tapas.parsers import (
    int_parser, str_parser
)

T = TypeVar("T")


class Parameter(Generic[T]):
    def __init__(
        self,
        id: str,
        parser: Callable[[str], Result[T, str]],
        validator: Optional[Callable[[T], Some[str]]] = None,
        prompt: Optional[str] = None,
    ):
        self.id = id
        self.parser = parser
        self.validator = validator
        self.prompt = prompt


class IntParameter(Parameter[int]):
    def __init__(
        self,
        id: str,
        validator: Optional[Callable[[T], Some[str]]] = None,
        prompt: Optional[str] = None,
    ):
        super(IntParameter, self).__init__(id, int_parser, validator, prompt)


class StrParameter(Parameter[str]):
    def __init__(
        self,
        id: str,
        validator: Optional[Callable[[T], Some[str]]] = None,
        prompt: Optional[str] = None,
    ):
        super(StrParameter, self).__init__(id, str_parser, validator, prompt)


class ParamReader:
    def __init__(self, prompt_provider: PromptProvider, print_provider: PrintProvider):
        self.prompt: Callable[[str], str] = prompt_provider.prompt
        self.print: Callable[[str], None] = print_provider.print

    def read_params(self, params: List[Parameter], json_params: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        errors = []

        for param in params:
            json_parts = param.id.split(".")
            json_value = json_params
            for part in json_parts:
                json_value = json_value.get(part)
                if json_value is None:
                    break

            print(json_value)

            if json_value is not None:
                if param.validator:
                    error = param.validator(json_value)
                    if error.is_some:
                        errors.append(error.unwrap())
                        continue
                result[param.id] = json_value
                self.print(f"{param.id} have been read from JSON params: {json_value}")
            elif not errors:
                prompt_message = param.prompt if param.prompt else f"Enter {param.id}: "
                while True:
                    user_input = self.prompt(prompt_message)
                    parse_result = param.parser(user_input)
                    if parse_result.is_err:
                        self.print(f"Failed to parse value {user_input}: {parse_result.unwrap()}")
                        continue
                    if param.validator:
                        validation_error = param.validator(parse_result.unwrap())
                        if validation_error.is_some:
                            self.print(f"Failed to validate value {user_input}: {validation_error.unwrap()}")
                            continue
                    result[param.id] = parse_result.unwrap()
                    break
        return result

    @staticmethod
    def parse_json(json_string: str) -> Dict[str, Any]:
        print(json_string)
        return json.loads(json_string)

