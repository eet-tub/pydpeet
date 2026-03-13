import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import extract_ocv_iocv


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "min_pause_lenght": Mocks.Mock_extract_ocv_iocv.min_pause_lenght,
        "min_loops": Mocks.Mock_extract_ocv_iocv.min_loops,
        "visualize": Mocks.Mock_extract_ocv_iocv.visualize,
        "df_primitives": Mocks.Mock_extract_ocv_iocv.df_primitives,
        "df": Mocks.Mock_extract_ocv_iocv.df,
        "config": Mocks.Mock_extract_ocv_iocv.config,
    }


class Test_extract_ocv_iocv_min_pause_lenght:
    """Placeholder failing test for variable 'min_pause_lenght' of 'extract_ocv_iocv'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: min_pause_lenght of extract_ocv_iocv")


class Test_extract_ocv_iocv_min_loops:
    """Placeholder failing test for variable 'min_loops' of 'extract_ocv_iocv'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: min_loops of extract_ocv_iocv")


class Test_extract_ocv_iocv_visualize:
    """Placeholder failing test for variable 'visualize' of 'extract_ocv_iocv'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: visualize of extract_ocv_iocv")


class Test_extract_ocv_iocv_df_primitives:
    # Only first test
    def test_valid(self, base_args):
        raise NotImplementedError("Test not implemented for variable: config of extract_ocv_iocv")

    def test_none(self, base_args):
        base_args["df_primitives"] = None
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df_primitives"] = "wrong type"
        assert not isinstance(base_args["df_primitives"], pd.DataFrame)
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_empty(self, base_args):
        base_args["df_primitives"] = pd.DataFrame()
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df_primitives"] = base_args["df_primitives"].drop(Mocks.Mock_extract_ocv_iocv.required_columns)
        assert_raises_and_print(KeyError, extract_ocv_iocv, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df_primitives"][Mocks.Mock_extract_ocv_iocv.required_columns] = base_args["df_primitives"][
            Mocks.Mock_extract_ocv_iocv.required_columns
        ].astype(int)
        assert (
            base_args["df_primitives"][Mocks.Mock_extract_ocv_iocv.required_columns].dtypes
            != Mocks.Mock_extract_ocv_iocv.required_columns_dtypes
        )
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_nan_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_extract_ocv_iocv.required_columns] = np.nan
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_none_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_extract_ocv_iocv.required_columns] = None
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_inf_values(self, base_args):
        base_args["df_primitives"][Mocks.Mock_extract_ocv_iocv.required_columns] = np.inf
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)


class Test_extract_ocv_iocv_df:
    # Only first test
    def test_valid(self, base_args):
        raise NotImplementedError("Test not implemented for variable: config of extract_ocv_iocv")

    def test_none(self, base_args):
        base_args["df"] = None
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df"] = "wrong type"
        assert not isinstance(base_args["df"], pd.DataFrame)
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_empty(self, base_args):
        base_args["df"] = pd.DataFrame()
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df"] = base_args["df"].drop(Mocks.Mock_extract_ocv_iocv.required_columns)
        assert_raises_and_print(KeyError, extract_ocv_iocv, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["df"][Mocks.Mock_extract_ocv_iocv.required_columns] = base_args["df"][
            Mocks.Mock_extract_ocv_iocv.required_columns
        ].astype(int)
        assert (
            base_args["df"][Mocks.Mock_extract_ocv_iocv.required_columns].dtypes
            != Mocks.Mock_extract_ocv_iocv.required_columns_dtypes
        )
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_nan_values(self, base_args):
        base_args["df"][Mocks.Mock_extract_ocv_iocv.required_columns] = np.nan
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_none_values(self, base_args):
        base_args["df"][Mocks.Mock_extract_ocv_iocv.required_columns] = None
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)

    def test_inf_values(self, base_args):
        base_args["df"][Mocks.Mock_extract_ocv_iocv.required_columns] = np.inf
        assert_raises_and_print(ValueError, extract_ocv_iocv, **base_args)


class Test_extract_ocv_iocv_config:
    """Placeholder failing test for variable 'config' of 'extract_ocv_iocv'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: config of extract_ocv_iocv")
