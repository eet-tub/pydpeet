import unittest
import pandas as pandas
from pydpeet.io.utils.formatter_utils import fix_time_format
from unittest.mock import patch
from io import StringIO

class TestFixTimeFormat(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_dataframe_none(self, mock_stdout):
        data = None
        expected = None
        result = fix_time_format(data, input_format='%d.%m.%Y %H:%M:%S')
        self.assertEqual(result, expected)
        self.assertEqual(mock_stdout.getvalue(),
                         "\033[31mWARNING: Error fixing timeformat Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_missing_absolute_time(self, mock_stdout):
        data = pandas.DataFrame({"A": [1, 2, 3]})
        expected = pandas.DataFrame({"A": [1, 2, 3]})
        result = fix_time_format(data, input_format='%d.%m.%Y %H:%M:%S')
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(),
                         "\033[31mWARNING: Error fixing timeformat Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_fix_time_format_empty_column(self, mock_stdout):
        data = pandas.DataFrame({'Absolute Time[yyyy-mm-dd hh:mm:ss]': []}, dtype=object)
        expected = pandas.DataFrame({'Absolute Time[yyyy-mm-dd hh:mm:ss]': []}, dtype=object)
        result = fix_time_format(data, input_format='%d.%m.%Y %H:%M:%S')
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(),
                            "\033[31mWARNING: Error fixing timeformat Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_fix_time_format_empty_values_in_column(self, mock_stdout):
        data = pandas.DataFrame({'Absolute Time[yyyy-mm-dd hh:mm:ss]': ["29.06.2022 16:54:14", ""]})
        expected = pandas.DataFrame({'Absolute Time[yyyy-mm-dd hh:mm:ss]': ["2022-06-29 16:54:14", pandas.NaT]})
        result = fix_time_format(data, input_format='%d.%m.%Y %H:%M:%S')
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(),
                            "\033[31mWARNING: Error fixing timeformat Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_correct_data(self, mock_stdout):
        data = pandas.DataFrame({'Absolute Time[yyyy-mm-dd hh:mm:ss]': ["29.06.2022 16:54:14"]})
        expected = pandas.DataFrame({'Absolute Time[yyyy-mm-dd hh:mm:ss]': ["2022-06-29 16:54:14"]}, dtype=object)
        result = fix_time_format(data, input_format='%d.%m.%Y %H:%M:%S')
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(),
                            "\033[31mWARNING: Error fixing timeformat Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_incorrect_data(self, mock_stdout):
        data = pandas.DataFrame({'Absolute Time[yyyy-mm-dd hh:mm:ss]': ["29.06.2022 16:54:14"]})
        expected = pandas.DataFrame({'Absolute Time[yyyy-mm-dd hh:mm:ss]': ["29.06.2022 16:54:14"]}, dtype=object)
        result = fix_time_format(data, input_format='%d.%m.%Y %H:%M:%S.%MS')
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(),
                         "\033[31mWARNING: Error fixing timeformat Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m\n")
