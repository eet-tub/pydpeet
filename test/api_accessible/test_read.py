import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import _assert_raises_and_print
from src.pydpeet import read


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "config": Mocks.Mock_read.config,
        "input_path": Mocks.Mock_read.input_path,
        "keep_all_additional_data": Mocks.Mock_read.keep_all_additional_data,
        "custom_folder_path": Mocks.Mock_read.custom_folder_path,
    }


class Test_read_config:
    """Placeholder failing test for variable 'config' of 'read'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: config of read")


class Test_read_input_path:
    def test_blacklisted_file(self, base_args):
        base_args["input_path"] = Mocks.Mock_read.blacklisted_input_path
        _assert_raises_and_print(ValueError, read, **base_args)

    def test_blacklisted_file_without_config(self, base_args):
        base_args["config"] = None
        base_args["input_path"] = Mocks.Mock_read.blacklisted_input_path
        _assert_raises_and_print(ValueError, read, **base_args)

    def test_blacklisted_file_in_list(self, base_args):
        base_args["input_path"] = Mocks.Mock_read.blacklisted_input_path_in_list
        _assert_raises_and_print(ValueError, read, **base_args)

    def test_folder_skips_blacklisted_files(self, base_args):
        base_args["config"] = "digatron_4_20_6_236"
        base_args["input_path"] = Mocks.Mock_read.folder_input_path
        result = read(**base_args)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], pd.DataFrame)

    def test_folder_without_config_skips_blacklisted_files(self, base_args):
        base_args["config"] = None
        base_args["input_path"] = Mocks.Mock_read.folder_input_path
        result = read(**base_args)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], pd.DataFrame)


class Test_read_keep_all_additional_data:
    def test_true(self, base_args):
        base_args["keep_all_additional_data"] = True
        result = read(**base_args)
        expected = Mocks.Mock_read.df_expected_with_additional_data
        assert pd.DataFrame.equals(result, expected)

    def test_false(self, base_args):
        base_args["keep_all_additional_data"] = False
        result = read(**base_args)
        expected = Mocks.Mock_read.df_expected_without_additional_data
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["keep_all_additional_data"] = None
        _assert_raises_and_print(ValueError, read, **base_args)

    def test_wrong_type(self, base_args):
        base_args["keep_all_additional_data"] = "wrong type"
        assert not isinstance(base_args["keep_all_additional_data"], bool)
        _assert_raises_and_print(ValueError, read, **base_args)


class Test_read_custom_folder_path:
    """Placeholder failing test for variable 'custom_folder_path' of 'read'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: custom_folder_path of read")
