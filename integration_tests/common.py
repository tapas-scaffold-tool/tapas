import sys
from encodings import utf_8
from pathlib import Path
from shutil import rmtree
from subprocess import Popen, PIPE, TimeoutExpired, run
from tempfile import mkdtemp
from typing import Any
from unittest import TestCase


def communicate(*args, input=None, timeout=60):
    print(f"Run command: {' '.join(*args)}")
    proc = Popen(*args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        outs, errs = proc.communicate(input=input, timeout=timeout)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    code = proc.poll()
    stdout = outs.decode(get_encoding(sys.stdout))
    stderr = errs.decode(get_encoding(sys.stderr))

    if len(stdout) != 0:
        print(stdout)
    if len(stderr) != 0:
        print(stderr, file=sys.stderr)

    return code, stdout, stderr


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


def get_test_tapas_dir() -> Path:
    return project_root() / "test_tapas"


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


class BaseTapasTest(TestCase):
    @classmethod
    def setUpClass(cls):
        run(["pip", "install", "."], cwd=project_root(), check=True)

    @classmethod
    def tearDownClass(cls):
        run(["pip", "uninstall", "tapas"], cwd=project_root(), check=True)
