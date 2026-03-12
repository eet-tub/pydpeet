import numpy as np
import pytest
import pandas as pd

from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from pydpeet.res.res_for_unittests.res import Mocks

from src.pydpeet import add_capacity


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df": Mocks.Mock_add_capacity.df.copy(),
        "df_primitives": Mocks.Mock_add_capacity.df_primitives.copy(),
        "neware_bool": Mocks.Mock_add_capacity.neware_bool,
        "config": Mocks.Mock_add_capacity.config,
        "verbose": Mocks.Mock_add_capacity.verbose,
    }


class Test_add_capacity_df(object):
    def test_valid(self, base_args):
        original_df = base_args["df"].copy()
        result = add_capacity(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["df"] = None
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df"] = "wrong type"
        assert not isinstance(base_args["df"], pd.DataFrame)
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_empty(self, base_args):
        base_args["df"] = pd.DataFrame()
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df"] = base_args["df"].drop(Mocks.Mock_add_capacity.required_columns)
        assert_raises_and_print(KeyError, add_capacity, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df"][Mocks.Mock_add_capacity.required_columns] = base_args["df"][Mocks.Mock_add_capacity.required_columns].astype(int)
        assert base_args["df"][Mocks.Mock_add_capacity.required_columns].dtypes != Mocks.Mock_add_capacity.required_columns_dtypes
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_nan_values(self, base_args):
        base_args["df"][Mocks.Mock_add_capacity.required_columns] = np.nan
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_none_values(self, base_args):
        base_args["df"][Mocks.Mock_add_capacity.required_columns] = None
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_inf_values(self, base_args):
        base_args["df"][Mocks.Mock_add_capacity.required_columns] = np.inf
        assert_raises_and_print(ValueError, add_capacity, **base_args)

class Test_add_capacity_df_primitives(object):
    def test_valid(self, base_args):
        original_df = base_args["df_primitives"].copy()
        result = add_capacity(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["df_primitives"] = None
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df_primitives"] = "wrong type"
        assert not isinstance(base_args["df_primitives"], pd.DataFrame)
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_empty(self, base_args):
        base_args["df_primitives"] = pd.DataFrame()
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df_primitives"] = base_args["df_primitives"].drop(Mocks.Mock_add_capacity.required_columns)
        assert_raises_and_print(KeyError, add_capacity, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df_primitives"][Mocks.Mock_add_capacity.required_columns] = base_args["df_primitives"][Mocks.Mock_add_capacity.required_columns].astype(int)
        assert base_args["df_primitives"][Mocks.Mock_add_capacity.required_columns].dtypes != Mocks.Mock_add_capacity.required_columns_dtypes
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_nan_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_add_capacity.required_columns] = np.nan
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_none_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_add_capacity.required_columns] = None
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_inf_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_add_capacity.required_columns] = np.inf
        assert_raises_and_print(ValueError, add_capacity, **base_args)


class Test_add_capacity_config(object):
    """Placeholder failing test for variable 'config' of 'add_capacity'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: config of add_capacity')


class Test_add_capacity_neware_bool(object):
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["neware_bool"] = True
        result = add_capacity(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["neware_bool"] = False
        result = add_capacity(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)
        
    def test_none(self, base_args):
        base_args["neware_bool"] = None
        assert_raises_and_print(ValueError, add_capacity, **base_args)
        
    def test_wrong_type(self, base_args):
        base_args["neware_bool"] = "wrong type"
        assert not isinstance(base_args["neware_bool"], bool)
        assert_raises_and_print(ValueError, add_capacity, **base_args)


class Test_add_capacity_verbose(object):
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["verbose"] = True
        result = add_capacity(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["verbose"] = False
        result = add_capacity(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["verbose"] = None
        assert_raises_and_print(ValueError, add_capacity, **base_args)

    def test_wrong_type(self, base_args):
        base_args["verbose"] = "wrong type"
        assert not isinstance(base_args["verbose"], bool)
        assert_raises_and_print(ValueError, add_capacity, **base_args)


