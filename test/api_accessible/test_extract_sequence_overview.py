import logging
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import _assert_raises_and_print
from src.pydpeet import extract_sequence_overview


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df_primitives": Mocks.Mock_extract_sequence_overview.df_primitives.copy(),
        "config": replace(Mocks.Mock_extract_sequence_overview.config),
    }


class Test_extract_sequence_overview_df_primitives:
    # Only first test
    def test_valid(self, base_args):
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)
        # Compare with expected result
        expected = Mocks.Mock_extract_sequence_overview.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["df_primitives"] = None
        _assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df_primitives"] = "wrong type"
        assert not isinstance(base_args["df_primitives"], pd.DataFrame)
        _assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_empty(self, base_args):
        base_args["df_primitives"] = pd.DataFrame()
        _assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df_primitives"] = base_args["df_primitives"].drop(
            Mocks.Mock_extract_sequence_overview.required_columns, axis=1
        )
        _assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        for col, _dtype in Mocks.Mock_extract_sequence_overview.required_columns_dtypes:
            base_args["df_primitives"][col] = base_args["df_primitives"][col].astype(str)
        expected_dtypes = pd.Series(
            {col: dtype for col, dtype in Mocks.Mock_extract_sequence_overview.required_columns_dtypes}
        )
        actual_dtypes = base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        _assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["df_primitives"].loc[:9, Mocks.Mock_extract_sequence_overview.required_columns[0]] = np.nan
        with caplog.at_level(logging.WARNING):
            result = extract_sequence_overview(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_extract_sequence_overview.required_columns[0]}' contains NaN values."
            in record.message
            for record in caplog.records
        )
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        base_args["df_primitives"].loc[:9, Mocks.Mock_extract_sequence_overview.required_columns[0]] = np.inf
        with caplog.at_level(logging.WARNING):
            result = extract_sequence_overview(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_extract_sequence_overview.required_columns[0]}' contains infinite values."
            in record.message
            for record in caplog.records
        )
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)


class Test_extract_sequence_overview_config:
    def test_valid(self, base_args):
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)
        expected = Mocks.Mock_extract_sequence_overview.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["config"] = None
        _assert_raises_and_print(AttributeError, extract_sequence_overview, **base_args)

    def test_wrong_type(self, base_args):
        base_args["config"] = "wrong type"
        assert not isinstance(base_args["config"], dict)
        _assert_raises_and_print(AttributeError, extract_sequence_overview, **base_args)

    def test_show_runtime_true(self, base_args):
        base_args["config"].show_runtime = True
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)
        expected = Mocks.Mock_extract_sequence_overview.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_show_runtime_false(self, base_args):
        base_args["config"].show_runtime = False
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)
        expected = Mocks.Mock_extract_sequence_overview.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_show_runtime_none(self, base_args):
        base_args["config"].show_runtime = None
        _assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_show_runtime_wrong_type(self, base_args):
        base_args["config"].show_runtime = "wrong type"
        assert not isinstance(base_args["config"].show_runtime, bool)
        _assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)
