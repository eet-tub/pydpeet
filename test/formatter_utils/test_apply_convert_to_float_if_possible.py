import unittest
from io import StringIO
from unittest.mock import patch

import pandas

from pydpeet.io.utils.formatter_utils import apply_convert_to_float_if_possible


class TestApplyConvertToFloatIfPossible(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_None_input(self, mock_stdout):
        data = None
        expected = None
        result = apply_convert_to_float_if_possible(data, "A")
        self.assertEqual(expected, result)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error applying convert_to_float_if_possible for A\033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_column_name_not_in_df(self, mock_stdout):
        data = pandas.DataFrame({"A": [1, 2, 3]})
        expected = pandas.DataFrame({"A": [1, 2, 3]})
        result = apply_convert_to_float_if_possible(data, "B")
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error applying convert_to_float_if_possible for B\033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_empty_dataframe(self, mock_stdout):
        data = pandas.DataFrame()
        expected = pandas.DataFrame()
        result = apply_convert_to_float_if_possible(data, "A")
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error applying convert_to_float_if_possible for B\033[0m\n")
