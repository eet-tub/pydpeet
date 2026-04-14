import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import extract_ocv_iocv


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "min_pause_lenght": Mocks.Mock_extract_ocv_iocv.min_pause_lenght,
        "min_loops": Mocks.Mock_extract_ocv_iocv.min_loops,
        "visualize": Mocks.Mock_extract_ocv_iocv.visualize,
        "df_primitives": Mocks.Mock_extract_ocv_iocv.df_primitives.copy(),
        "df": Mocks.Mock_extract_ocv_iocv.df.copy(),
        "config": Mocks.Mock_extract_ocv_iocv.config,
    }


class Test_extract_ocv_iocv_min_pause_lenght:
    """Placeholder failing test for variable 'min_pause_lenght' of 'extract_ocv_iocv'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: min_pause_lenght of extract_ocv_iocv")


class Test_extract_ocv_iocv_min_loops:
    """Placeholder failing test for variable 'min_loops' of 'extract_ocv_iocv'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: min_loops of extract_ocv_iocv")


class Test_extract_ocv_iocv_visualize:
    """Placeholder failing test for variable 'visualize' of 'extract_ocv_iocv'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: visualize of extract_ocv_iocv")


class Test_extract_ocv_iocv_df_primitives:
    def test_valid(self, base_args):
        base_args["df"] = None  # Only use df_primitives
        result = extract_ocv_iocv(**base_args)
        assert isinstance(result, list)
        assert len(result) == len(Mocks.Mock_extract_ocv_iocv.expected_ocv_iocv)
        for i, expected_df in enumerate(Mocks.Mock_extract_ocv_iocv.expected_ocv_iocv):
            pd.testing.assert_frame_equal(result[i], expected_df)

    def test_none(self, base_args):
        base_args["df"] = None
        base_args["df_primitives"] = None
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df"] = None
        base_args["df_primitives"] = "wrong type"
        assert not isinstance(base_args["df_primitives"], pd.DataFrame)
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_empty(self, base_args):
        base_args["df"] = None
        base_args["df_primitives"] = pd.DataFrame()
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df"] = None
        base_args["df_primitives"] = base_args["df_primitives"].drop(
            Mocks.Mock_extract_ocv_iocv.required_columns_df_primitives, axis=1
        )
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df"] = None
        for col, _dtype in Mocks.Mock_extract_ocv_iocv.required_columns_dtypes_df_primitives:
            base_args["df_primitives"][col] = base_args["df_primitives"][col].astype(str)
        expected_dtypes = pd.Series(
            {col: dtype for col, dtype in Mocks.Mock_extract_ocv_iocv.required_columns_dtypes_df_primitives}
        )
        actual_dtypes = base_args["df_primitives"][Mocks.Mock_extract_ocv_iocv.required_columns_df_primitives].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["df"] = None
        base_args["df_primitives"].loc[:9, Mocks.Mock_extract_ocv_iocv.required_columns_df_primitives[0]] = np.nan
        with caplog.at_level(logging.WARNING):
            extract_ocv_iocv(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_extract_ocv_iocv.required_columns_df_primitives[0]}' contains NaN values."
            in record.message
            for record in caplog.records
        )

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        base_args["df"] = None
        base_args["df_primitives"].loc[:9, Mocks.Mock_extract_ocv_iocv.required_columns_df_primitives[0]] = np.inf
        with caplog.at_level(logging.WARNING):
            extract_ocv_iocv(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_extract_ocv_iocv.required_columns_df_primitives[0]}' contains infinite values."
            in record.message
            for record in caplog.records
        )


class Test_extract_ocv_iocv_df:
    def test_valid(self, base_args):
        base_args["df_primitives"] = None  # Only use df
        result = extract_ocv_iocv(**base_args)
        assert isinstance(result, list)
        assert len(result) == len(Mocks.Mock_extract_ocv_iocv.expected_ocv_iocv)
        for i, expected_df in enumerate(Mocks.Mock_extract_ocv_iocv.expected_ocv_iocv):
            pd.testing.assert_frame_equal(result[i], expected_df)

    def test_none(self, base_args):
        base_args["df_primitives"] = None
        base_args["df"] = None
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df_primitives"] = None
        base_args["df"] = "wrong type"
        assert not isinstance(base_args["df"], pd.DataFrame)
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_empty(self, base_args):
        base_args["df_primitives"] = None
        base_args["df"] = pd.DataFrame()
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df_primitives"] = None
        base_args["df"] = base_args["df"].drop(Mocks.Mock_extract_ocv_iocv.required_columns_df, axis=1)
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df_primitives"] = None
        for col, _dtype in Mocks.Mock_extract_ocv_iocv.required_columns_dtypes_df:
            base_args["df"][col] = base_args["df"][col].astype(str)
        expected_dtypes = pd.Series(
            {col: dtype for col, dtype in Mocks.Mock_extract_ocv_iocv.required_columns_dtypes_df}
        )
        actual_dtypes = base_args["df"][Mocks.Mock_extract_ocv_iocv.required_columns_df].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["df_primitives"] = None
        base_args["df"].loc[:9, Mocks.Mock_extract_ocv_iocv.required_columns_df[0]] = np.nan
        with caplog.at_level(logging.WARNING):
            extract_ocv_iocv(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_extract_ocv_iocv.required_columns_df[0]}' contains NaN values." in record.message
            for record in caplog.records
        )

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        base_args["df_primitives"] = None
        base_args["df"].loc[:9, Mocks.Mock_extract_ocv_iocv.required_columns_df[0]] = np.inf
        with caplog.at_level(logging.WARNING):
            extract_ocv_iocv(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_extract_ocv_iocv.required_columns_df[0]}' contains infinite values." in record.message
            for record in caplog.records
        )


class Test_extract_ocv_iocv_config:
    """Placeholder failing test for variable 'config' of 'extract_ocv_iocv'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: config of extract_ocv_iocv")
