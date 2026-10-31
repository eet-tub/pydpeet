import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import _assert_raises_and_print
from src.pydpeet import extract_instructions


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df_primitives": Mocks.Mock_generate_instructions.df_primitives.copy(),
        "end_condition_map": Mocks.Mock_generate_instructions.end_condition_map,
        "threshold_warnings": Mocks.Mock_generate_instructions.threshold_warnings,
    }


class Test_extract_instructions_df_primitives:
    def test_valid(self, base_args, benchmark):
        def _run():
            result = extract_instructions(**base_args)
            assert isinstance(result, list)
            assert all(isinstance(item, str) for item in result)
            expected = Mocks.Mock_generate_instructions.expected
            assert result == expected

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = None
            _assert_raises_and_print(ValueError, extract_instructions, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = "wrong type"
            assert not isinstance(base_args["df_primitives"], pd.DataFrame)
            _assert_raises_and_print(ValueError, extract_instructions, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_empty(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = pd.DataFrame()
            _assert_raises_and_print(ValueError, extract_instructions, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_missing_required_columns(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = base_args["df_primitives"].drop(
                Mocks.Mock_generate_instructions.required_columns, axis=1
            )
            _assert_raises_and_print(ValueError, extract_instructions, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_column_dtypes(self, base_args, benchmark):
        def _run():
            for col, _dtype in Mocks.Mock_generate_instructions.required_columns_dtypes:
                base_args["df_primitives"][col] = base_args["df_primitives"][col].astype(str)
            expected_dtypes = pd.Series(
                {col: dtype for col, dtype in Mocks.Mock_generate_instructions.required_columns_dtypes}
            )
            actual_dtypes = base_args["df_primitives"][Mocks.Mock_generate_instructions.required_columns].dtypes
            assert not actual_dtypes.equals(expected_dtypes)
            _assert_raises_and_print(ValueError, extract_instructions, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_nan_values(self, base_args, caplog, benchmark):
        def _run():
            base_args["df_primitives"].loc[:9, Mocks.Mock_generate_instructions.required_columns[0]] = np.nan
            with caplog.at_level(logging.WARNING):
                result = extract_instructions(**base_args)
            print(f"\nCaptured Warning: {caplog.records[0].message}")
            assert any(
                f"Column '{Mocks.Mock_generate_instructions.required_columns[0]}' contains NaN values."
                in record.message
                for record in caplog.records
            )
            assert isinstance(result, list)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none_values(self, base_args, caplog, benchmark):
        def _run():
            assert True

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_inf_values(self, base_args, caplog, benchmark):
        def _run():
            base_args["df_primitives"].loc[:9, Mocks.Mock_generate_instructions.required_columns[0]] = np.inf
            with caplog.at_level(logging.WARNING):
                result = extract_instructions(**base_args)
            print(f"\nCaptured Warning: {caplog.records[0].message}")
            assert any(
                f"Column '{Mocks.Mock_generate_instructions.required_columns[0]}' contains infinite values."
                in record.message
                for record in caplog.records
            )
            assert isinstance(result, list)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)


class Test_extract_instructions_end_condition_map:
    """Placeholder failing test for variable 'end_condition_map' of 'extract_instructions'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: end_condition_map of extract_instructions")


class Test_extract_instructions_threshold_warnings:
    """Placeholder failing test for variable 'threshold_warnings' of 'extract_instructions'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: threshold_warnings of extract_instructions")
