class PromptProvider:
    def prompt(self, message: str) -> str:
        raise NotImplementedError()


class ConsolePromptProvider(PromptProvider):
    def prompt(self, message: str) -> str:
        return input(message)


class PrintProvider:
    def print(self, message: str) -> None:
        raise NotImplementedError()


class ConsolePrintProvider(PrintProvider):
    def print(self, message: str) -> None:
        print(message)
