from unittest import mock

import pytest

from uroboros import utils

incrementer = mock.MagicMock()
incrementer.method = lambda x: x+1

decrementer = mock.MagicMock()
decrementer.method = lambda x: x-1


@pytest.mark.parametrize(
    'objs,expected', [
        ([incrementer], 1),
        ([decrementer], -1),
        ([incrementer, incrementer], 2),
        ([incrementer, decrementer], 0),
    ]
)
def test_call_one_by_one(objs, expected):
    assert utils.call_one_by_one(objs, "method", 0) == expected
