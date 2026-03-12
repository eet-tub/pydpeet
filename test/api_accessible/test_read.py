import numpy as np
import pytest
import pandas as pd

from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from pydpeet.res.res_for_unittests.res import Mocks

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


class Test_read_config(object):
    """Placeholder failing test for variable 'config' of 'read'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: config of read')


class Test_read_input_path(object):
    """Placeholder failing test for variable 'input_path' of 'read'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: input_path of read')


class Test_read_keep_all_additional_data(object):
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["keep_all_additional_data"] = True
        result = read(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_read.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_read.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["keep_all_additional_data"] = False
        result = read(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_read.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_read.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["keep_all_additional_data"] = None
        assert_raises_and_print(ValueError, read, **base_args)

    def test_wrong_type(self, base_args):
        base_args["keep_all_additional_data"] = "wrong type"
        assert not isinstance(base_args["keep_all_additional_data"], bool)
        assert_raises_and_print(ValueError, read, **base_args)



class Test_read_custom_folder_path(object):
    """Placeholder failing test for variable 'custom_folder_path' of 'read'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: custom_folder_path of read')


