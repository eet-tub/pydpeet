import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import extract_sequence_overview


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {"df_primitives": Mocks.Mock_extract_sequence_overview.df_primitives.copy(), "SEGMENT_SEQUENCE_CONFIG": Mocks.Mock_extract_sequence_overview.SEGMENT_SEQUENCE_CONFIG, "SHOW_RUNTIME": Mocks.Mock_extract_sequence_overview.SHOW_RUNTIME}


class Test_extract_sequence_overview_df_primitives:
    # Only first test
    def test_valid(self, base_args):
        raise NotImplementedError("Test not implemented for variable: df_primitives of extract_sequence_overview")
        original_df = base_args["df_primitives"].copy()
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_extract_sequence_overview.add_columns, axis=1), original_df)

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
        base_args["df_primitives"] = base_args["df_primitives"].drop(Mocks.Mock_extract_sequence_overview.required_columns)
        assert_raises_and_print(KeyError, extract_sequence_overview, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns] = base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns].astype(int)
        assert base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns].dtypes != Mocks.Mock_extract_sequence_overview.required_columns_dtypes
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_nan_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns] = np.nan
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_none_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns] = None
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_inf_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_extract_sequence_overview.required_columns] = np.inf
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)


class Test_extract_sequence_overview_SEGMENT_SEQUENCE_CONFIG:
    """Placeholder failing test for variable 'SEGMENT_SEQUENCE_CONFIG' of 'extract_sequence_overview'."""

    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: SEGMENT_SEQUENCE_CONFIG of extract_sequence_overview")


class Test_extract_sequence_overview_SHOW_RUNTIME:
    def test_true(self, base_args):
        raise NotImplementedError("Test not implemented for variable: SHOW_RUNTIME of extract_sequence_overview")
        original_df = base_args["df_primitives"].copy()
        base_args["SHOW_RUNTIME"] = True
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_extract_sequence_overview.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        raise NotImplementedError("Test not implemented for variable: SHOW_RUNTIME of extract_sequence_overview")
        original_df = base_args["df_primitives"].copy()
        base_args["SHOW_RUNTIME"] = False
        result = extract_sequence_overview(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_extract_sequence_overview.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_extract_sequence_overview.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["SHOW_RUNTIME"] = None
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)

    def test_wrong_type(self, base_args):
        base_args["SHOW_RUNTIME"] = "wrong type"
        assert not isinstance(base_args["SHOW_RUNTIME"], bool)
        assert_raises_and_print(ValueError, extract_sequence_overview, **base_args)
