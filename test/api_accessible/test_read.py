import pandas as pd
import pytest

from pydpeet.res.res_for_unittests.res import Mocks
from pydpeet.utils.assert_raises_and_print import _assert_raises_and_print
from src.pydpeet import read


@pytest.fixture
def base_args():
    """Provides a fresh dictionary of default arguments for every test."""
    return {
        "config": Mocks.Mock_read.config,
        "input_path": Mocks.Mock_read.input_path,
        "keep_all_additional_data": Mocks.Mock_read.keep_all_additional_data,
        "custom_folder_path": Mocks.Mock_read.custom_folder_path,
    }


class Test_read_config:
    """Placeholder failing test for variable 'config' of 'read'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: config of read")


class Test_read_input_path:
    """Placeholder failing test for variable 'input_path' of 'read'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: input_path of read")


class Test_read_keep_all_additional_data:
    def test_true(self, base_args, benchmark):
        def _run():
            base_args["keep_all_additional_data"] = True
            result = read(**base_args)
            expected = Mocks.Mock_read.df_expected_with_additional_data
            assert pd.DataFrame.equals(result, expected)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_false(self, base_args, benchmark):
        def _run():
            base_args["keep_all_additional_data"] = False
            result = read(**base_args)
            expected = Mocks.Mock_read.df_expected_without_additional_data
            assert pd.DataFrame.equals(result, expected)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_none(self, base_args, benchmark):
        def _run():
            base_args["keep_all_additional_data"] = None
            _assert_raises_and_print(ValueError, read, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)

    def test_wrong_type(self, base_args, benchmark):
        def _run():
            base_args["keep_all_additional_data"] = "wrong type"
            assert not isinstance(base_args["keep_all_additional_data"], bool)
            _assert_raises_and_print(ValueError, read, **base_args)

        benchmark.pedantic(_run, rounds=1, warmup_rounds=0, iterations=1)


class Test_read_custom_folder_path:
    """Placeholder failing test for variable 'custom_folder_path' of 'read'."""

    @pytest.mark.skip(reason="Placeholder test")
    def test_placeholder(self):
        raise NotImplementedError("Test not implemented for variable: custom_folder_path of read")
