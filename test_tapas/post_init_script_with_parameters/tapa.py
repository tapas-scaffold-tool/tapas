from tapas.params import StrParameter


def get_params():
    return [
        StrParameter("param"),  # default_value="a simple param"
        StrParameter("b"),  # default_value="b_param"
    ]


def post_init(params):
    with open("generated-file.txt", mode="w") as f:
        f.write(f'p={params["param"]}\n')
