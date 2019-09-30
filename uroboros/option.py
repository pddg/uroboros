import abc
import argparse
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


class Option(metaclass=abc.ABCMeta):

    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)

    @lru_cache()
    def get_parser(self) -> 'argparse.ArgumentParser':
        return self.build_option(self.parser)

    @abc.abstractmethod
    def build_option(self, parser: 'argparse.ArgumentParser') \
            -> 'argparse.ArgumentParser':
        raise NotImplementedError

    def before_validate(self,
                        unsafe_args: 'argparse.Namespace'
                        ) -> 'argparse.Namespace':
        return unsafe_args

    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        return []

    def after_validate(self,
                       safe_args: 'argparse.Namespace'
                       ) -> 'argparse.Namespace':
        return safe_args
