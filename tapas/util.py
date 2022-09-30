import os
from pathlib import Path


class DirectoryContext:
    def __init__(self, path: Path):
        self.path = path
        self.cwd = None

    def __enter__(self):
        self.cwd = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cwd)
