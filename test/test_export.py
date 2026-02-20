import shutil
import unittest
from pandas import DataFrame
from unittest.mock import patch
from io import StringIO
from pydpeet.io.configs.config import DataOutputFiletype
from pydpeet.io.write import write
from test.utils import TEMP_PATH


class TestExportFunction(unittest.TestCase):
    OUTPUT_PATH = TEMP_PATH / 'output'
    OUTPUT_PATH_STR = str(OUTPUT_PATH)

    def test_dataframe_is_none(self):
        df = None
        output_file_name = 'test_file'
        with self.assertRaises(ValueError):
            write(df, self.OUTPUT_PATH_STR, output_file_name)

    @patch('sys.stdout', new_callable=StringIO)
    def test_valid_export(self, mock_stdout):
        df = DataFrame({'A': [1, 2, 3]})
        output_file_name = 'test_file'
        write(df, self.OUTPUT_PATH_STR, output_file_name)
        output_file_path = self.OUTPUT_PATH / output_file_name
        self.assertTrue((self.OUTPUT_PATH / (output_file_name + '_Data.parquet')).exists())
        self.assertEqual(mock_stdout.getvalue(), f"exporting to {output_file_path}\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_dataframe(self, mock_stdout):
        data_frame = 'not a dataframe'
        output_file_name = 'test_file'
        with self.assertRaises(TypeError):
            write(data_frame, self.OUTPUT_PATH_STR, output_file_name)
        self.assertEqual(mock_stdout.getvalue(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_output_path(self, mock_stdout):
        df = DataFrame({'A': [1, 2, 3]})
        output_file_name = 'test_file'
        with self.assertRaises(ValueError):
            write(df, 123, output_file_name)
        self.assertEqual(mock_stdout.getvalue(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_data_output_filetype(self, mock_stdout):
        df = DataFrame({'A': [1, 2, 3]})
        output_file_name = 'test_file'
        with self.assertRaises(ValueError):
            write(df, self.OUTPUT_PATH_STR, output_file_name, data_output_filetype=' invalid')
        self.assertEqual(mock_stdout.getvalue(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_non_existent_output_directory(self, mock_stdout):
        df = DataFrame({'A': [1, 2, 3]})
        output_file_name = 'test_file'
        write(df, self.OUTPUT_PATH_STR, output_file_name, data_output_filetype=DataOutputFiletype.parquet)
        output_file_path = self.OUTPUT_PATH / output_file_name
        self.assertEqual(mock_stdout.getvalue(), f"exporting to {output_file_path}\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_existing_output_directory(self, mock_stdout):
        df = DataFrame({'A': [1, 2, 3]})
        output_file_name = 'test_file'
        output_file_path = self.OUTPUT_PATH / output_file_name
        write(df, self.OUTPUT_PATH_STR, output_file_name)
        self.assertTrue((self.OUTPUT_PATH / (output_file_name + '_Data.parquet')).exists())
        self.assertEqual(mock_stdout.getvalue(), f"exporting to {output_file_path}\n")

    def tearDown(self):
        shutil.rmtree(TEMP_PATH, ignore_errors=True)
