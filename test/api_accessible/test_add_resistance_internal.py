import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import add_resistance_internal


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df": Mocks.Mock_add_resistance_internal.df.copy(),
        "config": Mocks.Mock_add_resistance_internal.config,
        "verbose": Mocks.Mock_add_resistance_internal.verbose,
    }


class Test_add_resistance_internal_df:
    # Only first test
    def test_valid(self, base_args):
        original_df = base_args["df"].copy()
        result = add_resistance_internal(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_resistance_internal.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_resistance_internal.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["df"] = None
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df"] = "wrong type"
        assert not isinstance(base_args["df"], pd.DataFrame)
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)

    def test_empty(self, base_args):
        base_args["df"] = pd.DataFrame()
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df"] = base_args["df"].drop(Mocks.Mock_add_resistance_internal.required_columns)
        assert_raises_and_print(KeyError, add_resistance_internal, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df"][Mocks.Mock_add_resistance_internal.required_columns] = base_args["df"][Mocks.Mock_add_resistance_internal.required_columns].astype(int)
        assert base_args["df"][Mocks.Mock_add_resistance_internal.required_columns].dtypes != Mocks.Mock_add_resistance_internal.required_columns_dtypes
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)

    def test_nan_values(self, base_args):
        base_args["df"][Mocks.Mock_add_resistance_internal.required_columns] = np.nan
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)

    def test_none_values(self, base_args):
        base_args["df"][Mocks.Mock_add_resistance_internal.required_columns] = None
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)

    def test_inf_values(self, base_args):
        base_args["df"][Mocks.Mock_add_resistance_internal.required_columns] = np.inf
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)


class Test_add_resistance_internal_config:
    """Placeholder failing test for variable 'config' of 'add_resistance_internal'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: config of add_resistance_internal")


class Test_add_resistance_internal_verbose:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["verbose"] = True
        result = add_resistance_internal(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_resistance_internal.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_resistance_internal.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["verbose"] = False
        result = add_resistance_internal(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_resistance_internal.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_resistance_internal.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["verbose"] = None
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)

    def test_wrong_type(self, base_args):
        base_args["verbose"] = "wrong type"
        assert not isinstance(base_args["verbose"], bool)
        assert_raises_and_print(ValueError, add_resistance_internal, **base_args)
