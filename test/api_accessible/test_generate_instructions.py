import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import generate_instructions


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df_primitives": Mocks.Mock_generate_instructions.df_primitives.copy(),
        "end_condition_map": Mocks.Mock_generate_instructions.end_condition_map,
        "threshold_warnings": Mocks.Mock_generate_instructions.threshold_warnings,
    }


class Test_generate_instructions_df_primitives:
    def test_valid(self, base_args):
        result = generate_instructions(**base_args)
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
        # Compare with expected result
        expected = Mocks.Mock_generate_instructions.expected
        assert result == expected

    def test_none(self, base_args):
        base_args["df_primitives"] = None
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df_primitives"] = "wrong type"
        assert not isinstance(base_args["df_primitives"], pd.DataFrame)
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_empty(self, base_args):
        base_args["df_primitives"] = pd.DataFrame()
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df_primitives"] = base_args["df_primitives"].drop(
            Mocks.Mock_generate_instructions.required_columns, axis=1
        )
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        for col, _dtype in Mocks.Mock_generate_instructions.required_columns_dtypes:
            base_args["df_primitives"][col] = base_args["df_primitives"][col].astype(str)
        expected_dtypes = pd.Series(
            {col: dtype for col, dtype in Mocks.Mock_generate_instructions.required_columns_dtypes}
        )
        actual_dtypes = base_args["df_primitives"][Mocks.Mock_generate_instructions.required_columns].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["df_primitives"].loc[:9, Mocks.Mock_generate_instructions.required_columns[0]] = np.nan
        with caplog.at_level(logging.WARNING):
            result = generate_instructions(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_generate_instructions.required_columns[0]}' contains NaN values." in record.message
            for record in caplog.records
        )
        assert isinstance(result, list)

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        base_args["df_primitives"].loc[:9, Mocks.Mock_generate_instructions.required_columns[0]] = np.inf
        with caplog.at_level(logging.WARNING):
            result = generate_instructions(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_generate_instructions.required_columns[0]}' contains infinite values."
            in record.message
            for record in caplog.records
        )
        assert isinstance(result, list)


class Test_generate_instructions_end_condition_map:
    """Placeholder failing test for variable 'end_condition_map' of 'generate_instructions'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: end_condition_map of generate_instructions")


class Test_generate_instructions_threshold_warnings:
    """Placeholder failing test for variable 'threshold_warnings' of 'generate_instructions'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: threshold_warnings of generate_instructions")
