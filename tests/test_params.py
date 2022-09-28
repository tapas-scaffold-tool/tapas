from unittest import TestCase

from tapas.params import ParamReader, StrParameter, StrEnumParameter
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

    def test_read_str_enum_param_ok(self):
        prompt = ListPromptProvider(["value_1"])
        print = SaveToListPrintProvider()
        param_reader = ParamReader(prompt, print)

        result = param_reader.read_params(
            [StrEnumParameter("test.id", values=["VaLuE_1", "vAlUe_2"])],
            {},
        )

        prompt.check_no_more_values()
        self.assertDictEqual(result, {"test.id": "value_1"})

    def test_read_str_enum_param_err(self):
        prompt = ListPromptProvider(["bad_value", "good_value"])
        print = SaveToListPrintProvider()
        param_reader = ParamReader(prompt, print)

        result = param_reader.read_params(
            [StrEnumParameter("test.id", values=["good_value", "another_value"])],
            {},
        )

        prompt.check_no_more_values()
        self.assertDictEqual(result, {"test.id": "good_value"})
        self.assertListEqual(
            print.get_values(),
            ["Failed to parse value bad_value: Unknown value bad_value, allowed values are [another_value ,good_value]"],
        )
