import sys
from typing import Any, List, Callable, Tuple, Optional
from pathlib import Path
from subprocess import run, PIPE
from lice.core import LICENSES

import requests
from git import Repo





def prompt_enum(var_name: str, default_value: str = None, prompt_string: str = None, values: List[str] = None):
    validators = []
    if values is not None:

        def validator(x: str):
            if (x or "").lower() in values:
                return None
            else:
                return f'Unknown value "{x}"'

        validators.append(validator)

    if prompt_string is None:
        allowed = " | ".join(values)
        if default_value:
            prompt_string = f"Enter {var_name}, allowed values are ({allowed})? [{default_value}]: "
        else:
            prompt_string = f"Enter {var_name}, allowed values are ({allowed}): "

    return prompt_str(var_name, default_value, prompt_string, validators)


def prompt_license():
    values = LICENSES + ["none"]
    allowed = " | ".join(LICENSES)
    return prompt_enum("license", "none", f"Add license ({allowed})? [none]: ", values)


def _user_input(var_name: str, prompt_string: str, default_value: Any):
    if not prompt_string:
        if default_value is not None:
            prompt_string = "Enter {} value [{}]: ".format(var_name, default_value)
        else:
            prompt_string = "Enter {} value: ".format(var_name)

    result = input(prompt_string)
    if len(result) == 0:
        result = default_value
    return result


def download_file(src: str, dst: str):
    resp = requests.get(src)
    with open(dst, "w") as f:
        f.write(resp.text)


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


def generate_license_text(license_type: str):
    if license_type not in LICENSES:
        raise ValueError(f'Unknown license type "{license_type}"')

    proc = run(["lice", license_type], stdout=PIPE, check=True)
    return proc.stdout.decode(sys.stdout.encoding)


def generate_license_file(licence_type: str, file: str = "LICENSE"):
    if licence_type.lower() == "none":
        return

    with open(file, "w") as f:
        f.write(generate_license_text(licence_type))
