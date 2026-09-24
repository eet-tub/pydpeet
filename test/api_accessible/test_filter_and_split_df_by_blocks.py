import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import _assert_raises_and_print
from src.pydpeet import filter_and_split_df_by_blocks


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df_segments_and_sequences": Mocks.Mock_filter_and_split_df_by_blocks.df_segments_and_sequences.copy(),
        "df_primitives": Mocks.Mock_filter_and_split_df_by_blocks.df_primitives.copy(),
        "rules": Mocks.Mock_filter_and_split_df_by_blocks.rules,
        "combine_op": Mocks.Mock_filter_and_split_df_by_blocks.combine_op,
        "print_blocks": Mocks.Mock_filter_and_split_df_by_blocks.print_blocks,
        "also_return_filtered_df": Mocks.Mock_filter_and_split_df_by_blocks.also_return_filtered_df,
    }


class Test_filter_and_split_df_by_blocks_df_segments_and_sequences:
    def test_valid(self, base_args, benchmark):
        def _run():
            result = filter_and_split_df_by_blocks(**base_args)
            expected_dfs_per_block = Mocks.Mock_filter_and_split_df_by_blocks.expected_dfs_per_block
            expected_df_filtered = Mocks.Mock_filter_and_split_df_by_blocks.expected_df_filtered.copy()
            assert isinstance(result, tuple)
            assert len(result) == 2
            dfs_per_block, df_filtered = result
            assert len(dfs_per_block) == len(expected_dfs_per_block)
            for i, expected_df in enumerate(expected_dfs_per_block):
                pd.testing.assert_frame_equal(dfs_per_block[i], expected_df)
            pd.testing.assert_frame_equal(df_filtered, expected_df_filtered)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["df_segments_and_sequences"] = None
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["df_segments_and_sequences"] = "wrong type"
            assert not isinstance(base_args["df_segments_and_sequences"], pd.DataFrame)
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_empty(self, base_args, benchmark):
        def _run():
            base_args["df_segments_and_sequences"] = pd.DataFrame()
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_missing_required_columns(self, base_args, benchmark):
        def _run():
            base_args["df_segments_and_sequences"] = base_args["df_segments_and_sequences"].drop(
                Mocks.Mock_filter_and_split_df_by_blocks.required_columns_df_segments, axis=1
            )
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_column_dtypes(self, base_args, benchmark):
        def _run():
            for col, _dtype in Mocks.Mock_filter_and_split_df_by_blocks.required_columns_dtypes_df_segments:
                base_args["df_segments_and_sequences"][col] = base_args["df_segments_and_sequences"][col].astype(str)
            expected_dtypes = pd.Series(
                {
                    col: dtype
                    for col, dtype in Mocks.Mock_filter_and_split_df_by_blocks.required_columns_dtypes_df_segments
                }
            )
            actual_dtypes = base_args["df_segments_and_sequences"][
                Mocks.Mock_filter_and_split_df_by_blocks.required_columns_df_segments
            ].dtypes
            assert not actual_dtypes.equals(expected_dtypes)
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_nan_values(self, base_args, caplog, benchmark):
        def _run():
            # Skip - df_segments_and_sequences has no float columns to test NaN on
            assert True

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none_values(self, base_args, caplog, benchmark):
        def _run():
            # assert True due to dtype == int (in all required columns) is it impossible to check None since it
            # would be converted to NaN or throw the test_wrong_column_dtypes failure
            assert True

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_inf_values(self, base_args, caplog, benchmark):
        def _run():
            # Skip - df_segments_and_sequences has no float columns to test inf on
            assert True

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)


