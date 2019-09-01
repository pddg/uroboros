import abc
import argparse
import logging
import sys
from typing import TYPE_CHECKING

from uroboros import errors
from uroboros import utils
from uroboros.constants import ExitStatus

if TYPE_CHECKING:
    from typing import List, Dict, Optional, Union, Set, Any
    from uroboros.option import Option


class Command(metaclass=abc.ABCMeta):
    """Define all actions as command."""

    logger = logging.getLogger(__name__)

    # Name of this command. This name is used as command name in CLI directly.
    name = None  # type: Optional[str]

    # Description of this command.
    long_description = None  # type: Optional[str]

    # Short description of this command displayed in
    # the help message of parent command.
    short_description = None  # type: Optional[str]

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

    def execute(self, argv: 'List[str]' = None) -> int:
        """
        Execute `uroboros.command.Command.run` internally.
        And return exit code (integer).
        :param argv:    Arguments to parse. If None is given, try to parse
                        `sys.argv` by the parser of this command.
        :return:        Exit status (integer only)
        """
        try:
            self._check_initialized()
        except errors.CommandNotRegisteredError:
            self.initialize()
        if argv is None:
            argv = sys.argv[1:]
        args = self._parser.parse_args(argv)
        # Get all nested validator and hook before validation
        exceptions = self.validate(args)
        layer = self._layer
        while hasattr(args, utils.get_args_command_name(layer)):
            sub_cmd = getattr(args, utils.get_args_command_name(layer))
            exceptions.extend(sub_cmd.validate(args))
            layer += 1
        # Exit with ExitStatus.FAILURE when the parameter validation is failed
        if len(exceptions) > 0:
            for exc in exceptions:
                self.logger.error(str(exc))
            return ExitStatus.FAILURE
        # Execute command
        exit_code = args.func(args)
        # FIXME: Just return when drop support for Python 3.5
        try:
            return ExitStatus(exit_code)
        except ValueError:
            if isinstance(exit_code, int):
                if exit_code < 0 or exit_code > 255:
                    return ExitStatus.OUT_OF_RANGE
            return ExitStatus.INVALID

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
            self._parser = self.create_default_parser()
        else:
            self._parser = parser
        # Add validator
        cmd_name = utils.get_args_command_name(self._layer)
        self._parser.set_defaults(**{cmd_name: self})
        # Add function to execute
        self._parser.set_defaults(func=self.run)
        self.build_option(self._parser)
        self.initialize_sub_parsers(self._parser)

    def initialize_sub_parsers(self, parser: 'argparse.ArgumentParser'):
        if len(self.sub_commands) == 0:
            return
        parser = parser.add_subparsers(
            dest=utils.get_args_section_name(self._layer),
            title="Sub commands",
        )
        for cmd in self.sub_commands:
            sub_parser = parser.add_parser(
                name=cmd.name,
                description=cmd.long_description,
                help=cmd.short_description,
                parents=[o.get_parser() for o in cmd.options],
            )
            cmd.initialize(sub_parser)

    def create_default_parser(self) -> 'argparse.ArgumentParser':
        parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.long_description,
            parents=[o.get_parser() for o in self.options]
        )
        parser.set_defaults(func=self.run)
        return parser

    def add_command(self, command: 'Command') -> 'Command':
        """
        Add sub command to this command.
        :param command: An instance of `uroboros.command.Command`
        :return: None
        """
        assert isinstance(command, Command), \
            "Given command is not an instance of `uroboros.Command` or" \
            "an instance of its subclass."
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
            commands_dict.update(sub_cmd.get_all_sub_commands())
        return {
            self: commands_dict,
        }

    def print_help(self):
        """
        Helper method for print the help message of this command.
        """
        self._check_initialized()
        return self._parser.print_help()

    def _call_one_by_one(self,
                         commands: 'List[Command]',
                         method_name: str,
                         args: 'Any'):
        for cmd in commands:
            assert hasattr(cmd, method_name), "'{cmd}' has no method '{method}".format(
                cmd=cmd.__name__,
                method=method_name
            )
            args = getattr(cmd, method_name)(args)
        return args

    def before_validate(self, unsafe_args: 'argparse.Namespace') -> 'argparse.Namespace':
        """
        Hook function before validation. This method will be called in order from
        root command to its children.
        Use `unsafe_args` carefully since it has not been validated yet.
        You can set any value into `unsafe_args` and you must return it finally.
        :param unsafe_args: An instance of argparse.Namespace
        :return: An instance of argparse.Namespace
        """
        return unsafe_args

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
