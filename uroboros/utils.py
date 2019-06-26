from typing import TYPE_CHECKING

from uroboros import errors
from uroboros.constants import ExitStatus

if TYPE_CHECKING:
    from typing import Dict, Union
    from uroboros.command import Command


def get_args_command_name(layer: int):
    return "__layer{layer}_command".format(layer=layer)


def get_args_validator_name(layer: int):
    return "__layer{layer}_validator".format(layer=layer)


def get_matched_command(name, command_dict: 'Dict[Command, Dict[Command, dict]]') -> 'Dict[Command, dict]':
    for cmd, sub_cmds in command_dict.items():
        if cmd.name == name:
            return {cmd: sub_cmds}
    raise errors.NoCommandError(name)


def to_int(exit_code: 'Union[ExitStatus, int]'):
    if isinstance(exit_code, ExitStatus):
        return exit_code.value
    if isinstance(exit_code, int):
        return exit_code
    raise ValueError("exit_code must be 'uroboros.constants.ExitStatus' or int.")
