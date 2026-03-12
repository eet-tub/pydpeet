import numpy as np
import pytest
import pandas as pd

from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from pydpeet.res.res_for_unittests.res import Mocks

from src.pydpeet import mapping


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "data_frame": Mocks.Mock_mapping.df.copy(),
        "column_map": Mocks.Mock_mapping.column_map,
        "missing_columns": Mocks.Mock_mapping.missing_columns
    }


class Test_mapping_data_frame(object):
    #Only first test
    def test_valid(self, base_args):
        raise NotImplementedError('Test not implemented for variable: data_frame of mapping')
        original_df = base_args["VARIABLE"].copy()
        result = mapping(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_mapping.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_mapping.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["VARIABLE"] = None
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_wrong_type(self, base_args):
        base_args["VARIABLE"] = "wrong type"
        assert not isinstance(base_args["VARIABLE"], pd.DataFrame)
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_empty(self, base_args):
        base_args["VARIABLE"] = pd.DataFrame()
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["VARIABLE"] = base_args["VARIABLE"].drop(Mocks.Mock_mapping.required_columns)
        assert_raises_and_print(KeyError, mapping, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_mapping.required_columns] = base_args["VARIABLE"][Mocks.Mock_mapping.required_columns].astype(int)
        assert base_args["VARIABLE"][Mocks.Mock_mapping.required_columns].dtypes != Mocks.Mock_mapping.required_columns_dtypes
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_nan_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_mapping.required_columns] = np.nan
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_none_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_mapping.required_columns] = None
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_inf_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_mapping.required_columns] = np.inf
        assert_raises_and_print(ValueError, mapping, **base_args)

class Test_mapping_column_map(object):
    """Placeholder failing test for variable 'column_map' of 'mapping'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: column_map of mapping')


class Test_mapping_missing_columns(object):
    """Placeholder failing test for variable 'missing_columns' of 'mapping'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: missing_columns of mapping')



class Test_mapping_df(object):
    """Placeholder failing test for variable 'df' of 'mapping'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: df of mapping')


