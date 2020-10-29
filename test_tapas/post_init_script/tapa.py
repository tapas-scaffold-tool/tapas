def ask():
    pass


def post_init():
    with open("generated-file.txt", mode="w") as f:
        f.write("Generated text.\n")
