from typing import Any
from enum import Enum, auto, unique


@unique
class PromptMode(Enum):
    USER = auto()
    JSON = auto()
    STRICT_JSON = auto()


class Context:
    def __init__(self, prompt_mode: PromptMode, values: dict):
        self.prompt_mode = prompt_mode
        self.dict = values

    def put(self, key: str, value: str):
        parts = key.split('.')
        cur_dict = self.dict
        for part in parts[:-1]:
            if part not in cur_dict:
                cur_dict[part] = {}
            cur_dict = cur_dict[part]
        cur_dict[parts[-1]] = value

    def get(self, key: str) -> Any:
        parts = key.split('.')
        cur_value = self.dict
        for part in parts:
            if part not in cur_value:
                return None
            cur_value = cur_value[part]
        return cur_value


class ContextHolder:
    CONTEXT = None

    @staticmethod
    def init_context(**kwargs):
        ContextHolder.CONTEXT = Context(**kwargs)

    @staticmethod
    def reset_and_get():
        ctx = ContextHolder.CONTEXT
        ContextHolder.CONTEXT = None
        return ctx
