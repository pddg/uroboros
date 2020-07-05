import abc
import argparse
import logging
import sys
from typing import TYPE_CHECKING

from uroboros import errors
from uroboros import utils
from uroboros.constants import ExitStatus

if TYPE_CHECKING:
    from typing import List, Dict, Optional, Union, Set
    from uroboros.option import Option
    CommandDict = Dict['Command', 'Optional[Command]']


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
        """Execute the command and return exit code (integer)

        Args:
            argv (:obj: List[str], optional): Arguments to parse. If None is
                given (e.g. do not pass any args), try to parse `sys.argv` .

        Returns:
            int: Exit status code
        """
        assert getattr(self, "name", None) is not None, \
            "{} does not have `name` attribute.".format(
                self.__class__.__name__)
        try:
            self._check_initialized()
        except errors.CommandNotRegisteredError:
            self.initialize()
        if argv is None:
            argv = sys.argv[1:]
        args = self._parser.parse_args(argv)
        commands = self.get_sub_commands(args)
        # Run hook before validation
        args = self._pre_hook(args, commands)
        # Execute validation recursively
        exceptions = self._validate_all(args, commands)
        # Exit with ExitStatus.FAILURE when the parameter validation is failed
        if len(exceptions) > 0:
            for exc in exceptions:
                self.logger.error(str(exc))
            return ExitStatus.FAILURE
        # Run hook after validation
        args = self._pre_hook_validated(args, commands)
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
        """This method must implement user defined action.

        This method is an abstract method of this class. This should be
        overwitten by the user. Return exit status code after execution.

        Args:
            args (argparse.Namespace): Parsed arguments.

        Returns:
            Union[ExitStatus, int]: Exit status code
        """
        raise NotImplementedError

    def build_option(self, parser: 'argparse.ArgumentParser') \
            -> 'argparse.ArgumentParser':
        """Configure ArgumentParser to add user defined options of this command.

        If you want to add your own option to this command, you can override
        this function. Then, you can configure the parser given by argument
        of this function.

        Args:
            parser (argparse.ArgumentParser): Parsed arguments.

        Returns:
            argparse.ArgumentParser: Configured argument parser.
        """
        return parser

    def initialize(self, parser: 'Optional[argparse.ArgumentParser]' = None):
        """Initialize this command and its sub commands recursively.

        Args:
            parser (argparse.ArgumentParser): ArgumentParser of parent command
        """
        if parser is None:
            self._parser = self._create_default_parser()
        else:
            self._parser = parser
        # Add validator
        cmd_name = utils.get_args_command_name(self._layer)
        self._parser.set_defaults(**{cmd_name: self})
        # Add function to execute
        self._parser.set_defaults(func=self.run)
        self.build_option(self._parser)
        self._initialize_sub_parsers(self._parser)

    def _initialize_sub_parsers(self, parser: 'argparse.ArgumentParser'):
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
                parents=[o.get_parser() for o in cmd.get_options()],
            )
            cmd.initialize(sub_parser)

    def _create_default_parser(self) -> 'argparse.ArgumentParser':
        parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.long_description,
            parents=[o.get_parser() for o in self.get_options()]
        )
        parser.set_defaults(func=self.run)
        return parser

    def add_command(self, *commands: 'Command') -> 'Command':
        """Add sub command to this command.

        Add one or more commands to this command.
        The added commands are callable as its sub command.

        Args:
            commands: An instance of sub commands
        """
        for command in commands:
            assert isinstance(command, Command), \
                "Given command is not an instance of `uroboros.Command` or" \
                "an instance of its subclass."
            assert getattr(command, "name", None) is not None, \
                "{} does not have `name` attribute.".format(
                    command.__class__.__name__)
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
        """Register parent command

        This function is used internaly.
        Register all parent command ids to check that the command has
        already been registered.

        Args:
            parent_ids (Set[int]): Set of parent command instance ids
        """
        self._parent_ids |= parent_ids
        for cmd in self.sub_commands:
            cmd.register_parent(self._parent_ids)

    def increment_nest(self, parent_layer_count: int):
        """Increment the depth of this command and its children.

        This function is used internaly.
        Increment the nest of this command and its children recursively.

        Args:
            parent_layer_count (int): Number of nest of parent command.
        """
        self._layer = parent_layer_count + 1
        # Propagate the increment to sub commands
        for cmd in self.sub_commands:
            cmd.increment_nest(self._layer)

    def get_sub_commands(self, args: 'argparse.Namespace') -> 'List[Command]':
        """Get the list of `Command` specified by CLI except myself.

        If myself is root_cmd and "root_cmd first_cmd second_cmd"
        is specified in CLI, this may return the instances of first_cmd
        and second_cmd.

        Returns:
            List[Command]: Child commands of this command.
        """
        commands = []
        # Do not include myself
        layer = self._layer + 1
        while hasattr(args, utils.get_args_command_name(layer)):
            cmd = getattr(args, utils.get_args_command_name(layer))
            commands.append(cmd)
            layer += 1
        return commands

    def get_all_sub_commands(self) -> 'Dict[Command, CommandDict]':
        """Get all child commands of this command including itself.

        Traverse all sub commands of this command recursively.
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

        Returns:
           Dict[Command, CommandDict]: All child commands of this command.
        """
        commands_dict = {}
        for sub_cmd in self.sub_commands:
            commands_dict.update(sub_cmd.get_all_sub_commands())
        return {
            self: commands_dict,
        }

    def get_options(self) -> 'List[Option]':
        """Get all uroboros.`Option instance of this `Command.

        Returns:
            List[Option]: List of uroboros.Option instance
        """
        return [opt() if type(opt) == type else opt for opt in self.options]

    def print_help(self):
        """Helper method for print the help message of this command.

        Raises:
            errors.CommandNotRegisteredError: If this command has
                not been initialized.

        Note:
            This function can be called after initialization.
        """
        self._check_initialized()
        return self._parser.print_help()

    def _pre_hook(self,
                  args: 'argparse.Namespace',
                  sub_commands: 'List[Command]') -> 'argparse.Namespace':
        return utils.call_one_by_one(
            [self] + sub_commands,
            "_hook",
            args,
            hook_name="before_validate"
        )

    def _hook(self,
              args: 'argparse.Namespace',
              hook_name: str) -> 'argparse.Namespace':
        for opt in self.get_options():
            assert hasattr(opt, hook_name), \
                "{} does not have '{}' method".format(
                    opt.__class__.__name__, hook_name)
            args = getattr(opt, hook_name)(args)
        assert hasattr(self, hook_name), \
            "{} does not have '{}' method".format(
                self.__class__.__name__, hook_name)
        args = getattr(self, hook_name)(args)
        return args

    def before_validate(self,
                        unsafe_args: 'argparse.Namespace'
                        ) -> 'argparse.Namespace':
        """Hook function before validation

        This method will be called in order from root command to its children.
        Use `unsafe_args` carefully since it has not been validated yet.
        You can set any value into `unsafe_args` and you must return it
        finally.

        Args:
            unsafe_args (argparse.Namespace): Parsed arguments which
                are not validated.
        Returns:
            argparse.Namespace: An instance of argparse.Namespace
        """
        return unsafe_args

    def _validate_all(self,
                      args: 'argparse.Namespace',
                      sub_commands: 'List[Command]') -> 'List[Exception]':
        exceptions = []
        for cmd in [self] + sub_commands:
            exceptions.extend(cmd.validate(args))
        return exceptions

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        """Validate parameters of given options.

        Args:
            args (argparse.Namespace): Parsed arguments which
                are not validated.
        Returns:
            List[Exception]: The list of exceptions
        """
        exceptions = []
        for opt in self.options:
            exceptions.extend(opt.validate(args))
        return exceptions

    def _pre_hook_validated(self,
                            args: 'argparse.Namespace',
                            sub_commands: 'List[Command]'
                            ) -> 'argparse.Namespace':
        return utils.call_one_by_one(
            [self] + sub_commands,
            "_hook",
            args,
            hook_name='after_validate'
        )

    def after_validate(self,
                       safe_args: 'argparse.Namespace'
                       ) -> 'argparse.Namespace':
        """Hook function after validation.

        This method will be called in order from root command to 
        its children. Given argument `safe_args` is validated by
        validation method of your commands. You can set any value
        into `safe_args` and you must return it finally.

        Args:
            safe_args (argparse.Namespace): Validated arguments

        Returns:
            argparse.Namespace: An instance of argparse.Namespace
        """
        return safe_args

    def _check_initialized(self):
        """Check that this command has been initialized.

        Raises:
            errors.CommandNotRegisteredError: If this command has
                not been initialized.
        """
        if self._parser is None:
            raise errors.CommandNotRegisteredError(self.name)
