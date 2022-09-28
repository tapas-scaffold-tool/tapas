from unittest import TestCase

from tapas.params import ParamReader, StrParameter
from tests.utils import (
    ListPromptProvider,
    SaveToListPrintProvider,
)


class TestParamReader(TestCase):
    def test_read_params_from_prompt(self):
        prompt = ListPromptProvider([
            "test_value",
        ])
        print = SaveToListPrintProvider()
        param_reader = ParamReader(prompt, print)

        result = param_reader.read_params(
            [StrParameter("test.id")],
            {},
        )

        prompt.check_no_more_values()
        self.assertDictEqual(result, {"test.id": "test_value"})

    def test_read_params_from_json_dict(self):
        prompt = ListPromptProvider([])
        print = SaveToListPrintProvider()
        param_reader = ParamReader(prompt, print)

        result = param_reader.read_params(
            [StrParameter("test.id")],
            {"test": {"id": "test_value"}},
        )

        prompt.check_no_more_values()
        self.assertDictEqual(result, {"test.id": "test_value"})

    def test_read_params_default_value(self):
        prompt = ListPromptProvider([""])
        print = SaveToListPrintProvider()
        param_reader = ParamReader(prompt, print)

        result = param_reader.read_params(
            [StrParameter("test.id", default="default")],
            {},
        )

        prompt.check_no_more_values()
        self.assertDictEqual(result, {"test.id": "default"})
