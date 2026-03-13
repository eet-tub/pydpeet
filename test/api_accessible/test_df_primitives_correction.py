import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import df_primitives_correction


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df_primitives": Mocks.Mock_df_primitives_correction.df_primitives.copy(),
        "correction_config": Mocks.Mock_df_primitives_correction.correction_config,
        "data_columns": Mocks.Mock_df_primitives_correction.data_columns,
        "thresholds": Mocks.Mock_df_primitives_correction.thresholds,
        "reindex": Mocks.Mock_df_primitives_correction.reindex,
        "reannotate": Mocks.Mock_df_primitives_correction.reannotate,
    }


class Test_df_primitives_correction_df_primitives:
    # Only first test
    def test_valid(self, base_args):
        original_df = base_args["df_primitives"].copy()
        result = df_primitives_correction(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_df_primitives_correction.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_df_primitives_correction.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["df_primitives"] = None
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df_primitives"] = "wrong type"
        assert not isinstance(base_args["df_primitives"], pd.DataFrame)
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_empty(self, base_args):
        base_args["df_primitives"] = pd.DataFrame()
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df_primitives"] = base_args["df_primitives"].drop(
            Mocks.Mock_df_primitives_correction.required_columns
        )
        assert_raises_and_print(KeyError, df_primitives_correction, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df_primitives"][Mocks.Mock_df_primitives_correction.required_columns] = base_args["df_primitives"][
            Mocks.Mock_df_primitives_correction.required_columns
        ].astype(int)
        assert (
            base_args["df_primitives"][Mocks.Mock_df_primitives_correction.required_columns].dtypes
            != Mocks.Mock_df_primitives_correction.required_columns_dtypes
        )
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_nan_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_df_primitives_correction.required_columns] = np.nan
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_none_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_df_primitives_correction.required_columns] = None
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_inf_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_df_primitives_correction.required_columns] = np.inf
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)


class Test_df_primitives_correction_correction_config:
    """Placeholder failing test for variable 'correction_config' of 'df_primitives_correction'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: correction_config of df_primitives_correction")


class Test_df_primitives_correction_data_columns:
    """Placeholder failing test for variable 'data_columns' of 'df_primitives_correction'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: data_columns of df_primitives_correction")


class Test_df_primitives_correction_thresholds:
    """Placeholder failing test for variable 'thresholds' of 'df_primitives_correction'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: thresholds of df_primitives_correction")


class Test_df_primitives_correction_reindex:
    def test_true(self, base_args):
        original_df = base_args["df_primitives"].copy()
        base_args["reindex"] = True
        result = df_primitives_correction(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_df_primitives_correction.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_df_primitives_correction.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df_primitives"].copy()
        base_args["reindex"] = False
        result = df_primitives_correction(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_df_primitives_correction.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_df_primitives_correction.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["reindex"] = None
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_wrong_type(self, base_args):
        base_args["reindex"] = "wrong type"
        assert not isinstance(base_args["reindex"], bool)
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)


class Test_df_primitives_correction_reannotate:
    def test_true(self, base_args):
        original_df = base_args["df_primitives"].copy()
        base_args["reannotate"] = True
        result = df_primitives_correction(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_df_primitives_correction.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_df_primitives_correction.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df_primitives"].copy()
        base_args["reannotate"] = False
        result = df_primitives_correction(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_df_primitives_correction.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_df_primitives_correction.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["reannotate"] = None
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_wrong_type(self, base_args):
        base_args["reannotate"] = "wrong type"
        assert not isinstance(base_args["reannotate"], bool)
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)
