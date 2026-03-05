import unittest
from io import StringIO
from unittest.mock import patch

import pandas as pandas

from pydpeet.io.utils.formatter_utils import move_strings_from_column_to_metadata


class TestMoveStringsFromColumnToMetadata(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_move_strings_from_column_to_metadata(self, mock_stdout):
        data = pandas.DataFrame({"Floats+MSG": [1.1, "MSG", 3.3], "Meta_Data": ["Metadata_str", None, None]})
        expected = pandas.DataFrame({"Floats+MSG": [1.1, None, 3.3], "Meta_Data": ["Metadata_str\n\nMSG", None, None]}, dtype=object)
        column_name = "Floats+MSG"
        result = move_strings_from_column_to_metadata(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertNotEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error adding Messages to Metadata \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_data_frame_empty(self, mock_stdout):
        data = None
        expected = None
        column_name = "Floats+MSG"
        result = move_strings_from_column_to_metadata(data, column_name)
        self.assertEqual(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error adding Messages to Metadata \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_column_not_in_data_frame(self, mock_stdout):
        data = pandas.DataFrame({"Floats+MSG": [1.1, "MSG", 3.3], "Meta_Data": ["Metadata_str", None, None]})
        expected = pandas.DataFrame({"Floats+MSG": [1.1, "MSG", 3.3], "Meta_Data": ["Metadata_str", None, None]}, dtype=object)
        column_name = "NonExistingColumn"
        result = move_strings_from_column_to_metadata(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error adding Messages to Metadata \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_no_metadata_column(self, mock_stdout):
        data = pandas.DataFrame({"Floats+MSG": [1.1, "MSG", 3.3]})
        expected = pandas.DataFrame({"Floats+MSG": [1.1, "MSG", 3.3]}, dtype=object)
        column_name = "Floats+MSG"
        result = move_strings_from_column_to_metadata(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error adding Messages to Metadata \033[0m\n")

    @patch("sys.stdout", new_callable=StringIO)
    def test_collumn_no_str(self, mock_stdout):
        data = pandas.DataFrame({"Floats+MSG": [1.1, "MSG", 3.3], "Meta_Data": ["Metadata_str", None, None]})
        expected = pandas.DataFrame({"Floats+MSG": [1.1, "MSG", 3.3], "Meta_Data": ["Metadata_str", None, None]}, dtype=object)
        column_name = 1523
        result = move_strings_from_column_to_metadata(data, column_name)
        pandas.testing.assert_frame_equal(result, expected)
        self.assertEqual(mock_stdout.getvalue(), "\033[31mWARNING: Error adding Messages to Metadata \033[0m\n")
