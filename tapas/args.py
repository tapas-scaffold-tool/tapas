class TapasArgument:
    def __init__(self, name, prompt=None, postprocessor=None):
        self.name = name
        if not prompt:
            self.prompt = 'Enter \'{}\''.format(name)
        else:
            self.prompt = prompt
        if not postprocessor:
            self.postprocessor = lambda x: x
        else:
            self.postprocessor = postprocessor


def arg(name):
    return TapasArgument(name)


