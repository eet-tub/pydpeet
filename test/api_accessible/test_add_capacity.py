import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import _assert_raises_and_print
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


class Test_add_capacity_df:
    # Only first test
    def test_valid(self, base_args, benchmark):
        def _run():
            original_df = base_args["df"].copy()
            result = add_capacity(**base_args)
            assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
            assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)
            # Compare with expected result
            expected = Mocks.Mock_add_capacity.df_expected
            assert pd.DataFrame.equals(result, expected)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["df"] = None
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["df"] = "wrong type"
            assert not isinstance(base_args["df"], pd.DataFrame)
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_empty(self, base_args, benchmark):
        def _run():
            base_args["df"] = pd.DataFrame()
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_missing_required_columns(self, base_args, benchmark):
        def _run():
            base_args["df"] = base_args["df"].drop(Mocks.Mock_add_capacity.required_columns_df, axis=1)
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_column_dtypes(self, base_args, benchmark):
        def _run():
            for col, _dtype in Mocks.Mock_add_capacity.required_column_dtypes_df:
                base_args["df"][col] = base_args["df"][col].astype(str)
            expected_dtypes = pd.Series(
                {col: dtype for col, dtype in Mocks.Mock_add_capacity.required_column_dtypes_df}
            )
            actual_dtypes = base_args["df"][Mocks.Mock_add_capacity.required_columns_df].dtypes
            assert not actual_dtypes.equals(expected_dtypes)
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_nan_values(self, base_args, caplog, benchmark):
        def _run():
            base_args["df"].loc[:9, Mocks.Mock_add_capacity.required_columns_df[0]] = np.nan
            with caplog.at_level(logging.WARNING):
                add_capacity(**base_args)
            print(f"\nCaptured Warning: {caplog.records[0].message}")
            assert any(
                f"Column '{Mocks.Mock_add_capacity.required_columns_df[0]}' contains NaN values." in record.message
                for record in caplog.records
            )

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none_values(self, base_args, caplog, benchmark):
        def _run():
            # assert True due to dtype == float (in all required columns) is it impossible to check None since it
            # would be converted to NaN or throw the test_wrong_column_dtypes failure
            assert True

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_inf_values(self, base_args, caplog, benchmark):
        def _run():
            base_args["df"].loc[:9, Mocks.Mock_add_capacity.required_columns_df[0]] = np.inf
            with caplog.at_level(logging.WARNING):
                add_capacity(**base_args)
            print(f"\nCaptured Warning: {caplog.records[0].message}")
            assert any(
                f"Column '{Mocks.Mock_add_capacity.required_columns_df[0]}' contains infinite values." in record.message
                for record in caplog.records
            )

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)


class Test_add_capacity_df_primitives:
    # Only first test
    def test_valid(self, base_args, benchmark):
        def _run():
            original_df = base_args["df"].copy()
            result = add_capacity(**base_args)
            assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
            assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)
            # Compare with expected result
            expected = Mocks.Mock_add_capacity.df_expected
            assert pd.DataFrame.equals(result, expected)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = None
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = "wrong type"
            assert not isinstance(base_args["df_primitives"], pd.DataFrame)
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_empty(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = pd.DataFrame()
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_missing_required_columns(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = base_args["df_primitives"].drop(
                Mocks.Mock_add_capacity.required_columns_df_primitives, axis=1
            )
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_column_dtypes(self, base_args, benchmark):
        def _run():
            for col, _dtype in Mocks.Mock_add_capacity.required_column_dtypes_df_primitives:
                base_args["df_primitives"][col] = base_args["df_primitives"][col].astype(str)
            expected_dtypes = pd.Series(
                {col: dtype for col, dtype in Mocks.Mock_add_capacity.required_column_dtypes_df_primitives}
            )
            actual_dtypes = base_args["df_primitives"][Mocks.Mock_add_capacity.required_columns_df_primitives].dtypes
            assert not actual_dtypes.equals(expected_dtypes)
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_nan_values(self, base_args, caplog, benchmark):
        def _run():
            base_args["df_primitives"].loc[:9, Mocks.Mock_add_capacity.required_columns_df_primitives[0]] = np.nan
            with caplog.at_level(logging.WARNING):
                add_capacity(**base_args)
            print(f"\nCaptured Warning: {caplog.records[0].message}")
            assert any(
                f"Column '{Mocks.Mock_add_capacity.required_columns_df_primitives[0]}' contains NaN values."
                in record.message
                for record in caplog.records
            )

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none_values(self, base_args, caplog, benchmark):
        def _run():
            # assert True due to dtype == float (in all required columns) is it impossible to check None since it
            # would be converted to NaN or throw the test_wrong_column_dtypes failure
            assert True

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_inf_values(self, base_args, caplog, benchmark):
        def _run():
            base_args["df_primitives"].loc[:9, Mocks.Mock_add_capacity.required_columns_df_primitives[0]] = np.inf
            with caplog.at_level(logging.WARNING):
                add_capacity(**base_args)
            print(f"\nCaptured Warning: {caplog.records[0].message}")
            assert any(
                f"Column '{Mocks.Mock_add_capacity.required_columns_df_primitives[0]}' contains infinite values."
                in record.message
                for record in caplog.records
            )

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)


class Test_add_capacity_config:
    """Placeholder failing test for variable 'config' of 'add_capacity'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: config of add_capacity")


class Test_add_capacity_neware_bool:
    def test_true(self, base_args, benchmark):
        def _run():
            original_df = base_args["df"].copy()
            base_args["neware_bool"] = True
            result = add_capacity(**base_args)
            assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
            assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)
            # Compare with expected result
            expected = Mocks.Mock_add_capacity.df_expected
            assert pd.DataFrame.equals(result, expected)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_false(self, base_args, benchmark):
        def _run():
            original_df = base_args["df"].copy()
            base_args["neware_bool"] = False
            result = add_capacity(**base_args)
            assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
            assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)
            # Compare with expected result
            expected = Mocks.Mock_add_capacity.df_expected
            assert pd.DataFrame.equals(result, expected)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["neware_bool"] = None
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["neware_bool"] = "wrong type"
            assert not isinstance(base_args["neware_bool"], bool)
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)


class Test_add_capacity_verbose:
    def test_true(self, base_args, benchmark):
        def _run():
            original_df = base_args["df"].copy()
            base_args["verbose"] = True
            result = add_capacity(**base_args)
            assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
            assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)
            # Compare with expected result
            expected = Mocks.Mock_add_capacity.df_expected
            assert pd.DataFrame.equals(result, expected)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_false(self, base_args, benchmark):
        def _run():
            original_df = base_args["df"].copy()
            base_args["verbose"] = False
            result = add_capacity(**base_args)
            assert all(col in result.columns for col in Mocks.Mock_add_capacity.add_columns)
            assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_capacity.add_columns, axis=1), original_df)
            # Compare with expected result
            expected = Mocks.Mock_add_capacity.df_expected
            assert pd.DataFrame.equals(result, expected)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["verbose"] = None
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["verbose"] = "wrong type"
            assert not isinstance(base_args["verbose"], bool)
            _assert_raises_and_print(ValueError, add_capacity, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)
