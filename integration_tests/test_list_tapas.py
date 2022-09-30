from integration_tests.common import (
    BaseTapasTest,
    communicate,
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

        self.assertEqual(
            out,
            "Tapa name    Description\n" + "-----------  -------------\n" + "test-tapa    Test tapa\n",
        )
