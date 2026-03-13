import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import convert


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "config": Mocks.Mock_convert.config,
        "input_path": Mocks.Mock_convert.input_path,
        "output_path": Mocks.Mock_convert.output_path,
        "keep_all_additional_data": Mocks.Mock_convert.keep_all_additional_data,
        "custom_folder_path": Mocks.Mock_convert.custom_folder_path,
    }


class Test_convert_config:
    """Placeholder failing test for variable 'config' of 'convert'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: config of convert")


class Test_convert_input_path:
    """Placeholder failing test for variable 'input_path' of 'convert'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: input_path of convert")


class Test_convert_output_path:
    """Placeholder failing test for variable 'output_path' of 'convert'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: output_path of convert")


class Test_convert_keep_all_additional_data:
    def test_true(self, base_args):
        base_args["keep_all_additional_data"] = True
        result = convert(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_convert.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_convert.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        base_args["keep_all_additional_data"] = False
        result = convert(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_convert.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_convert.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["keep_all_additional_data"] = None
        assert_raises_and_print(ValueError, convert, **base_args)

    def test_wrong_type(self, base_args):
        base_args["keep_all_additional_data"] = "wrong type"
        assert not isinstance(base_args["keep_all_additional_data"], bool)
        assert_raises_and_print(ValueError, convert, **base_args)


class Test_convert_custom_folder_path:
    """Placeholder failing test for variable 'custom_folder_path' of 'convert'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: custom_folder_path of convert")
