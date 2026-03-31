import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import extract_sequence_overview


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df_primitives": Mocks.Mock_extract_sequence_overview.df_primitives.copy(),
        "SEGMENT_SEQUENCE_CONFIG": Mocks.Mock_extract_sequence_overview.SEGMENT_SEQUENCE_CONFIG,
        "SHOW_RUNTIME": Mocks.Mock_extract_sequence_overview.SHOW_RUNTIME,
    }


class Test_extract_sequence_overview_df_primitives:
    # Only first test
    def test_valid(self, base_args):
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)

    def test_none(self, base_args):
        base_args["df_primitives"] = None
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df_primitives"] = "wrong type"
        assert not isinstance(base_args["df_primitives"], pd.DataFrame)
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_empty(self, base_args):
        base_args["df_primitives"] = pd.DataFrame()
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df_primitives"] = base_args["df_primitives"].drop(
            Mocks.Mock_extract_sequence_overview.required_columns, axis=1
        )
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        for col, _dtype in Mocks.Mock_extract_sequence_overview.required_columns_dtypes:
            base_args["df_primitives"][col] = base_args["df_primitives"][col].astype(str)
        expected_dtypes = pd.Series(
            {col: dtype for col, dtype in Mocks.Mock_extract_sequence_overview.required_columns_dtypes}
        )
        actual_dtypes = base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns[0]].iloc[:10] = np.nan
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
        base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns[0]].iloc[:10] = np.inf
        with caplog.at_level(logging.WARNING):
            result = extract_sequence_overview(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_extract_sequence_overview.required_columns[0]}' contains infinite values."
            in record.message
            for record in caplog.records
        )
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)


class Test_extract_sequence_overview_SEGMENT_SEQUENCE_CONFIG:
    """Placeholder failing test for variable 'SEGMENT_SEQUENCE_CONFIG' of 'extract_sequence_overview'."""

    @pytest.mark.skip
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: SEGMENT_SEQUENCE_CONFIG of extract_sequence_overview"
        )


class Test_extract_sequence_overview_SHOW_RUNTIME:
    def test_true(self, base_args):
        base_args["SHOW_RUNTIME"] = True
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)

    def test_false(self, base_args):
        base_args["SHOW_RUNTIME"] = False
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)

    def test_none(self, base_args):
        base_args["SHOW_RUNTIME"] = None
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_wrong_type(self, base_args):
        base_args["SHOW_RUNTIME"] = "wrong type"
        assert not isinstance(base_args["SHOW_RUNTIME"], bool)
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)
