from tapas.params import StrParameter


def get_params():
    return [
        StrParameter("directory_name"),
        StrParameter("file_name"),
        StrParameter("value_in_file"),
    ]
