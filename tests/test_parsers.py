from unittest import TestCase

from rusty_results import Ok, Err

from tapas.parsers import int_parser


class TestIntParser(TestCase):
    def test_parse_ok(self):
        self.assertEqual(Ok(123), int_parser("123"))

    def test_parse_failed(self):
        self.assertEqual(Err("invalid literal for int() with base 10: 'abc'"), int_parser("abc"))
