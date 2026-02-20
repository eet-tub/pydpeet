import unittest
from io import StringIO
from unittest.mock import patch

import numpy as np
import pandas as pandas

from pydpeet.io.utils.formatter_utils import nan_to_none_in_column


class TestNanToNone(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_nan_to_none(self, mock_stdout):
        data = pandas.DataFrame({"A": [1, 2, np.nan]}, dtype=float)
        expected = pandas.DataFrame({"A": [1, 2, None]}, dtype=object)
        column_name = "A"
        result = nan_to_none_in_column(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(), f"\033[31mWARNING: Error fixing {column_name} (replacing NaN with None) \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_empty_column(self, mock_stdout):
        data = pandas.DataFrame({"A": []})
        expected = pandas.DataFrame({"A": []})
        column_name = "A"
        result = nan_to_none_in_column(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(), f"\033[31mWARNING: Error fixing {column_name} (replacing NaN with None) \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_empty_dataframe(self, mock_stdout):
        data = pandas.DataFrame()
        expected = pandas.DataFrame()
        column_name = "A"
        result = nan_to_none_in_column(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), f"\033[31mWARNING: Error fixing {column_name} (replacing NaN with None) \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_empty_column_name(self, mock_stdout):
        data = pandas.DataFrame({"A": [1, 2, 3]})
        expected = pandas.DataFrame({"A": [1, 2, 3]})
        column_name = None
        result = nan_to_none_in_column(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), f"\033[31mWARNING: Error fixing {column_name} (replacing NaN with None) \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_not_string_column_name(self, mock_stdout):
        data = pandas.DataFrame({"A": [1, 2, 3]})
        expected = pandas.DataFrame({"A": [1, 2, 3]})
        column_name = 13
        result = nan_to_none_in_column(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), f"\033[31mWARNING: Error fixing {column_name} (replacing NaN with None) \033[0m\n")
