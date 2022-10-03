from unittest import TestCase

from parameterized import parameterized
from rusty_results import Ok, Err

from tapas.parsers import int_parser, bool_parser


class TestIntParser(TestCase):
    def test_parse_ok(self):
        self.assertEqual(Ok(123), int_parser("123"))

    def test_parse_failed(self):
        self.assertEqual(Err("invalid literal for int() with base 10: 'abc'"), int_parser("abc"))


class TestBoolParser(TestCase):
    @parameterized.expand(
        [
            ("TruE", True),
            ("yes", True),
            ("Y", True),
            ("falsE", False),
            ("No", False),
            ("n", False),
        ],
        name_func=lambda _0, _1, params: f"test_parse_{str(params[0][0]).lower()}_as_{str(params[0][1]).lower()}",
    )
    def test_parse_bool_value(self, value, expected):
        self.assertEqual(Ok(expected), bool_parser(value))

    def test_parse_failed(self):
        self.assertEqual(
            Err("Illegal boolean value badvalue. Allowed values are: [true, y, yes, false, n, no]"),
            bool_parser("badvalue")
        )
