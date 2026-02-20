import unittest
from io import StringIO
from unittest.mock import patch

import pandas

from pydpeet.io.utils.formatter_utils import testtime_hours_to_seconds_direct


class TestTesttimeHoursToSecondsDirect(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_df_is_none(self, mock_stdout):
        data = None
        expected = None
        result = testtime_hours_to_seconds_direct(data)
        self.assertEqual(expected, result)
        self.assertEqual(mock_stdout.getvalue(),
                         "\033[31mWARNING: Error fixing Testtime[s] (converting hours to seconds). Reason: dataFrame is None \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_df_is_empty(self, mock_stdout):
        data = pandas.DataFrame()
        expected = pandas.DataFrame()
        result = testtime_hours_to_seconds_direct(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertEqual(mock_stdout.getvalue(),
                         "\033[31mWARNING: Error fixing Testtime[s] (converting hours to seconds). Reason: Testtime[s] is not in dataFrame.columns \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_testtime_is_not_in_df(self, mock_stdout):
        data = pandas.DataFrame({'A': ['1:30']})
        expected = pandas.DataFrame({'A': ['1:30']})
        result = testtime_hours_to_seconds_direct(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertEqual(mock_stdout.getvalue(),
                         "\033[31mWARNING: Error fixing Testtime[s] (converting hours to seconds). Reason: Testtime[s] is not in dataFrame.columns \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_testtime_is_empty(self, mock_stdout):
        data = pandas.DataFrame({'Testtime[s]': [""],
                                 'A': [2.0]})
        expected = pandas.DataFrame({'Testtime[s]': [""],
                                     'A': [2.0]
                                     })
        result = testtime_hours_to_seconds_direct(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertNotEqual(mock_stdout.getvalue(),
                         "\033[31mWARNING: Error fixing Testtime[s] (converting hours to seconds). Reason: could not convert string to float: '' \033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_convert_testtime(self, mock_stdout):
        data = pandas.DataFrame({'Testtime[s]': [25.5]})
        expected = pandas.DataFrame({'Testtime[s]': [91800.0]})
        result = testtime_hours_to_seconds_direct(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertNotEqual(mock_stdout.getvalue(),
                         "\033[31mWARNING: Error fixing Testtime[s] (converting hours to seconds). Reason: Testtime[s] is empty can't apply time_to_seconds \033[0m\n")
