from pathlib import Path

from git import Repo

from tapas.params import BoolParameter
from tapas.tools.common import get_system_param


INIT_GIT_PARAMETER_ID = get_system_param("git")


def init_git_repo(commit_message: str = "Initial commit", dot_files=None):
    if dot_files is None:
        dot_files = [
            ".gitignore",
        ]

    if not Path(".git").exists():
        repo = Repo.init()
    else:
        repo = Repo(".")
    repo.index.add("*")
    for dot_file in dot_files:
        if Path(dot_file).exists():
            repo.index.add(dot_file)
    repo.index.commit(commit_message)


class InitGitParameter(BoolParameter):
    def __init__(self):
        super(InitGitParameter, self).__init__(
            INIT_GIT_PARAMETER_ID,
            prompt="Init git repo",
            default=True,
        )


TAPAS_SYSTEM_INIT_GIT_PARAMETER = InitGitParameter()
