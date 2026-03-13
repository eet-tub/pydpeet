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
        "df_primitives": Mocks.df_primitives.copy(),
        "end_condition_map": Mocks.end_condition_map,
        "threshold_warnings": Mocks.threshold_warnings,
    }


class Test_generate_instructions_df_primitives:
    # Only first test
    def test_valid(self, base_args):
        original_df = base_args["VARIABLE"].copy()
        result = generate_instructions(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_generate_instructions.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_generate_instructions.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["VARIABLE"] = None
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_wrong_type(self, base_args):
        base_args["VARIABLE"] = "wrong type"
        assert not isinstance(base_args["VARIABLE"], pd.DataFrame)
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_empty(self, base_args):
        base_args["VARIABLE"] = pd.DataFrame()
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["VARIABLE"] = base_args["VARIABLE"].drop(Mocks.Mock_generate_instructions.required_columns)
        assert_raises_and_print(KeyError, generate_instructions, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_generate_instructions.required_columns] = base_args["VARIABLE"][
            Mocks.Mock_generate_instructions.required_columns
        ].astype(int)
        assert (
            base_args["VARIABLE"][Mocks.Mock_generate_instructions.required_columns].dtypes
            != Mocks.Mock_generate_instructions.required_columns_dtypes
        )
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_nan_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_generate_instructions.required_columns] = np.nan
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_none_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_generate_instructions.required_columns] = None
        assert_raises_and_print(ValueError, generate_instructions, **base_args)

    def test_inf_values(self, base_args):
        base_args["VARIABLE"][Mocks.Mock_generate_instructions.required_columns] = np.inf
        assert_raises_and_print(ValueError, generate_instructions, **base_args)


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
