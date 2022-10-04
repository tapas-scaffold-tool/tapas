import sys
from encodings import utf_8
from subprocess import Popen, PIPE, TimeoutExpired
from typing import Any


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
