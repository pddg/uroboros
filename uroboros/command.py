import abc
import argparse
import logging
from typing import TYPE_CHECKING

from uroboros import errors
from uroboros import utils

if TYPE_CHECKING:
    from typing import List, Dict, Optional, Union, Set
    from uroboros.option import Option
    from uroboros.constants import ExitStatus


class Command(metaclass=abc.ABCMeta):
    """Define all actions as command."""

    logger = logging.getLogger(__name__)

    # Name of this command. This name is used as command name in CLI directly.
    name = None  # type: Optional[str]

    # Description of this command.
    description = None  # type: Optional[str]

    # Option for this command
    options = []  # type: List[Option]

    def __init__(self):
        # Remember the depth of nesting
        self._layer = 0

        self.sub_commands = []  # type: List[Command]
        self._parent_ids = {id(self)}  # type: Set[int]

        # The option parser for this command
        # This is enabled after initialization.
        self._parser = None  # type: Optional[argparse.ArgumentParser]

    def execute(self, args: 'Optional[argparse.Namespace]' = None) -> int:
        """
        Execute `uroboros.command.Command.run` internally.
        And return exit code (integer).
        :param args:    Parsed arguments. If None is given, try to parse
                        `sys.argv` by the parser of this command.
        :return:        Exit status (integer only)
        """
        if args is None:
            self.initialize()
            args = self._parser.parse_args()
        # Get all nested validator
        exceptions = self.validate(args)
        layer = self._layer
        while hasattr(args, utils.get_args_validator_name(layer)):
            validator = getattr(args, utils.get_args_validator_name(layer))
            exceptions.extend(validator(args))
            layer += 1
        # Exit with ExitStatus.FAILURE when the parameter validation is failed
        if len(exceptions) > 0:
            for exc in exceptions:
                self.logger.error(str(exc))
            return ExitStatus.FAILURE
        # Execute command
        exit_code = args.func(args)
        return ExitStatus(exit_code)

    @abc.abstractmethod
    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        raise NotImplementedError

    def build_option(self, parser: 'argparse.ArgumentParser') \
            -> 'argparse.ArgumentParser':
        return parser

    def initialize(self, parser: 'Optional[argparse.ArgumentParser]' = None):
        """
        Initialize this command and its sub commands recursively.
        :param parser: `argparse.ArgumentParser` of parent command
        :return: None
        """
        if parser is None:
            self._parser = argparse.ArgumentParser(
                prog=self.name,
                description=self.description,
                parents=[o.get_parser() for o in self.options]
            )
            self._parser.set_defaults(func=self.run)
        else:
            self._parser = parser
        self.build_option(self._parser)
        if len(self.sub_commands) == 0:
            return
        parser = self._parser.add_subparsers(
            dest=utils.get_args_command_name(self._layer),
            title="Sub commands",
        )
        for cmd in self.sub_commands:
            sub_parser = parser.add_parser(
                name=cmd.name,
                description=cmd.description,
                help=cmd.description,
                parents=[o.get_parser() for o in cmd.options],
            )
            # Add validator
            validator_name = utils.get_args_validator_name(self._layer)
            sub_parser.set_defaults(**{validator_name: cmd.validate})
            # Add function to execute
            sub_parser.set_defaults(func=cmd.run)
            cmd.initialize(sub_parser)

    def add_command(self, command: 'Command') -> 'Command':
        """
        Add sub command to this command.
        :param command: An instance of `uroboros.command.Command`
        :return: None
        """
        command_id = id(command)
        if command_id in self._parent_ids or \
                command_id in self._sub_command_ids:
            raise errors.CommandDuplicateError(command, self)
        command.register_parent(self._parent_ids)
        command.increment_nest(self._layer)
        self.sub_commands.append(command)
        return self

    @property
    def _sub_command_ids(self) -> 'Set[int]':
        return {id(cmd) for cmd in self.sub_commands}

    def register_parent(self, parent_ids: 'Set[int]'):
        self._parent_ids |= parent_ids
        for cmd in self.sub_commands:
            cmd.register_parent(self._parent_ids)

    def increment_nest(self, parent_layer_count: int):
        """
        Increment the depth of this command.
        :param parent_layer_count: Number of nest of parent command.
        :return: None
        """
        self._layer = parent_layer_count + 1
        # Propagate the increment to sub commands
        for cmd in self.sub_commands:
            cmd.increment_nest(self._layer)

    def get_sub_commands(self) -> 'Dict[Command, dict]':
        """
        Get the nested dictionary of `Command`.
        Traverse all sub commands of this command recursively.
        :return: Dictionary of command
        {
            self: {
              first_command: {
                first_command_sub_command1: {...},
                # If the command has no sub commands,
                # the value become empty dictionary.
                first_command_sub_command2: {},
              },
              second_command: {
                second_command_sub_command1: {},
                second_command_sub_command2: {},
              },
              ...
            },
        }
        """
        commands_dict = {}
        for sub_cmd in self.sub_commands:
            commands_dict.update(sub_cmd.get_sub_commands())
        return {
            self: commands_dict,
        }

    def print_help(self):
        """
        Helper method for print the help message of this command.
        """
        self._check_initialized()
        return self._parser.print_help()

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        """
        Validate parameters of given options.
        :param args: Parsed arguments
        :return: The list of exceptions
        """
        exceptions = []
        for opt in self.options:
            exceptions.extend(opt.validate(args))
        return exceptions

    def _check_initialized(self):
        initialized = False
        if self._parser is not None:
            initialized = True
        if not initialized:
            raise errors.CommandNotRegisteredError(self.name)
