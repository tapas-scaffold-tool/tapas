import click
import os


@click.command()
@click.argument('tapa')
def main(tapa):
    _walk(_get_path(tapa), os.getcwd(), None)


def _walk(src, dst, file_processor):
    for cur_dir, subdir_list, file_list in os.walk(src):
        _make_dir_if_absent(os.path.join(dst, os.path.relpath(cur_dir, src)))
        for f in file_list:
            src_file_name = os.path.join(cur_dir, f)
            dst_file_name = os.path.join(dst, os.path.relpath(src_file_name, src))

            with open(src_file_name, 'r') as src_file, open(dst_file_name, 'w') as dst_file:
                dst_file.writelines(src_file.readlines())


def _get_path(path):
    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))


def _make_dir_if_absent(full_path):
    if os.path.exists(full_path):
        if not os.path.isdir(full_path):
            raise Exception('%s exists but is a file' % full_path)
    else:
        os.makedirs(full_path)
