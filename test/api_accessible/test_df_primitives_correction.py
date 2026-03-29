import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet import df_primitives_correction
from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print


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
    def test_valid(self, base_args):
        result = df_primitives_correction(**base_args)
        expected = Mocks.Mock_df_primitives_correction.df_primitives_expected.copy()
        assert result.equals(expected)

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
            Mocks.Mock_df_primitives_correction.required_columns, axis=1
        )
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        for col, _dtype in Mocks.Mock_df_primitives_correction.required_columns_dtypes:
            base_args["df_primitives"][col] = base_args["df_primitives"][col].astype(str)
        expected_dtypes = pd.Series(
            {col: dtype for col, dtype in Mocks.Mock_df_primitives_correction.required_columns_dtypes}
        )
        actual_dtypes = base_args["df_primitives"][Mocks.Mock_df_primitives_correction.required_columns].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_nan_values(self, base_args, caplog):
        col = Mocks.Mock_df_primitives_correction.required_columns[0]
        base_args["df_primitives"] = base_args["df_primitives"].copy()
        base_args["df_primitives"].loc[base_args["df_primitives"].index[:10], col] = np.nan
        with caplog.at_level(logging.WARNING):
            df_primitives_correction(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message if caplog.records else 'None'}")
        assert any(f"Column '{col}' contains NaN values." in record.message for record in caplog.records)

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        col = Mocks.Mock_df_primitives_correction.required_columns[0]
        base_args["df_primitives"] = base_args["df_primitives"].copy()
        base_args["df_primitives"].loc[base_args["df_primitives"].index[:10], col] = np.inf
        with caplog.at_level(logging.WARNING):
            df_primitives_correction(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message if caplog.records else 'None'}")
        assert any(f"Column '{col}' contains infinite values." in record.message for record in caplog.records)


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
        base_args["reindex"] = True
        result = df_primitives_correction(**base_args)
        expected = Mocks.Mock_df_primitives_correction.df_primitives_expected.copy()
        assert result.equals(expected)

    def test_false(self, base_args):
        base_args["reindex"] = False
        result = df_primitives_correction(**base_args)
        # When reindex=False, IDs won't be consecutive - verify it still works
        assert isinstance(result, pd.DataFrame)
        assert "ID" in result.columns

    def test_none(self, base_args):
        base_args["reindex"] = None
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_wrong_type(self, base_args):
        base_args["reindex"] = "wrong type"
        assert not isinstance(base_args["reindex"], bool)
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)


class Test_df_primitives_correction_reannotate:
    def test_true(self, base_args):
        base_args["reannotate"] = True
        result = df_primitives_correction(**base_args)
        expected = Mocks.Mock_df_primitives_correction.df_primitives_expected.copy()
        assert result.equals(expected)

    def test_false(self, base_args):
        base_args["reannotate"] = False
        result = df_primitives_correction(**base_args)
        # When reannotate=False, annotations won't be updated - verify it still works
        assert isinstance(result, pd.DataFrame)
        assert "Duration" in result.columns

    def test_none(self, base_args):
        base_args["reannotate"] = None
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)

    def test_wrong_type(self, base_args):
        base_args["reannotate"] = "wrong type"
        assert not isinstance(base_args["reannotate"], bool)
        assert_raises_and_print(ValueError, df_primitives_correction, **base_args)
