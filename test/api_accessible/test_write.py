import pytest

from pydpeet.res.res_for_unittests.res import Mocks


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "data_input": Mocks.Mock_write.data_input,
        "output_path": Mocks.Mock_write.output_path,
        "output_file_name": Mocks.Mock_write.output_file_name,
        "data_output_filetype": Mocks.Mock_write.data_output_filetype,
    }


class Test_write_data_input:
    """Placeholder failing test for variable 'data_input' of 'write'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: data_input of write")


class Test_write_output_path:
    """Placeholder failing test for variable 'output_path' of 'write'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: output_path of write")


class Test_write_output_file_name:
    """Placeholder failing test for variable 'output_file_name' of 'write'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: output_file_name of write")


class Test_write_data_output_filetype:
    """Placeholder failing test for variable 'data_output_filetype' of 'write'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: data_output_filetype of write")
