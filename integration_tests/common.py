from pathlib import Path
from shutil import rmtree
from subprocess import run
from tempfile import mkdtemp
from unittest import TestCase


def project_root() -> Path:
    return Path(__file__).parents[1].resolve().absolute()


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
        run(["pip", "install", "-e", "."], cwd=project_root(), check=True)
