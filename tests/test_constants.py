import pytest

from uroboros.constants import ExitStatus


class TestExitStatus(object):

    @pytest.mark.parametrize(
        'exit_code', [0, 1, 2, 126, 127, 128, 130]
    )
    def test_assumed(self, exit_code):
        expected = exit_code
        actual = ExitStatus(exit_code)
        assert expected == actual

    @pytest.mark.parametrize(
        'exit_code', [3, 64, 125]
    )
    def test_undefined(self, exit_code):
        expected_value = exit_code
        expected_name = "EXIT_WITH_{}".format(exit_code)
        actual = ExitStatus(exit_code)
        assert expected_value == actual.value
        assert expected_name == actual.name

    @pytest.mark.parametrize(
        'exit_code', [129, 254]
    )
    def test_fatal_signal(self, exit_code):
        expected_value = exit_code
        expected_name = "FATAL_SIGNAL_{}".format(exit_code - 128)
        actual = ExitStatus(exit_code)
        assert expected_value == actual.value
        assert expected_name == actual.name

    @pytest.mark.parametrize(
        'exit_code', [-1, 256]
    )
    def test_out_of_range(self, exit_code):
        expected = ExitStatus.OUT_OF_RANGE
        actual = ExitStatus(exit_code)
        assert expected == actual

    @pytest.mark.parametrize(
        'exit_code', [1.5, '0', None]
    )
    def test_invalid(self, exit_code):
        expected = ExitStatus.INVALID
        actual = ExitStatus(exit_code)
        assert expected == actual
