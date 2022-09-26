def post_init(params):
    with open("generated-file.txt", mode="w") as f:
        f.write("Generated text.\n")
