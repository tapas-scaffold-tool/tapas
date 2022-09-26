from typing import Any
import sys
from unittest import TestCase
from tempfile import mkdtemp
from shutil import rmtree
from subprocess import Popen, TimeoutExpired, PIPE, run
from pathlib import Path
from encodings import utf_8


def communicate(*args, input=None, timeout=60):
    proc = Popen(*args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        outs, errs = proc.communicate(input=input, timeout=timeout)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    code = proc.poll()

    return code, outs.decode(get_encoding(sys.stdout)), errs.decode(get_encoding(sys.stderr))


def get_encoding(arg: Any):
    if arg.encoding is not None:
        return arg.encoding
    else:
        return utf_8.getregentry().name


def pass_to_process(*args) -> bytes:
    input_string = "\n".join(args) + "\n"
    return input_string.encode(get_encoding(sys.stdin))


def project_root() -> Path:
    return Path(__file__).parents[1]


def test_tapas_dir() -> Path:
    return project_root() / "test_tapas"


class MainTest(TestCase):
    @classmethod
    def setUpClass(cls):
        run(["pip", "install", "."], cwd=project_root(), check=True)

    @classmethod
    def tearDownClass(cls):
        run(["pip", "uninstall", "tapas"], cwd=project_root(), check=True)

    def test_dir_file_value(self):
        tapa = test_tapas_dir() / "dir_file_value"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target],
                input=pass_to_process("directory name", "file name", "value"),
            )

            if len(err) != 0:
                print(err)

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
        tapa = test_tapas_dir() / "post_init_script"

        with TempDirectory() as target:
            code, out, err = communicate(["tapas", "dir:{}".format(str(tapa)), target])

            if len(err) != 0:
                print(err)

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            static_file = target / "static-file.txt"
            generated_file = target / "generated-file.txt"

            self.assertEqual("Static text.\n", static_file.read_text(), "File content mismatch")
            self.assertEqual("Generated text.\n", generated_file.read_text(), "File content mismatch")

    def test_params(self):
        tapa = test_tapas_dir() / "params"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target, "-p", '{"a": {"b": 1, "c": "Test string!"}}']
            )

            if len(err) != 0:
                print(err)

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            file = target / "file.txt"

            self.assertEqual("1\nTest string!\n", file.read_text(), "File content mismatch")

    def test_params_partial(self):
        tapa = test_tapas_dir() / "params"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target, "-p", '{"a": {"b": 1}}'],
                input=pass_to_process("Test string!"),
            )

            if len(err) != 0:
                print(err)

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            file = target / "file.txt"

            self.assertEqual("1\nTest string!\n", file.read_text(), "File content mismatch")

    def test_post_init_script_with_parameters(self):
        tapa = test_tapas_dir() / "post_init_script_with_parameters"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "dir:{}".format(str(tapa)), target, "-p", '{"param": "param value", "dict_param": {"a": 1}}'],
                input=pass_to_process("Test string!"),
            )

            if len(err) != 0:
                print(err)

            self.assertEqual(0, code, "Exit code is not zero")
            self.assertEqual(0, len(err), "Errors occurred")

            target = Path(target)
            file = target / "generated-file.txt"

            self.assertEqual("p=param value,dp.a=1,def=123\n", file.read_text(), "File content mismatch")

    def test_custom_index_file(self):
        index_dir = test_tapas_dir() / "custom_index"

        with TempDirectory() as target:
            code, out, err = communicate(
                ["tapas", "--index", f"dir:{index_dir}", "test-tapa", target],
                input=pass_to_process("directory name", "file name", "value"),
            )

            if len(err) != 0:
                print(err)

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


class TempDirectory:
    def __init__(self, clean=True):
        self.dir = None
        self.clean = clean

    def __enter__(self):
        self.dir = mkdtemp()
        return self.dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.clean:
            rmtree(self.dir, ignore_errors=True)
