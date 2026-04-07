import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from src.pydpeet import visualize_phases


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "dataframe": Mocks.Mock_visualize_phases.dataframe.copy(),
        "start_time": Mocks.Mock_visualize_phases.start_time,
        "end_time": Mocks.Mock_visualize_phases.end_time,
        "visualize_phases_config": Mocks.Mock_visualize_phases.visualize_phases_config,
        "segment_alpha": Mocks.Mock_visualize_phases.segment_alpha,
        "line_visualization_config": Mocks.Mock_visualize_phases.line_visualization_config,
        "use_lines_for_segments": Mocks.Mock_visualize_phases.use_lines_for_segments,
        "show_column_names": Mocks.Mock_visualize_phases.show_column_names,
        "show_time": Mocks.Mock_visualize_phases.show_time,
        "show_id": Mocks.Mock_visualize_phases.show_id,
        "width_height_ratio": Mocks.Mock_visualize_phases.width_height_ratio,
        "show_runtime": Mocks.Mock_visualize_phases.show_runtime,
    }


class Test_visualize_phases_dataframe:
    # Only first test
    def test_valid(self, base_args, caplog):
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        # visualize_phases returns None (it's a visualization function)
        assert result is None

    def test_none(self, base_args):
        base_args["dataframe"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["dataframe"] = "wrong type"
        assert not isinstance(base_args["dataframe"], pd.DataFrame)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_empty(self, base_args):
        base_args["dataframe"] = pd.DataFrame()
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["dataframe"] = base_args["dataframe"].drop(Mocks.Mock_visualize_phases.required_columns, axis=1)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        for col, _dtype in Mocks.Mock_visualize_phases.required_columns_dtypes:
            base_args["dataframe"][col] = base_args["dataframe"][col].astype(str)
        expected_dtypes = pd.Series({col: dtype for col, dtype in Mocks.Mock_visualize_phases.required_columns_dtypes})
        actual_dtypes = base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns[0]].iloc[:10] = np.nan
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
        base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns[0]].iloc[:10] = np.inf
        with caplog.at_level(logging.WARNING):
            visualize_phases(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_visualize_phases.required_columns[0]}' contains infinite values." in record.message
            for record in caplog.records
        )


class Test_visualize_phases_start_time:
    """Placeholder failing test for variable 'start_time' of 'visualize_phases'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: start_time of visualize_phases")


class Test_visualize_phases_end_time:
    """Placeholder failing test for variable 'end_time' of 'visualize_phases'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: end_time of visualize_phases")


class Test_visualize_phases_visualize_phases_config:
    """Placeholder failing test for variable 'visualize_phases_config' of 'visualize_phases'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: visualize_phases_config of visualize_phases")


class Test_visualize_phases_segment_alpha:
    """Placeholder failing test for variable 'segment_alpha' of 'visualize_phases'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: segment_alpha of visualize_phases")


class Test_visualize_phases_line_visualization_config:
    """Placeholder failing test for variable 'line_visualization_config' of 'visualize_phases'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: line_visualization_config of visualize_phases")


class Test_visualize_phases_use_lines_for_segments:
    def test_true(self, base_args, caplog):
        base_args["use_lines_for_segments"] = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_false(self, base_args, caplog):
        base_args["use_lines_for_segments"] = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_none(self, base_args):
        base_args["use_lines_for_segments"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["use_lines_for_segments"] = "wrong type"
        assert not isinstance(base_args["use_lines_for_segments"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)


class Test_visualize_phases_show_column_names:
    def test_true(self, base_args, caplog):
        base_args["show_column_names"] = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_false(self, base_args, caplog):
        base_args["show_column_names"] = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_none(self, base_args):
        base_args["show_column_names"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["show_column_names"] = "wrong type"
        assert not isinstance(base_args["show_column_names"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)


class Test_visualize_phases_show_time:
    def test_true(self, base_args, caplog):
        base_args["show_time"] = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_false(self, base_args, caplog):
        base_args["show_time"] = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_none(self, base_args):
        base_args["show_time"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["show_time"] = "wrong type"
        assert not isinstance(base_args["show_time"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)


class Test_visualize_phases_show_id:
    def test_true(self, base_args, caplog):
        base_args["show_id"] = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_false(self, base_args, caplog):
        base_args["show_id"] = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_none(self, base_args):
        base_args["show_id"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["show_id"] = "wrong type"
        assert not isinstance(base_args["show_id"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)


class Test_visualize_phases_width_height_ratio:
    """Placeholder failing test for variable 'width_height_ratio' of 'visualize_phases'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: width_height_ratio of visualize_phases")


class Test_visualize_phases_show_runtime:
    def test_true(self, base_args, caplog):
        base_args["show_runtime"] = True
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_false(self, base_args, caplog):
        base_args["show_runtime"] = False
        with caplog.at_level(logging.INFO):
            result = visualize_phases(**base_args)
        assert result is None

    def test_none(self, base_args):
        base_args["show_runtime"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["show_runtime"] = "wrong type"
        assert not isinstance(base_args["show_runtime"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)
