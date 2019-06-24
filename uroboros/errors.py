class CommandNotRegisteredError(Exception):

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return "Command '{name}' has not been registered yet."\
            .format(name=self.name)


class NoCommandError(Exception):

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return "There is no command named '{name}'."\
            .format(name=self.name)
