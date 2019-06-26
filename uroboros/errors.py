from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uroboros import Command


class CommandNotRegisteredError(Exception):

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return "Command '{name}' has not been registered yet." \
            .format(name=self.name)


class NoCommandError(Exception):

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return "There is no command named '{name}'." \
            .format(name=self.name)


class CommandDuplicateError(Exception):

    def __init__(self, command: 'Command', parent: 'Command'):
        self.command = command
        self.parent = parent

    def __str__(self):
        return \
            "The command '{name}' has already been registered" \
            " in '{parent}' or its parents.".format(
                name=self.command.__class__.__name__,
                parent=self.parent.__class__.__name__)
