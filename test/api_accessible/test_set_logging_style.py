import numpy as np
import pytest
import pandas as pd

from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from pydpeet.res.res_for_unittests.res import Mocks

from src.pydpeet import set_logging_style


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "level": Mocks.Mock_set_logging_style.level,
        "formatting_string": Mocks.Mock_set_logging_style.formatting_string,
    }


class Test_set_logging_style_level(object):
    """Placeholder failing test for variable 'level' of 'set_logging_style'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: level of set_logging_style')


class Test_set_logging_style_formatting_string(object):
    """Placeholder failing test for variable 'formatting_string' of 'set_logging_style'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: formatting_string of set_logging_style')


