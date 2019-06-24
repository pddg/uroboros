import abc
import argparse
import logging
from typing import TYPE_CHECKING

from uroboros import errors
from uroboros import utils

if TYPE_CHECKING:
    from typing import List, Dict, Optional, Union
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
        # TODO: Make more simply
        # Get all nested commands to validate
        command_names = []
        layer = 0
        while hasattr(args, utils.get_args_layer_name(layer)):
            name = getattr(args, utils.get_args_layer_name(layer))
            command_names.append(name)
            layer += 1
        # Define command to execute
        to_execute = self
        exceptions = self.validate(args)
        if len(command_names) > 0:
            # Find sub command
            cmd_dict = self.get_sub_commands()
            for name in command_names:
                cmd_dict = cmd_dict.get(to_execute)
                cmd_dict = utils.get_matched_command(name, cmd_dict)
                to_execute = list(cmd_dict.keys())[0]
                exceptions.extend(to_execute.validate(args))
        # Exit with EXIT_FAILURE when the parameter validation is failed
        if len(exceptions) > 0:
            for exc in exceptions:
                self.logger.error(str(exc))
            return utils.to_int(ExitStatus.FAILURE)
        # Execute command
        exit_code = args.func(args)
        return utils.to_int(exit_code)

    @abc.abstractmethod
    def run(self, args: 'argparse.Namespace') -> 'Union[ExitStatus, int]':
        raise NotImplementedError

    def build_option(self, parser: 'argparse.ArgumentParser') -> 'argparse.ArgumentParser':
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
            dest=utils.get_args_layer_name(self._layer),
            title="Sub commands",
        )
        for cmd in self.sub_commands:
            sub_parser = parser.add_parser(
                name=cmd.name,
                description=cmd.description,
                help=cmd.description,
                parents=[o.get_parser() for o in cmd.options],
            )
            sub_parser.set_defaults(func=cmd.run)
            cmd.initialize(sub_parser)

    def add_command(self, command: 'Command') -> 'Command':
        """
        Add sub command to this command.
        :param command: An instance of `uroboros.command.Command`
        :return: None
        """
        command.increment_nest(self._layer)
        self.sub_commands.append(command)
        return self

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
        # TODO: Execute validation recursively
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
