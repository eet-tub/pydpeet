import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import add_soc


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {"df": Mocks.Mock_add_soc.df.copy(),
            "df_primitives": Mocks.Mock_add_soc.df_primitives.copy(),
            "neware_bool": Mocks.Mock_add_soc.neware_bool,
            "standard_method": Mocks.Mock_add_soc.standard_method,
            "methods": Mocks.Mock_add_soc.methods,
            "config": Mocks.Mock_add_soc.config,
            "lower_soc_for_voltage": Mocks.Mock_add_soc.lower_soc_for_voltage,
            "upper_soc_for_voltage": Mocks.Mock_add_soc.upper_soc_for_voltage,
            "lower_voltage_for_soc": Mocks.Mock_add_soc.lower_voltage_for_soc,
            "upper_voltage_for_soc": Mocks.Mock_add_soc.upper_voltage_for_soc,
            "verbose": Mocks.Mock_add_soc.verbose,
            "restart_for_testindex": Mocks.Mock_add_soc.restart_for_testindex
    }


class Test_add_soc_df:
    # Only first test
    def test_valid(self, base_args):
        original_df = base_args["df"].copy()
        result = add_soc(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_soc.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_soc.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["df"] = None
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df"] = "wrong type"
        assert not isinstance(base_args["df"], pd.DataFrame)
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_empty(self, base_args):
        base_args["df"] = pd.DataFrame()
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df"] = base_args["df"].drop(Mocks.Mock_add_soc.required_columns)
        assert_raises_and_print(KeyError, add_soc, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df"][Mocks.Mock_add_soc.required_columns] = base_args["df"][Mocks.Mock_add_soc.required_columns].astype(int)
        assert base_args["df"][Mocks.Mock_add_soc.required_columns].dtypes != Mocks.Mock_add_soc.required_columns_dtypes
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_nan_values(self, base_args):
        base_args["df"][Mocks.Mock_add_soc.required_columns] = np.nan
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_none_values(self, base_args):
        base_args["df"][Mocks.Mock_add_soc.required_columns] = None
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_inf_values(self, base_args):
        base_args["df"][Mocks.Mock_add_soc.required_columns] = np.inf
        assert_raises_and_print(ValueError, add_soc, **base_args)


class Test_add_soc_df_primitives:
    # Only first test
    def test_valid(self, base_args):
        original_df = base_args["df_primitives"].copy()
        result = add_soc(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_soc.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_soc.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["df_primitives"] = None
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df_primitives"] = "wrong type"
        assert not isinstance(base_args["df_primitives"], pd.DataFrame)
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_empty(self, base_args):
        base_args["df_primitives"] = pd.DataFrame()
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df_primitives"] = base_args["df_primitives"].drop(Mocks.Mock_add_soc.required_columns)
        assert_raises_and_print(KeyError, add_soc, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df_primitives"][Mocks.Mock_add_soc.required_columns] = base_args["df_primitives"][Mocks.Mock_add_soc.required_columns].astype(int)
        assert base_args["df_primitives"][Mocks.Mock_add_soc.required_columns].dtypes != Mocks.Mock_add_soc.required_columns_dtypes
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_nan_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_add_soc.required_columns] = np.nan
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_none_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_add_soc.required_columns] = None
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_inf_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_add_soc.required_columns] = np.inf
        assert_raises_and_print(ValueError, add_soc, **base_args)


class Test_add_soc_neware_bool:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["neware_bool"] = True
        result = add_soc(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_soc.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_soc.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["neware_bool"] = False
        result = add_soc(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_soc.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_soc.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["neware_bool"] = None
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_wrong_type(self, base_args):
        base_args["neware_bool"] = "wrong type"
        assert not isinstance(base_args["neware_bool"], bool)
        assert_raises_and_print(ValueError, add_soc, **base_args)


class Test_add_soc_standard_method:
    """Placeholder failing test for variable 'standard_method' of 'add_soc'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: standard_method of add_soc")


class Test_add_soc_methods:
    """Placeholder failing test for variable 'methods' of 'add_soc'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: methods of add_soc")


class Test_add_soc_config:
    """Placeholder failing test for variable 'config' of 'add_soc'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: config of add_soc")


class Test_add_soc_lower_soc_for_voltage:
    """Placeholder failing test for variable 'lower_soc_for_voltage' of 'add_soc'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: lower_soc_for_voltage of add_soc")


class Test_add_soc_upper_soc_for_voltage:
    """Placeholder failing test for variable 'upper_soc_for_voltage' of 'add_soc'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: upper_soc_for_voltage of add_soc")


class Test_add_soc_lower_voltage_for_soc:
    """Placeholder failing test for variable 'lower_voltage_for_soc' of 'add_soc'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: lower_voltage_for_soc of add_soc")


class Test_add_soc_upper_voltage_for_soc:
    """Placeholder failing test for variable 'upper_voltage_for_soc' of 'add_soc'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: upper_voltage_for_soc of add_soc")


class Test_add_soc_verbose:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["verbose"] = True
        result = add_soc(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_soc.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_soc.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["verbose"] = False
        result = add_soc(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_soc.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_soc.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["verbose"] = None
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_wrong_type(self, base_args):
        base_args["verbose"] = "wrong type"
        assert not isinstance(base_args["verbose"], bool)
        assert_raises_and_print(ValueError, add_soc, **base_args)


class Test_add_soc_restart_for_testindex:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["restart_for_testindex"] = True
        result = add_soc(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_soc.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_soc.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["restart_for_testindex"] = False
        result = add_soc(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_soc.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_soc.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["restart_for_testindex"] = None
        assert_raises_and_print(ValueError, add_soc, **base_args)

    def test_wrong_type(self, base_args):
        base_args["restart_for_testindex"] = "wrong type"
        assert not isinstance(base_args["restart_for_testindex"], bool)
        assert_raises_and_print(ValueError, add_soc, **base_args)
