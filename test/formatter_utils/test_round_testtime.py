import unittest
from io import StringIO
from unittest.mock import patch

import pandas

from pydpeet.io.utils.formatter_utils import round_testtime


class TestRoundTesttime(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_df_is_none(self, mock_stdout):
        data = None
        expected = None
        result = round_testtime(data)
        self.assertEqual(expected, result)
        self.assertEqual(
            mock_stdout.getvalue(),
            "\033[31mWARNING: Error fixing Test_Time[s] (rounding). Reason: dataFrame is None \033[0m\n",
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_df_is_empty(self, mock_stdout):
        data = pandas.DataFrame()
        expected = pandas.DataFrame()
        result = round_testtime(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertEqual(
            mock_stdout.getvalue(),
            "\033[31mWARNING: Error fixing Test_Time[s] (rounding). Reason: dataframe is empty \033[0m\n",
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_rounding_testtime_as_str(self, mock_stdout):
        data = pandas.DataFrame({"Test_Time[s]": ["12.56416565165", "255.16816586565416546"]})
        expected = pandas.DataFrame({"Test_Time[s]": [12.56417, 255.168175]})
        result = round_testtime(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertNotEqual(
            mock_stdout.getvalue(),
            "\033[31mWARNING: Error fixing Test_Time[s] (rounding). Reason: dataframe is empty \033[0m\n",
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_rounding_testtime(self, mock_stdout):
        data = pandas.DataFrame({"Test_Time[s]": [12.56416565165, 255.16816586565416546]})
        expected = pandas.DataFrame({"Test_Time[s]": [12.56417, 255.168175]})
        result = round_testtime(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertNotEqual(
            mock_stdout.getvalue(),
            "\033[31mWARNING: Error fixing Test_Time[s] (rounding). Reason: dataframe is empty \033[0m\n",
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_rounding_testtime_as_int(self, mock_stdout):
        data = pandas.DataFrame({"Test_Time[s]": [12, 255]})
        expected = pandas.DataFrame({"Test_Time[s]": [12.0, 255.0]})
        result = round_testtime(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertNotEqual(
            mock_stdout.getvalue(),
            "\033[31mWARNING: Error fixing Test_Time[s] (rounding). Reason: dataframe is empty \033[0m\n",
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_rounding_testtime_as_str_wrong_format(self, mock_stdout):
        data = pandas.DataFrame({"Test_Time[s]": ["abc", "bca"]})
        expected = pandas.DataFrame({"Test_Time[s]": ["abc", "bca"]})
        result = round_testtime(data)
        pandas.testing.assert_frame_equal(expected, result)
        self.assertEqual(
            mock_stdout.getvalue(),
            "\033[31mWARNING: Error fixing Test_Time[s] (rounding). Reason: could not convert string to float: 'abc' \033[0m\n",
        )
