import pytest

from pydpeet.res.res_for_unittests.res import Mocks


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "filename": Mocks.Mock_write.filename,
    }


class Test_write_to_bibtex_filename:
    """Placeholder failing test for variable 'filename' of 'write_to_bibtex'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: filename of write_to_bibtex")
