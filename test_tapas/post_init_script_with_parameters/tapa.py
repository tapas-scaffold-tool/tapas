from tapas.tools import prompt_str


def ask():
    prompt_str("param", default_value="a simple param")
    prompt_str("b", default_value="b_param")


def post_init(param, dict_param, param_with_default=123, **kwargs):
    with open("generated-file.txt", mode="w") as f:
        f.write(f'p={param},dp.a={dict_param["a"]},def={param_with_default}\n')
