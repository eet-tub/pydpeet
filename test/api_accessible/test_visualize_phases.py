import numpy as np
import pytest
import pandas as pd

from pydpeet.utils.assert_raises_and_print import assert_raises_and_print
from pydpeet.res.res_for_unittests.res import Mocks

from src.pydpeet import visualize_phases


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "dataframe": Mocks.Mock_visualize_phases.dataframe,
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


class Test_visualize_phases_dataframe(object):
    #Only first test
    def test_valid(self, base_args):
        original_df = base_args["dataframe"].copy()
        result = visualize_phases(**base_args)

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
        base_args["dataframe"] = base_args["dataframe"].drop(Mocks.Mock_visualize_phases.required_columns)
        assert_raises_and_print(KeyError, visualize_phases, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns] = base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns].astype(int)
        assert base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns].dtypes != Mocks.Mock_visualize_phases.required_columns_dtypes
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_nan_values(self, base_args):
        base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns] = np.nan
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_none_values(self, base_args):
        base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_inf_values(self, base_args):
        base_args["dataframe"][Mocks.Mock_visualize_phases.required_columns] = np.inf
        assert_raises_and_print(ValueError, visualize_phases, **base_args)


class Test_visualize_phases_start_time(object):
    """Placeholder failing test for variable 'start_time' of 'visualize_phases'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: start_time of visualize_phases')


class Test_visualize_phases_end_time(object):
    """Placeholder failing test for variable 'end_time' of 'visualize_phases'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: end_time of visualize_phases')


class Test_visualize_phases_visualize_phases_config(object):
    """Placeholder failing test for variable 'visualize_phases_config' of 'visualize_phases'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: visualize_phases_config of visualize_phases')


class Test_visualize_phases_segment_alpha(object):
    """Placeholder failing test for variable 'segment_alpha' of 'visualize_phases'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: segment_alpha of visualize_phases')


class Test_visualize_phases_line_visualization_config(object):
    """Placeholder failing test for variable 'line_visualization_config' of 'visualize_phases'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: line_visualization_config of visualize_phases')


class Test_visualize_phases_use_lines_for_segments(object):
    def test_true(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["use_lines_for_segments"] = True
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["use_lines_for_segments"] = False
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["use_lines_for_segments"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["use_lines_for_segments"] = "wrong type"
        assert not isinstance(base_args["use_lines_for_segments"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)



class Test_visualize_phases_show_column_names(object):
    def test_true(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["show_column_names"] = True
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["show_column_names"] = False
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["show_column_names"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["show_column_names"] = "wrong type"
        assert not isinstance(base_args["show_column_names"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)



class Test_visualize_phases_show_time(object):
    def test_true(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["show_time"] = True
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["show_time"] = False
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["show_time"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["show_time"] = "wrong type"
        assert not isinstance(base_args["VARIABLE"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)



class Test_visualize_phases_show_id(object):
    def test_true(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["show_id"] = True
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["show_id"] = False
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["show_id"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["show_id"] = "wrong type"
        assert not isinstance(base_args["show_id"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)



class Test_visualize_phases_width_height_ratio(object):
    """Placeholder failing test for variable 'width_height_ratio' of 'visualize_phases'."""
    def test_placeholder(self):
        raise NotImplementedError('Test not implemented for variable: width_height_ratio of visualize_phases')


class Test_visualize_phases_show_runtime(object):
    def test_true(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["show_runtime"] = True
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["dataframe"].copy()
        base_args["show_runtime"] = False
        result = visualize_phases(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_visualize_phases.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_visualize_phases.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["show_runtime"] = None
        assert_raises_and_print(ValueError, visualize_phases, **base_args)

    def test_wrong_type(self, base_args):
        base_args["show_runtime"] = "wrong type"
        assert not isinstance(base_args["show_runtime"], bool)
        assert_raises_and_print(ValueError, visualize_phases, **base_args)


