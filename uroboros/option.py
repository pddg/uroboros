import abc
import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


class Option(metaclass=abc.ABCMeta):

    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)

    def get_parser(self) -> 'argparse.ArgumentParser':
        return self.build_option(self.parser)

    @abc.abstractmethod
    def build_option(self, parser: 'argparse.ArgumentParser') \
            -> 'argparse.ArgumentParser':
        raise NotImplementedError

    @abc.abstractmethod
    def validate(self, args: 'argparse.Namespace') -> 'List[Exception]':
        raise NotImplementedError
