from typing import TYPE_CHECKING

from uroboros import errors

if TYPE_CHECKING:
    from typing import Dict
    from uroboros.command import Command
    CommandDict = Dict[Command, dict]
    CommandsDict = Dict[Command, CommandDict]


def get_args_command_name(layer: int):
    return "__layer{layer}_command".format(layer=layer)


def get_args_validator_name(layer: int):
    return "__layer{layer}_validator".format(layer=layer)


def get_matched_command(name, command_dict: 'CommandsDict') -> 'CommandDict':
    for cmd, sub_cmds in command_dict.items():
        if cmd.name == name:
            return {cmd: sub_cmds}
    raise errors.NoCommandError(name)
