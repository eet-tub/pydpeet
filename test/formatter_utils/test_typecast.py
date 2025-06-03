import unittest
from io import StringIO
from unittest.mock import patch

import pandas


from ppb.utils.formatter_utils import typecast


class TestTypecastFunction(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_typecast_to_int(self, mock_stdout):
        data = {'StepID': ["1", "2", "3"]}
        df = pandas.DataFrame(data)
        result = typecast(df, 'StepID', int)
        self.assertEqual(result['StepID'].dtype, int)
        column_name = 'StepID'
        datatype = int
        self.assertNotEqual(mock_stdout.getvalue(),
                            f"\033[31mWARNING: Error converting column:{column_name} to {datatype.__name__} \033[0m")

    @patch('sys.stdout', new_callable=StringIO)
    def test_typecast_to_float(self, mock_stdout):
        data = {'A': ['1.0', '2.0', '3.0']}
        df = pandas.DataFrame(data)
        result = typecast(df, 'A', float)
        self.assertEqual(result['A'].dtype, float)
        column_name = 'A'
        datatype = float
        self.assertNotEqual(mock_stdout.getvalue(),
                            f"\033[31mWARNING: Error converting column:{column_name} to {datatype.__name__} \033[0m")

    @patch('sys.stdout', new_callable=StringIO)
    def test_typecast_to_str(self, mock_stdout):
        data = {'A': [1, 2, 3]}
        df = pandas.DataFrame(data)
        result = typecast(df, 'A', str)
        self.assertEqual(result['A'].dtype, object)
        column_name = 'A'
        datatype = str
        self.assertNotEqual(mock_stdout.getvalue(),
                            f"\033[31mWARNING: Error converting column:{column_name} to {datatype.__name__} \033[0m")

    @patch('sys.stdout', new_callable=StringIO)
    def test_typecast_with_missing_column(self, mock_stdout):
        data = pandas.DataFrame({'A': [1, 2, 3]})
        expected = pandas.DataFrame({'A': [1, 2, 3]})
        result = typecast(data, 'B', int)
        pandas.testing.assert_frame_equal(result, expected)
        column_name = 'B'
        datatype = int
        self.assertEqual(mock_stdout.getvalue(),
                         f"\033[31mWARNING: Error converting column:{column_name} to {datatype.__name__}\033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_typecast_with_non_convertible_values(self, mock_stdout):
        data = {'A': ['a', 'b', 'c']}
        df = pandas.DataFrame(data)
        result = typecast(df, 'A', int)
        self.assertEqual(result['A'].dtype, object)
        column_name = 'A'
        datatype = int
        self.assertEqual(mock_stdout.getvalue(),
                         f"\033[31mWARNING: Error converting column:{column_name} to {datatype.__name__}\033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_typecast_with_empty_dataframe(self, mock_stdout):
        df = pandas.DataFrame()
        result = typecast(df, 'A', int)
        self.assertEqual(result.empty, True)
        column_name = 'A'
        datatype = int
        self.assertEqual(mock_stdout.getvalue(),
                         f"\033[31mWARNING: Error converting column:{column_name} to {datatype.__name__}\033[0m\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_typecast_with_not_string_column(self, mock_stdout):
        data = pandas.DataFrame({'A': [1, 2, 3]})
        expected = pandas.DataFrame({'A': [1, 2, 3]})
        result = typecast(data, 1, int)
        pandas.testing.assert_frame_equal(result, expected)
        column_name = 1
        datatype = int
        self.assertEqual(mock_stdout.getvalue(),
                         f"\033[31mWARNING: Error converting column:{column_name} to {datatype.__name__}\033[0m\n")

