from tapas.tools.tapas_integration_tests import communicate

from integration_tests.common import (
    BaseTapasTest,
)


class TapasHelpTest(BaseTapasTest):
    def test_show_help(self):
        code, out, err = communicate(
            ["tapas", "--help"],
        )

        self.assertEqual(0, code, "Exit code is not zero")
        self.assertEqual(0, len(err), "Errors occurred")

        self.assertTrue(out.startswith("usage: tapas"))
