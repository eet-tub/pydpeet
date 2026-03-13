import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
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
    # Only first test
    def test_valid(self, base_args):
        raise NotImplementedError(
            "Test not implemented for variable: df_segments_and_sequences of filter_and_split_df_by_blocks"
        )
        original_df = base_args["VARIABLE"].copy()
        result = filter_and_split_df_by_blocks(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_filter_and_split_df_by_blocks.add_columns)
        assert pd.DataFrame.equals(
            result.drop(Mocks.Mock_filter_and_split_df_by_blocks.add_columns, axis=1), original_df
        )

    def test_none(self, base_args):
        base_args["VARIABLE"] = None
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_wrong_type(self, base_args):
        base_args["VARIABLE"] = "wrong type"
        assert not isinstance(base_args["VARIABLE"], pd.DataFrame)
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_empty(self, base_args):
        base_args["VARIABLE"] = pd.DataFrame()
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["VARIABLE"] = base_args["VARIABLE"].drop(Mocks.Mock_filter_and_split_df_by_blocks.required_columns)
        assert_raises_and_print(KeyError, filter_and_split_df_by_blocks, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns] = base_args["VARIABLE"][
            Mocks.Mock_filter_and_split_df_by_blocks.required_columns
        ].astype(int)
        assert (
            base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns].dtypes
            != Mocks.Mock_filter_and_split_df_by_blocks.required_columns_dtypes
        )
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_nan_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns] = np.nan
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_none_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns] = None
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_inf_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns] = np.inf
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)


class Test_filter_and_split_df_by_blocks_df_primitives:
    # Only first test
    def test_valid(self, base_args):
        raise NotImplementedError(
            "Test not implemented for variable: df_segments_and_sequences of filter_and_split_df_by_blocks"
        )
        original_df = base_args["VARIABLE"].copy()
        result = filter_and_split_df_by_blocks(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_filter_and_split_df_by_blocks.add_columns)
        assert pd.DataFrame.equals(
            result.drop(Mocks.Mock_filter_and_split_df_by_blocks.add_columns, axis=1), original_df
        )

    def test_none(self, base_args):
        base_args["VARIABLE"] = None
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_wrong_type(self, base_args):
        base_args["VARIABLE"] = "wrong type"
        assert not isinstance(base_args["VARIABLE"], pd.DataFrame)
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_empty(self, base_args):
        base_args["VARIABLE"] = pd.DataFrame()
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["VARIABLE"] = base_args["VARIABLE"].drop(Mocks.Mock_filter_and_split_df_by_blocks.required_columns)
        assert_raises_and_print(KeyError, filter_and_split_df_by_blocks, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns] = base_args["VARIABLE"][
            Mocks.Mock_filter_and_split_df_by_blocks.required_columns
        ].astype(int)
        assert (
            base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns].dtypes
            != Mocks.Mock_filter_and_split_df_by_blocks.required_columns_dtypes
        )
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_nan_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns] = np.nan
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_none_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns] = None
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_inf_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_filter_and_split_df_by_blocks.required_columns] = np.inf
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)


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
    def test_true(self, base_args):
        raise NotImplementedError(
            "Test not implemented for variable: df_segments_and_sequences of filter_and_split_df_by_blocks"
        )
        original_df = base_args["df"].copy()
        base_args["VARIABLE"] = True
        result = filter_and_split_df_by_blocks(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_filter_and_split_df_by_blocks.add_columns)
        assert pd.DataFrame.equals(
            result.drop(Mocks.Mock_filter_and_split_df_by_blocks.add_columns, axis=1), original_df
        )

    def test_false(self, base_args):
        raise NotImplementedError(
            "Test not implemented for variable: df_segments_and_sequences of filter_and_split_df_by_blocks"
        )
        original_df = base_args["df"].copy()
        base_args["VARIABLE"] = False
        result = filter_and_split_df_by_blocks(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_filter_and_split_df_by_blocks.add_columns)
        assert pd.DataFrame.equals(
            result.drop(Mocks.Mock_filter_and_split_df_by_blocks.add_columns, axis=1), original_df
        )

    def test_none(self, base_args):
        base_args["VARIABLE"] = None
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_wrong_type(self, base_args):
        base_args["VARIABLE"] = "wrong type"
        assert not isinstance(base_args["VARIABLE"], bool)
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)


class Test_filter_and_split_df_by_blocks_also_return_filtered_df:
    def test_true(self, base_args):
        raise NotImplementedError(
            "Test not implemented for variable: df_segments_and_sequences of filter_and_split_df_by_blocks"
        )
        original_df = base_args["df"].copy()
        base_args["VARIABLE"] = True
        result = filter_and_split_df_by_blocks(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_filter_and_split_df_by_blocks.add_columns)
        assert pd.DataFrame.equals(
            result.drop(Mocks.Mock_filter_and_split_df_by_blocks.add_columns, axis=1), original_df
        )

    def test_false(self, base_args):
        raise NotImplementedError(
            "Test not implemented for variable: df_segments_and_sequences of filter_and_split_df_by_blocks"
        )
        original_df = base_args["df"].copy()
        base_args["VARIABLE"] = False
        result = filter_and_split_df_by_blocks(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_filter_and_split_df_by_blocks.add_columns)
        assert pd.DataFrame.equals(
            result.drop(Mocks.Mock_filter_and_split_df_by_blocks.add_columns, axis=1), original_df
        )

    def test_none(self, base_args):
        base_args["VARIABLE"] = None
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)

    def test_wrong_type(self, base_args):
        base_args["VARIABLE"] = "wrong type"
        assert not isinstance(base_args["VARIABLE"], bool)
        assert_raises_and_print(ValueError, filter_and_split_df_by_blocks, **base_args)
