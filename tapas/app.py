import click
import os
from os import path as path
from jinja2 import Environment, Template, FileSystemLoader, Undefined, StrictUndefined


@click.command()
@click.argument('tapa')
def main(tapa):
    params = _get_params()
    _walk(_get_path(tapa), os.getcwd(), params)


def _walk(src, dst, params):
    env = Environment(
        loader=FileSystemLoader(src),
        undefined=StrictUndefined,
    )
    for cur_dir, subdir_list, file_list in os.walk(src):
        rendered_dst_dir = path.join(dst, env.from_string(path.relpath(cur_dir, src)).render(params))
        _make_dir_if_absent(rendered_dst_dir)
        for f in file_list:
            src_file_name = path.join(cur_dir, f)
            dst_file_name = path.join(dst, env.from_string(path.relpath(src_file_name, src)).render(params))

            t = env.get_template(_get_template_name(src, src_file_name))
            with open(dst_file_name, 'w') as wrt:
                wrt.write(t.render(params))


def _get_path(path):
    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))


def _make_dir_if_absent(full_path):
    if os.path.exists(full_path):
        if not os.path.isdir(full_path):
            raise Exception('%s exists but is a file' % full_path)
    else:
        os.makedirs(full_path)


def _get_template_name(src, full_path):
    return os.path.relpath(full_path, src).replace('\\', '/')


def _get_params():
    return {
        'a': 'Aaa!!!',
        'b': 'Boo',
    }