class Test_filter_and_split_df_by_blocks_df_primitives:
    def test_valid(self, base_args, benchmark):
        def _run():
            result = filter_and_split_df_by_blocks(**base_args)
            expected_dfs_per_block = Mocks.Mock_filter_and_split_df_by_blocks.expected_dfs_per_block
            expected_df_filtered = Mocks.Mock_filter_and_split_df_by_blocks.expected_df_filtered.copy()
            assert isinstance(result, tuple)
            assert len(result) == 2
            dfs_per_block, df_filtered = result
            assert len(dfs_per_block) == len(expected_dfs_per_block)
            for i, expected_df in enumerate(expected_dfs_per_block):
                pd.testing.assert_frame_equal(dfs_per_block[i], expected_df)
            pd.testing.assert_frame_equal(df_filtered, expected_df_filtered)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = None
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = "wrong type"
            assert not isinstance(base_args["df_primitives"], pd.DataFrame)
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_empty(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = pd.DataFrame()
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_missing_required_columns(self, base_args, benchmark):
        def _run():
            base_args["df_primitives"] = base_args["df_primitives"].drop(
                Mocks.Mock_filter_and_split_df_by_blocks.required_columns_df_primitives, axis=1
            )
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_column_dtypes(self, base_args, benchmark):
        def _run():
            for col, _dtype in Mocks.Mock_filter_and_split_df_by_blocks.required_columns_dtypes_df_primitives:
                base_args["df_primitives"][col] = base_args["df_primitives"][col].astype(str)
            expected_dtypes = pd.Series(
                {
                    col: dtype
                    for col, dtype in Mocks.Mock_filter_and_split_df_by_blocks.required_columns_dtypes_df_primitives
                }
            )
            actual_dtypes = base_args["df_primitives"][
                Mocks.Mock_filter_and_split_df_by_blocks.required_columns_df_primitives
            ].dtypes
            assert not actual_dtypes.equals(expected_dtypes)
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_nan_values(self, base_args, caplog, benchmark):
        def _run():
            col = Mocks.Mock_filter_and_split_df_by_blocks.nan_inf_test_column_df_primitives
            base_args["df_primitives"] = base_args["df_primitives"].copy()
            base_args["df_primitives"].loc[base_args["df_primitives"].index[:10], col] = np.nan
            with caplog.at_level(logging.WARNING):
                filter_and_split_df_by_blocks(**base_args)
            print(f"\nCaptured Warning: {caplog.records[0].message if caplog.records else 'None'}")
            assert any(f"Column '{col}' contains NaN values." in record.message for record in caplog.records)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none_values(self, base_args, caplog, benchmark):
        def _run():
            # assert True due to dtype == int (in all required columns) is it impossible to check None since it
            # would be converted to NaN or throw the test_wrong_column_dtypes failure
            assert True

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_inf_values(self, base_args, caplog, benchmark):
        def _run():
            col = Mocks.Mock_filter_and_split_df_by_blocks.nan_inf_test_column_df_primitives
            base_args["df_primitives"] = base_args["df_primitives"].copy()
            base_args["df_primitives"].loc[base_args["df_primitives"].index[:10], col] = np.inf
            with caplog.at_level(logging.WARNING):
                filter_and_split_df_by_blocks(**base_args)
            print(f"\nCaptured Warning: {caplog.records[0].message if caplog.records else 'None'}")
            assert any(f"Column '{col}' contains infinite values." in record.message for record in caplog.records)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)


class Test_filter_and_split_df_by_blocks_rules:
    """Placeholder failing test for variable 'rules' of 'filter_and_split_df_by_blocks'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: rules of filter_and_split_df_by_blocks")


class Test_filter_and_split_df_by_blocks_combine_op:
    """Placeholder failing test for variable 'combine_op' of 'filter_and_split_df_by_blocks'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: combine_op of filter_and_split_df_by_blocks")


class Test_filter_and_split_df_by_blocks_print_blocks:
    def test_true(self, base_args, benchmark):
        def _run():
            base_args["print_blocks"] = True
            result = filter_and_split_df_by_blocks(**base_args)
            assert isinstance(result, tuple)
            assert len(result) == 2

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_false(self, base_args, benchmark):
        def _run():
            base_args["print_blocks"] = False
            result = filter_and_split_df_by_blocks(**base_args)
            assert isinstance(result, tuple)
            assert len(result) == 2

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["print_blocks"] = None
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["print_blocks"] = "wrong type"
            assert not isinstance(base_args["print_blocks"], bool)
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)


class Test_filter_and_split_df_by_blocks_also_return_filtered_df:
    def test_true(self, base_args, benchmark):
        def _run():
            base_args["also_return_filtered_df"] = True
            result = filter_and_split_df_by_blocks(**base_args)
            assert isinstance(result, tuple)
            assert len(result) == 2
            dfs_per_block, df_filtered = result
            assert isinstance(dfs_per_block, list)
            assert isinstance(df_filtered, pd.DataFrame)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_false(self, base_args, benchmark):
        def _run():
            base_args["also_return_filtered_df"] = False
            result = filter_and_split_df_by_blocks(**base_args)
            assert isinstance(result, list)
            assert not isinstance(result, tuple)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["also_return_filtered_df"] = None
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["also_return_filtered_df"] = "wrong type"
            assert not isinstance(base_args["also_return_filtered_df"], bool)
            _assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)
