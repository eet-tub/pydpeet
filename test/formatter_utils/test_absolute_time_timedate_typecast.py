import unittest
from io import StringIO
from unittest.mock import patch

import pandas as pandas

from pydpeet.io.utils.formatter_utils import absolute_time_timedate_typecast


class TestAbsoluteTimeTimedateTypecast(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_dataframe_none(self, mock_stdout):
        data = None
        expected = None
        result = absolute_time_timedate_typecast(data)
        self.assertEqual(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error typecasting Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_no_absolutetime_column(self, mock_stdout):
        data = pandas.DataFrame({"A": [1, 2, 3]})
        expected = pandas.DataFrame({"A": [1, 2, 3]})
        result = absolute_time_timedate_typecast(data)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error typecasting Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_absolutetime_column_empty(self, mock_stdout):
        data = pandas.DataFrame({"Absolute Time[yyyy-mm-dd hh:mm:ss]": []})
        expected = pandas.DataFrame({"Absolute Time[yyyy-mm-dd hh:mm:ss]": []}, dtype="datetime64[ns]")
        result = absolute_time_timedate_typecast(data)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error typecasting Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")
