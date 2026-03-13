import pytest

from pydpeet.res.res_for_unittests.res import Mocks


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "level": Mocks.Mock_set_logging_style.level,
        "formatting_string": Mocks.Mock_set_logging_style.formatting_string,
    }


class Test_set_logging_style_level:
    """Placeholder failing test for variable 'level' of 'set_logging_style'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: level of set_logging_style")


class Test_set_logging_style_formatting_string:
    """Placeholder failing test for variable 'formatting_string' of 'set_logging_style'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: formatting_string of set_logging_style")
