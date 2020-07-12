import abc
import argparse
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


class Option(metaclass=abc.ABCMeta):
    """Common option class"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)

    @lru_cache()
    def get_parser(self) -> 'argparse.ArgumentParser':
        return self.build_option(self.parser)

    @abc.abstractmethod
    def build_option(self, parser: 'argparse.ArgumentParser') \
            -> 'argparse.ArgumentParser':
        """Configure ArgumentParser to add user defined options of this command.

        You must override this function. You should configure the parser given
        by argument of this function, then return the parser.
        This method and `uroboros.Command.build_option` method are functionally
        equivalent.

        Args:
            parser (argparse.ArgumentParser): Initialized argument parser

        Returns:
            argparse.ArgumentParser: Configured argument parser.
        """
        raise NotImplementedError

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

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        """Validate parameters of given options.

        Args:
            args (argparse.Namespace): Parsed arguments which
                are not validated.
        Returns:
            List[Exception]: The list of exceptions
        """
        return []

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
