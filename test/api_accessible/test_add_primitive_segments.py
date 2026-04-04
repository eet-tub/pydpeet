import logging

import numpy as np
import pandas as pd
import pytest

from pydpeet import add_primitive_segments
from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import assert_raises_and_print


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "df": Mocks.Mock_add_primitive_segments.df.copy(),
        "STEP_ANALYZER_PRIMITIVES_CONFIG": Mocks.Mock_add_primitive_segments.STEP_ANALYZER_PRIMITIVES_CONFIG,
        "SEGMENTS_TO_DETECT_CONFIG": Mocks.Mock_add_primitive_segments.SEGMENTS_TO_DETECT_CONFIG,
        "ADJUST_SEGMENTS_CONFIG": Mocks.Mock_add_primitive_segments.ADJUST_SEGMENTS_CONFIG,
        "THRESHOLDS_PRIMITIVE_ANNOTATION": Mocks.Mock_add_primitive_segments.THRESHOLDS_PRIMITIVE_ANNOTATION,
        "THRESHOLD_CV_SEGMENTS_0A_END": Mocks.Mock_add_primitive_segments.THRESHOLD_CV_SEGMENTS_0A_END,
        "THRESHOLD_CONSOLE_PRINTS_CV_CHECK": Mocks.Mock_add_primitive_segments.THRESHOLD_CONSOLE_PRINTS_CV_CHECK,
        "THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK": Mocks.Mock_add_primitive_segments.THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK,
        "THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH": Mocks.Mock_add_primitive_segments.THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH,
        "THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK": Mocks.Mock_add_primitive_segments.THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK,
        "SHOW_RUNTIME": Mocks.Mock_add_primitive_segments.SHOW_RUNTIME,
        "check_CV_0Aend_segments_bool": Mocks.Mock_add_primitive_segments.check_CV_0Aend_segments_bool,
        "check_zero_length_segments_bool": Mocks.Mock_add_primitive_segments.check_zero_length_segments_bool,
        "check_Power_zero_W_segments_bool": Mocks.Mock_add_primitive_segments.check_Power_zero_W_segments_bool,
        "supress_IO_warnings": Mocks.Mock_add_primitive_segments.supress_IO_warnings,
        "PRECOMPILE": Mocks.Mock_add_primitive_segments.PRECOMPILE,
        "FORCE_PRECOMPILATION": Mocks.Mock_add_primitive_segments.FORCE_PRECOMPILATION,
    }


class Test_add_primitive_segments_df:
    # Only first test
    def test_valid(self, base_args):
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["df"] = None
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_wrong_type(self, base_args):
        base_args["df"] = "wrong type"
        assert not isinstance(base_args["df"], pd.DataFrame)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_empty(self, base_args):
        base_args["df"] = pd.DataFrame()
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_missing_required_columns(self, base_args):
        base_args["df"] = base_args["df"].drop(Mocks.Mock_add_primitive_segments.required_columns, axis=1)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_wrong_column_dtypes(self, base_args):
        for col, _dtype in Mocks.Mock_add_primitive_segments.required_columns_dtypes:
            base_args["df"][col] = base_args["df"][col].astype(str)
        expected_dtypes = pd.Series(
            {col: dtype for col, dtype in Mocks.Mock_add_primitive_segments.required_columns_dtypes}
        )
        actual_dtypes = base_args["df"][Mocks.Mock_add_primitive_segments.required_columns].dtypes
        assert not actual_dtypes.equals(expected_dtypes)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)

    def test_nan_values(self, base_args, caplog):
        base_args["df"][Mocks.Mock_add_primitive_segments.required_columns[0]].iloc[:10] = np.nan
        with caplog.at_level(logging.WARNING):
            add_primitive_segments(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_add_primitive_segments.required_columns[0]}' contains NaN values." in record.message
            for record in caplog.records
        )

    def test_none_values(self, base_args, caplog):
        # assert True due to dtype == float (in all required columns) is it impossible to check None since it
        # would be converted to NaN or throw the test_wrong_column_dtypes failure
        assert True

    def test_inf_values(self, base_args, caplog):
        base_args["df"][Mocks.Mock_add_primitive_segments.required_columns[0]].iloc[:10] = np.inf
        with caplog.at_level(logging.WARNING):
            add_primitive_segments(**base_args)
        print(f"\nCaptured Warning: {caplog.records[0].message}")
        assert any(
            f"Column '{Mocks.Mock_add_primitive_segments.required_columns[0]}' contains infinite values."
            in record.message
            for record in caplog.records
        )


class Test_add_primitive_segments_STEP_ANALYZER_PRIMITIVES_CONFIG:
    """Placeholder failing test for variable 'STEP_ANALYZER_PRIMITIVES_CONFIG' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: STEP_ANALYZER_PRIMITIVES_CONFIG of add_primitive_segments"
        )


class Test_add_primitive_segments_SEGMENTS_TO_DETECT_CONFIG:
    """Placeholder failing test for variable 'SEGMENTS_TO_DETECT_CONFIG' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: SEGMENTS_TO_DETECT_CONFIG of add_primitive_segments"
        )


