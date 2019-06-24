from enum import Enum


class ExitStatus(Enum):
    SUCCESS = 0
    FAILURE = 1
    MISS_USAGE = 2
