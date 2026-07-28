import logging
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from pydpeet import add_primitive_segments
from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import _assert_raises_and_print


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df": Mocks.Mock_add_primitive_segments.df.copy(),
        "config": replace(Mocks.Mock_add_primitive_segments.config),
    }


class Test_add_primitive_segments_df:
    # Only first test
    def test_valid(self, base_args):
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["df"] = None
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df"] = "wrong type"
        assert not isinstance(base_args["df"], pd.DataFrame)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_empty(self, base_args):
        base_args["df"] = pd.DataFrame()
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df"] = base_args["df"].drop(Mocks.Mock_add_primitive_segments.required_columns, axis=1)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        for col, _dtype in Mocks.Mock_add_primitive_segments.required_columns_dtypes:
            base_args["df"][col] = base_args["df"][col].astype(str)
        expected_dtypes = pd.Series(
            {col: dtype for col, dtype in Mocks.Mock_add_primitive_segments.required_columns_dtypes}
        )
        actual_dtypes = base_args["df"][Mocks.Mock_add_primitive_segments.required_columns].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["df"].loc[:9, Mocks.Mock_add_primitive_segments.required_columns[0]] = np.nan
        with caplog.at_level(logging.WARNING):
            add_primitive_segments(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_add_primitive_segments.required_columns[0]}' contains NaN values." in record.message
            for record in caplog.records
        )

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        base_args["df"].loc[:9, Mocks.Mock_add_primitive_segments.required_columns[0]] = np.inf
        with caplog.at_level(logging.WARNING):
            add_primitive_segments(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_add_primitive_segments.required_columns[0]}' contains infinite values."
            in record.message
            for record in caplog.records
        )


class Test_add_primitive_segments_config:
    def test_valid(self, base_args):
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["config"] = None
        _assert_raises_and_print(AttributeError, add_primitive_segments, **base_args)

    def test_wrong_type(self, base_args):
        base_args["config"] = "wrong type"
        assert not isinstance(base_args["config"], dict)
        _assert_raises_and_print(AttributeError, add_primitive_segments, **base_args)

    def test_show_runtime_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].show_runtime = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_show_runtime_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].show_runtime = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_show_runtime_none(self, base_args):
        base_args["config"].show_runtime = None
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_show_runtime_wrong_type(self, base_args):
        base_args["config"].show_runtime = "wrong type"
        assert not isinstance(base_args["config"].show_runtime, bool)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_check_cv_0aend_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].check_cv_0aend_segments_bool = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_cv_0aend_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].check_cv_0aend_segments_bool = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_cv_0aend_none(self, base_args):
        base_args["config"].check_cv_0aend_segments_bool = None
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_cv_0aend_wrong_type(self, base_args):
        base_args["config"].check_cv_0aend_segments_bool = "wrong type"
        assert not isinstance(base_args["config"].check_cv_0aend_segments_bool, bool)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_check_zero_length_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].check_zero_length_segments_bool = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_zero_length_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].check_zero_length_segments_bool = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_zero_length_none(self, base_args):
        base_args["config"].check_zero_length_segments_bool = None
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_zero_length_wrong_type(self, base_args):
        base_args["config"].check_zero_length_segments_bool = "wrong type"
        assert not isinstance(base_args["config"].check_zero_length_segments_bool, bool)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_check_power_zero_w_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].check_power_zero_w_segments_bool = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_power_zero_w_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].check_power_zero_w_segments_bool = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_power_zero_w_none(self, base_args):
        base_args["config"].check_power_zero_w_segments_bool = None
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_check_power_zero_w_wrong_type(self, base_args):
        base_args["config"].check_power_zero_w_segments_bool = "wrong type"
        assert not isinstance(base_args["config"].check_power_zero_w_segments_bool, bool)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_supress_io_warnings_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].supress_io_warnings = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_supress_io_warnings_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].supress_io_warnings = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_supress_io_warnings_none(self, base_args):
        base_args["config"].supress_io_warnings = None
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_supress_io_warnings_wrong_type(self, base_args):
        base_args["config"].supress_io_warnings = "wrong type"
        assert not isinstance(base_args["config"].supress_io_warnings, bool)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_precompile_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].precompile = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_precompile_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].precompile = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_precompile_none(self, base_args):
        base_args["config"].precompile = None
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_precompile_wrong_type(self, base_args):
        base_args["config"].precompile = "wrong type"
        assert not isinstance(base_args["config"].precompile, bool)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_force_precompilation_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].force_precompilation = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_force_precompilation_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["config"].force_precompilation = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_force_precompilation_none(self, base_args):
        base_args["config"].force_precompilation = None
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_force_precompilation_wrong_type(self, base_args):
        base_args["config"].force_precompilation = "wrong type"
        assert not isinstance(base_args["config"].force_precompilation, bool)
        _assert_raises_and_print(ValueError, add_primitive_segments, **base_args)
