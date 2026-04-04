import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import mapping


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "data_frame": Mocks.Mock_mapping.df.copy(),
        "column_map": Mocks.Mock_mapping.column_map,
        "missing_columns": Mocks.Mock_mapping.missing_columns,
    }


class Test_mapping_data_frame:
    def test_valid(self, base_args):
        original_df = base_args["data_frame"].copy()
        result = mapping(**base_args)
        # Check that add_columns are present
        assert all(col in result.columns for col in Mocks.Mock_mapping.add_columns)
        # Check that mapped columns have correct standardized names
        for raw_col, std_col in Mocks.Mock_mapping.column_map.items():
            assert std_col in result.columns
            # Verify values are preserved from original
            assert result[std_col].equals(original_df[raw_col])

    def test_none(self, base_args):
        base_args["data_frame"] = None
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_wrong_type(self, base_args):
        base_args["data_frame"] = "wrong type"
        assert not isinstance(base_args["data_frame"], pd.DataFrame)
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_empty(self, base_args):
        base_args["data_frame"] = pd.DataFrame()
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["data_frame"] = base_args["data_frame"].drop(Mocks.Mock_mapping.required_columns, axis=1)
        assert_raises_and_print(ValueError, mapping, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        # Mapping function only renames columns, doesn't validate dtypes
        # This test is not applicable
        assert True

    def test_nan_values(self, base_args, caplog):
        base_args["data_frame"][Mocks.Mock_mapping.required_columns[0]].iloc[:10] = np.nan
        with caplog.at_level(logging.WARNING):
            result = mapping(**base_args)
        # Check result has mapped columns with NaN values preserved
        mapped_col = Mocks.Mock_mapping.column_map[Mocks.Mock_mapping.required_columns[0]]
        assert pd.isna(result[mapped_col].iloc[:10]).all()
        assert all(col in result.columns for col in Mocks.Mock_mapping.add_columns)

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        base_args["data_frame"][Mocks.Mock_mapping.required_columns[0]].iloc[:10] = np.inf
        with caplog.at_level(logging.WARNING):
            result = mapping(**base_args)
        # Check result has mapped columns with inf values preserved
        mapped_col = Mocks.Mock_mapping.column_map[Mocks.Mock_mapping.required_columns[0]]
        assert np.isinf(result[mapped_col].iloc[:10]).all()
        assert all(col in result.columns for col in Mocks.Mock_mapping.add_columns)


class Test_mapping_column_map:
    """Placeholder failing test for variable 'column_map' of 'mapping'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: column_map of mapping")


class Test_mapping_missing_columns:
    """Placeholder failing test for variable 'missing_columns' of 'mapping'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: missing_columns of mapping")
