from pathlib import Path

from tapas.tools.tapas_integration_tests import (
    communicate,
    pass_to_process,
)

from integration_tests.common import (
    get_test_tapas_dir,
    TempDirectory,
    BaseTapasTest,
)


class GenerateTapasTest(BaseTapasTest):
    def test_dir_file_value(self):
        tapa = get_test_tapas_dir() / "dir_file_value"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target],
                input=pass_to_process("directory name", "file name", "value"),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            directory = target / "directory name"
            file = directory / "file name.txt"

            self.assertTrue(directory.exists(), "Directory was not created")
            self.assertTrue(directory.is_dir(), "Directory is not directory")

            self.assertTrue(file.exists(), "File was not created")
            self.assertTrue(file.is_file(), "File is not file")

            self.assertEqual("value\n", file.read_text(), "File content mismatch")

    def test_post_init_script(self):
        tapa = get_test_tapas_dir() / "post_init_script"

        with TempDirectory() as target:
            code, out, err = communicate(["tapas", "dir:{}".format(str(tapa)), target])

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            static_file = target / "static-file.txt"
            generated_file = target / "generated-file.txt"

            self.assertEqual("Static text.\n", static_file.read_text(), "File content mismatch")
            self.assertEqual("Generated text.\n", generated_file.read_text(), "File content mismatch")

    def test_params(self):
        tapa = get_test_tapas_dir() / "params"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target, "-p", '{"a": {"b": 1, "c": "Test string!"}}']
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            file = target / "file.txt"

            self.assertEqual("1\nTest string!\n", file.read_text(), "File content mismatch")

    def test_params_partial(self):
        tapa = get_test_tapas_dir() / "params"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target, "-p", '{"a": {"b": 1}}'],
                input=pass_to_process("Test string!"),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            file = target / "file.txt"

            self.assertEqual("1\nTest string!\n", file.read_text(), "File content mismatch")

    def test_post_init_script_with_parameters(self):
        tapa = get_test_tapas_dir() / "post_init_script_with_parameters"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target, "-p", '{"param": "param value"}'],
                input=pass_to_process("Test string!"),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            file = target / "generated-file.txt"

            self.assertEqual("p=param value\n", file.read_text(), "File content mismatch")

    def test_custom_index_file(self):
        index_dir = get_test_tapas_dir() / "custom_index"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "--index", f"dir:{index_dir}", "test-tapa", target],
                input=pass_to_process("directory name", "file name", "value"),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            directory = target / "directory name"
            file = directory / "file name.txt"

            self.assertTrue(directory.exists(), "Directory was not created")
            self.assertTrue(directory.is_dir(), "Directory is not directory")

            self.assertTrue(file.exists(), "File was not created")
            self.assertTrue(file.is_file(), "File is not file")

            self.assertEqual("value\n", file.read_text(), "File content mismatch")

    def test_default_value(self):
        tapa = get_test_tapas_dir() / "params_with_default_value"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target],
                input=pass_to_process(""),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            file = target / "file.txt"

            self.assertTrue(file.exists(), "File was not created")
            self.assertTrue(file.is_file(), "File is not file")

            self.assertEqual("default\n", file.read_text(), "File content mismatch")

    def test_parse_and_validation_error(self):
        tapa = get_test_tapas_dir() / "params_with_parser_and_validator"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target],
                input=pass_to_process("abc", "-1", "1"),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            file = target / "file.txt"

            self.assertTrue(file.exists(), "File was not created")
            self.assertTrue(file.is_file(), "File is not file")

            self.assertEqual("1\n", file.read_text(), "File content mismatch")

    def test_generate_license(self):
        tapa = get_test_tapas_dir() / "license"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target],
                input=pass_to_process("mit"),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            license_file = target / "LICENSE"

            self.assertTrue(license_file.exists(), "File was not created")
            self.assertTrue(license_file.is_file(), "File is not file")

            self.assertTrue(license_file.read_text().find("MIT License") != -1, "File content mismatch")

    def test_do_not_generate_license_by_default(self):
        tapa = get_test_tapas_dir() / "license"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target],
                input=pass_to_process(""),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            license_file = target / "LICENSE"

            self.assertFalse(license_file.exists(), "License file should not be created")

    def test_init_git_by_default(self):
        tapa = get_test_tapas_dir() / "git"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target],
                input=pass_to_process(""),
            )

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            git_dir = target / ".git"

            self.assertTrue(git_dir.exists(), "Git directory was not created")
            self.assertTrue(git_dir.is_dir(), "Git directory is not directory")