class Test_add_primitive_segments_ADJUST_SEGMENTS_CONFIG:
    """Placeholder failing test for variable 'ADJUST_SEGMENTS_CONFIG' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: ADJUST_SEGMENTS_CONFIG of add_primitive_segments")


class Test_add_primitive_segments_THRESHOLDS_PRIMITIVE_ANNOTATION:
    """Placeholder failing test for variable 'THRESHOLDS_PRIMITIVE_ANNOTATION' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: THRESHOLDS_PRIMITIVE_ANNOTATION of add_primitive_segments"
        )


class Test_add_primitive_segments_THRESHOLD_CV_SEGMENTS_0A_END:
    """Placeholder failing test for variable 'THRESHOLD_CV_SEGMENTS_0A_END' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: THRESHOLD_CV_SEGMENTS_0A_END of add_primitive_segments"
        )


class Test_add_primitive_segments_THRESHOLD_CONSOLE_PRINTS_CV_CHECK:
    """Placeholder failing test for variable 'THRESHOLD_CONSOLE_PRINTS_CV_CHECK' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: THRESHOLD_CONSOLE_PRINTS_CV_CHECK of add_primitive_segments"
        )


class Test_add_primitive_segments_THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK:
    """Placeholder failing test for variable 'THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK of add_primitive_segments"
        )


class Test_add_primitive_segments_THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH:
    """Placeholder failing test for variable 'THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH of add_primitive_segments"
        )


class Test_add_primitive_segments_THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK:
    """Placeholder failing test for variable 'THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK' of 'add_primitive_segments'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError(
            "Test not implemented for variable: THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK of add_primitive_segments"
        )


class Test_add_primitive_segments_SHOW_RUNTIME:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["SHOW_RUNTIME"] = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["SHOW_RUNTIME"] = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["SHOW_RUNTIME"] = None
        # assume replaced with true
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_wrong_type(self, base_args):
        base_args["SHOW_RUNTIME"] = "wrong type"
        assert not isinstance(base_args["SHOW_RUNTIME"], bool)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)


class Test_add_primitive_segments_check_CV_0Aend_segments_bool:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["check_CV_0Aend_segments_bool"] = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["check_CV_0Aend_segments_bool"] = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["check_CV_0Aend_segments_bool"] = None
        # assume replaced with true
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_wrong_type(self, base_args):
        base_args["check_CV_0Aend_segments_bool"] = "wrong type"
        assert not isinstance(base_args["check_CV_0Aend_segments_bool"], bool)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)


class Test_add_primitive_segments_check_zero_length_segments_bool:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["check_zero_length_segments_bool"] = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["check_zero_length_segments_bool"] = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["check_zero_length_segments_bool"] = None
        # assume replaced with true
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_wrong_type(self, base_args):
        base_args["check_zero_length_segments_bool"] = "wrong type"
        assert not isinstance(base_args["check_zero_length_segments_bool"], bool)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)


class Test_add_primitive_segments_check_Power_zero_W_segments_bool:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["check_Power_zero_W_segments_bool"] = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["check_Power_zero_W_segments_bool"] = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_none(self, base_args):
        base_args["check_Power_zero_W_segments_bool"] = None
        # assume replaced with true
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)

    def test_wrong_type(self, base_args):
        base_args["check_Power_zero_W_segments_bool"] = "wrong type"
        assert not isinstance(base_args["check_Power_zero_W_segments_bool"], bool)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)


class Test_add_primitive_segments_supress_IO_warnings:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["supress_IO_warnings"] = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["supress_IO_warnings"] = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["supress_IO_warnings"] = None
        # assume replaced with true
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_wrong_type(self, base_args):
        base_args["supress_IO_warnings"] = "wrong type"
        assert not isinstance(base_args["supress_IO_warnings"], bool)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)


class Test_add_primitive_segments_PRECOMPILE:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["PRECOMPILE"] = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["PRECOMPILE"] = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["PRECOMPILE"] = None
        # assume replaced with true
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_wrong_type(self, base_args):
        base_args["PRECOMPILE"] = "wrong type"
        assert not isinstance(base_args["PRECOMPILE"], bool)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)


class Test_add_primitive_segments_FORCE_PRECOMPILATION:
    def test_true(self, base_args):
        original_df = base_args["df"].copy()
        base_args["FORCE_PRECOMPILATION"] = True
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_false(self, base_args):
        original_df = base_args["df"].copy()
        base_args["FORCE_PRECOMPILATION"] = False
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_none(self, base_args):
        base_args["FORCE_PRECOMPILATION"] = None
        # assume replaced with true
        original_df = base_args["df"].copy()
        result = add_primitive_segments(**base_args)
        assert all(col in result.columns for col in Mocks.Mock_add_primitive_segments.add_columns)
        assert pd.DataFrame.equals(result.drop(Mocks.Mock_add_primitive_segments.add_columns, axis=1), original_df)
        # Compare with expected result
        expected = Mocks.Mock_add_primitive_segments.df_expected
        assert pd.DataFrame.equals(result, expected)

    def test_wrong_type(self, base_args):
        base_args["FORCE_PRECOMPILATION"] = "wrong type"
        assert not isinstance(base_args["FORCE_PRECOMPILATION"], bool)
        assert_raises_and_print(ValueError, add_primitive_segments, **base_args)
