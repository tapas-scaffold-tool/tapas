from tapas.tools.tapas_integration_tests import communicate

from integration_tests.common import (
    BaseTapasTest,
    get_test_tapas_dir,
)


class TapasHelpTest(BaseTapasTest):
    def test_show_help(self):
        index_dir = get_test_tapas_dir() / "custom_index"

        code, out, err = communicate(
            ["tapas", "--index", f"dir:{index_dir}", "--list"],
        )

        self.assertEqual(0, code, "Exit code is not zero")
        self.assertEqual(0, len(err), "Errors occurred")

        out = out.splitlines()  # Make Unix and Windows lines uniform

        self.assertListEqual(
            out,
            [
                "Tapa name    Description",
                "-----------  -------------",
                "test-tapa    Test tapa",
            ],
        )
