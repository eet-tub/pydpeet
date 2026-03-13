import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import merge_into_series


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df_list": Mocks.Mock_merge_into_series.df_list,
        "time_between_tests_seconds": Mocks.Mock_merge_into_series.time_between_tests_seconds,
        "verbose": Mocks.Mock_merge_into_series.verbose,
        "sort_dfs": Mocks.Mock_merge_into_series.sort_dfs,
    }


class Test_merge_into_series_df_list:
    """Placeholder failing test for variable 'df_list' of 'merge_into_series'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: df_list of merge_into_series")


class Test_merge_into_series_time_between_tests_seconds:
    """Placeholder failing test for variable 'time_between_tests_seconds' of 'merge_into_series'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: time_between_tests_seconds of merge_into_series")


class Test_merge_into_series_verbose:
    def test_true(self, base_args):
        raise NotImplementedError("Test not implemented for variable: verbose of merge_into_series")
        original_df = base_args["df"].copy()
        base_args["verbose"] = True
        result = merge_into_series(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_merge_into_series.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_merge_into_series.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        raise NotImplementedError("Test not implemented for variable: verbose of merge_into_series")
        original_df = base_args["df"].copy()
        base_args["verbose"] = False
        result = merge_into_series(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_merge_into_series.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_merge_into_series.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["verbose"] = None
        assert_raises_and_print(ValueError, merge_into_series, **base_args)

    def test_wrong_type(self, base_args):
        base_args["verbose"] = "wrong type"
        assert not isinstance(base_args["verbose"], bool)
        assert_raises_and_print(ValueError, merge_into_series, **base_args)


class Test_merge_into_series_sort_dfs:
    def test_true(self, base_args):
        raise NotImplementedError("Test not implemented for variable: verbose of merge_into_series")
        original_df = base_args["df"].copy()
        base_args["sort_dfs"] = True
        result = merge_into_series(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_merge_into_series.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_merge_into_series.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        raise NotImplementedError("Test not implemented for variable: verbose of merge_into_series")
        original_df = base_args["df"].copy()
        base_args["sort_dfs"] = False
        result = merge_into_series(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_merge_into_series.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_merge_into_series.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["sort_dfs"] = None
        assert_raises_and_print(ValueError, merge_into_series, **base_args)

    def test_wrong_type(self, base_args):
        base_args["sort_dfs"] = "wrong type"
        assert not isinstance(base_args["sort_dfs"], bool)
        assert_raises_and_print(ValueError, merge_into_series, **base_args)


class Test_merge_into_series_dfs:
    """Placeholder failing test for variable 'dfs' of 'merge_into_series'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: dfs of merge_into_series")
