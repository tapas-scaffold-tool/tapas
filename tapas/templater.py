from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, StrictUndefined

from tapas.constants import UTF_8
from tapas.io import PrintProvider


class Templater:
    def __init__(self, print_provider: PrintProvider):
        self.print = print_provider.print

    def walk(self, template_dir: Path, destination_dir: Path, params: Dict[str, Any], force: bool) -> int:
        params = self._expand_keys(params)
        print(params)
        if not template_dir.exists():
            self.print(f'Incorrect tapa. Template dir "{template_dir}" not found.')
            return 1

        env = Environment(undefined=StrictUndefined)

        for child in template_dir.glob("**/*"):
            relative = child.relative_to(template_dir)

            rendered = destination_dir / Path(*map(lambda p: env.from_string(p).render(params), relative.parts))

            if child.is_dir():
                rendered.mkdir(parents=True, exist_ok=True)
            elif child.is_file():
                # NB: Read such way to save \n in the end of file
                text = ""
                with open(child, "r", encoding=UTF_8) as f:
                    text = "".join(f.readlines())

                content = env.from_string(text).render(params)

                # NB: Fix \n at the end after rendering
                if text.endswith("\n"):
                    content += "\n"

                if rendered.exists() and not force:
                    self.print("File {} exists. Aborting.".format(rendered))
                    return 1
                rendered.write_text(content, encoding=UTF_8)
            else:
                raise NotImplementedError()

        return 0

    @staticmethod
    def _expand_keys(values: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for key, value in values.items():
            parts = key.split(".")
            final = parts[-1]
            parts = parts[:-1]
            cursor = result
            for part in parts:
                if part not in cursor:
                    cursor[part] = {}
                cursor = cursor[part]
            cursor[final] = value
        return result
