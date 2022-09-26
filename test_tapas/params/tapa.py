from tapas.params import StrParameter, IntParameter


def get_params():
    return [
        IntParameter("a.b"),
        StrParameter("a.c"),
    ]
