from typing import List

from tapas.io import (
    PromptProvider,
    PrintProvider,
)


class ListPromptProvider(PromptProvider):
    def __init__(self, values: List[str]):
        self.values = values
        self.next = 0

    def prompt(self, message: str) -> str:
        if self.next < len(self.values):
            value = self.values[self.next]
            self.next += 1
            return value
        else:
            raise AssertionError(f"No more values in prompt")

    def check_no_more_values(self):
        diff = len(self.values) - self.next
        if diff:
            raise AssertionError(f"Expected 0 values left but extra {diff} values found")


class SaveToListPrintProvider(PrintProvider):
    def __init__(self):
        self.values = []

    def print(self, message: str) -> None:
        self.values.append(message)

    def get_values(self) -> List[str]:
        return self.values
