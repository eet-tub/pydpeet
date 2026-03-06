import unittest
from io import StringIO
from unittest.mock import patch

import pandas

from pydpeet.io.configs.config import (
    STANDARD_COLUMNS,
    Config,
)
from pydpeet.io.convert import (
    _add_metadata_to_dataframe,
    _column_mapping,
    _convert_file_to_pandas_data_frame,
    _drop_additional_data,
    _reorder_columns,
)
from pydpeet.io.utils.formatter_utils import replace_empty_with_none_in_standard_columns
from test.utils import RES_PATH


class TestReplaceEmptyWithNoneInStandardColumns(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_df_is_none(self, mock_stdout):
        data = None
        expected = None
        result = replace_empty_with_none_in_standard_columns(data)
        self.assertEqual(expected, result)
        self.assertEqual(
            mock_stdout.getvalue(),
            "\033[31mWARNING: Error replacing empty with None. Reason: dataFrame is None \033[0m\n",
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_df_is_empty(self, mock_stdout):
        data = pandas.DataFrame()
        expected = pandas.DataFrame()
        result = replace_empty_with_none_in_standard_columns(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertEqual(
            mock_stdout.getvalue(),
            "\033[31mWARNING: Error replacing empty with None. Reason: dataframe is empty \033[0m\n",
        )

    def test_exception_handling(self):
        data = {STANDARD_COLUMNS[0]: ["", "value"]}
        df = pandas.DataFrame(data)
        with patch("builtins.print") as mock_print:
            replace_empty_with_none_in_standard_columns(df)
            mock_print.assert_called_once()

    @patch("sys.stdout", new_callable=StringIO)
    def test_replace_empty_with_none(self, mock_stdout):
        config = Config.Custom
        input_path = RES_PATH / "replace_empty_with_none" / "emptyvalues.csv"
        custom_folder_path = RES_PATH / "replace_empty_with_none" / "custom"
        keep_all_additional_data = False

        data_frame, meta_data = _convert_file_to_pandas_data_frame(config, input_path, custom_folder_path)
        data_frame = _column_mapping(data_frame, config, custom_folder_path)
        if not keep_all_additional_data:
            data_frame = _drop_additional_data(data_frame)
        data_frame = _add_metadata_to_dataframe(data_frame, meta_data)
        data_frame = _reorder_columns(data_frame)

        # result = replace_empty_with_none_in_standard_columns(data_frame)
        # TODO: check validity of result. Manual testing showed correct results but we dont know how to test yet.

        self.assertNotEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error replacing empty with None. Reason: \033[0m")
