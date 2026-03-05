import unittest
from io import StringIO
from unittest.mock import patch

import pandas

from pydpeet.io.utils.formatter_utils import testtime_hours_to_seconds_with_string_interpretation


class TestTesttimeHoursToSecondsWithStringInterpretation(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_with_none(self, mock_stdout):
        data = None
        expected = None
        result = testtime_hours_to_seconds_with_string_interpretation(data, False)
        self.assertEqual(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error fixing Testtime[s] \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_with_no_testtime(self, mock_stdout):
        data = pandas.DataFrame({"A": [1, 2, 3]})
        expected = pandas.DataFrame({"A": [1, 2, 3]})
        result = testtime_hours_to_seconds_with_string_interpretation(data, False)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error fixing Testtime[s] \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_empty_column(self, mock_stdout):
        data = pandas.DataFrame({"Test_Time[s]": []})
        expected = pandas.DataFrame({"Test_Time[s]": []})
        result = testtime_hours_to_seconds_with_string_interpretation(data, False)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error fixing Testtime[s] \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_astype_string_not_bool(self, mock_stdout):
        data = pandas.DataFrame({"Test_Time[s]": [1, 2, 3]})
        expected = pandas.DataFrame({"Test_Time[s]": [1, 2, 3]})
        result = testtime_hours_to_seconds_with_string_interpretation(data, 25.1337)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error fixing Testtime[s] \033[0m\n")
