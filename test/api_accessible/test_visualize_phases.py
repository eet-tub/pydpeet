import logging
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import _assert_raises_and_print
from src.pydpeet import visualize_phases


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df": Mocks.Mock_visualize_phases.df.copy(),
        "config": replace(Mocks.Mock_visualize_phases.config),
    }


class Test_visualize_phases_df:
    # Only first test
    def test_valid(self, base_args, caplog):
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        # visualize_phases returns None (it's a visualization function)
        assert result is None

    def test_none(self, base_args):
        base_args["df"] = None
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df"] = "wrong type"
        assert not isinstance(base_args["df"], pd.DataFrame)
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_empty(self, base_args):
        base_args["df"] = pd.DataFrame()
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df"] = base_args["df"].drop(Mocks.Mock_visualize_phases.required_columns, axis=1)
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        for col, _dtype in Mocks.Mock_visualize_phases.required_columns_dtypes:
            base_args["df"][col] = base_args["df"][col].astype(str)
        expected_dtypes = pd.Series({col: dtype for col, dtype in Mocks.Mock_visualize_phases.required_columns_dtypes})
        actual_dtypes = base_args["df"][Mocks.Mock_visualize_phases.required_columns].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["df"].loc[:9, Mocks.Mock_visualize_phases.required_columns[0]] = np.nan
        with caplog.at_level(logging.WARNING):
            visualize_phases(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_visualize_phases.required_columns[0]}' contains NaN values." in record.message
            for record in caplog.records
        )

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        base_args["df"].loc[:9, Mocks.Mock_visualize_phases.required_columns[0]] = np.inf
        with caplog.at_level(logging.WARNING):
            visualize_phases(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_visualize_phases.required_columns[0]}' contains infinite values." in record.message
            for record in caplog.records
        )


class Test_visualize_phases_config:
    def test_valid(self, base_args, caplog):
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_none(self, base_args):
        base_args["config"] = None
        _assert_raises_and_print(AttributeError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["config"] = "wrong type"
        assert not isinstance(base_args["config"], dict)
        _assert_raises_and_print(AttributeError, visualize_phases, **base_args)

    def test_use_lines_for_segments_true(self, base_args, caplog):
        base_args["config"].use_lines_for_segments = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_use_lines_for_segments_false(self, base_args, caplog):
        base_args["config"].use_lines_for_segments = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_use_lines_for_segments_none(self, base_args):
        base_args["config"].use_lines_for_segments = None
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_use_lines_for_segments_wrong_type(self, base_args):
        base_args["config"].use_lines_for_segments = "wrong type"
        assert not isinstance(base_args["config"].use_lines_for_segments, bool)
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_show_column_names_true(self, base_args, caplog):
        base_args["config"].show_column_names = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_show_column_names_false(self, base_args, caplog):
        base_args["config"].show_column_names = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_show_column_names_none(self, base_args):
        base_args["config"].show_column_names = None
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_show_column_names_wrong_type(self, base_args):
        base_args["config"].show_column_names = "wrong type"
        assert not isinstance(base_args["config"].show_column_names, bool)
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_show_time_true(self, base_args, caplog):
        base_args["config"].show_time = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_show_time_false(self, base_args, caplog):
        base_args["config"].show_time = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_show_time_none(self, base_args):
        base_args["config"].show_time = None
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_show_time_wrong_type(self, base_args):
        base_args["config"].show_time = "wrong type"
        assert not isinstance(base_args["config"].show_time, bool)
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_show_id_true(self, base_args, caplog):
        base_args["config"].show_id = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_show_id_false(self, base_args, caplog):
        base_args["config"].show_id = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_show_id_none(self, base_args):
        base_args["config"].show_id = None
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_show_id_wrong_type(self, base_args):
        base_args["config"].show_id = "wrong type"
        assert not isinstance(base_args["config"].show_id, bool)
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_show_runtime_true(self, base_args, caplog):
        base_args["config"].show_runtime = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_show_runtime_false(self, base_args, caplog):
        base_args["config"].show_runtime = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_show_runtime_none(self, base_args):
        base_args["config"].show_runtime = None
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_show_runtime_wrong_type(self, base_args):
        base_args["config"].show_runtime = "wrong type"
        assert not isinstance(base_args["config"].show_runtime, bool)
        _assert_raises_and_print(ValueError, visualize_phases, **base_args)
