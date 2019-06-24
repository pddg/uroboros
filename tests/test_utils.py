import pytest

from uroboros import utils
from uroboros.constants import ExitStatus


class TestToInt:

    @pytest.mark.parametrize(
        'exit_code', (0, 1, 127)
    )
    def test_normal_int(self, exit_code):
        actual = utils.to_int(exit_code)
        assert actual == exit_code

    @pytest.mark.parametrize(
        'exit_code', (
            ExitStatus.SUCCESS,
            ExitStatus.FAILURE,
            ExitStatus.MISS_USAGE,
        )
    )
    def test_normal_status(self, exit_code):
        actual = utils.to_int(exit_code)
        assert actual == exit_code.value
