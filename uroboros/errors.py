class CommandNotRegisteredError(Exception):

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"Command '{self.name}' has not been registered yet."


class NoCommandError(Exception):

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"There is no command named '{self.name}'."
