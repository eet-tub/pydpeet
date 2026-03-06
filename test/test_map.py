from io import StringIO
from unittest import TestCase
from unittest.mock import patch

import pandas

from pydpeet.io.map import mapping

COLUMN_MAP = {
    "Record number": "Step_Count",
    "Voltage(V)": "Voltage[V]",
    "Current(A)": "Current[A]",
    "Relative Time(h:min:s.ms)": "Test_Time[s]",
    "Real Time(h:min:s.ms)": "Date_Time",
}

COLUMN_MAP_NONE = {}

COLUMN_MAP_INCOMPLETE = {"Record number": "Step_Count", "Voltage(V)": "Voltage[V]", "Current(A)": "Current[A]"}

COLUMN_MAP_TOO_MANY = {
    "Record number": "Step_Count",
    "Voltage(V)": "Voltage[V]",
    "Current(A)": "Current[A]",
    "Relative Time(h:min:s.ms)": "Test_Time[s]",
    "Real Time(h:min:s.ms)": "Date_Time",
    "TOO MANY": "TEST",
}


MISSING_REQUIRED_COLUMNS = ["Temperature[°C]", "EIS_f[Hz]", "EIS_Z_Real[Ohm]", "EIS_Z_Imag[Ohm]", "EIS_DC[A]"]

MISSING_REQUIRED_COLUMNS_NONE = []

MISSING_REQUIRED_COLUMNS_INCOMPLETE = [
    "Temperature[°C]",
    "EIS_f[Hz]",
]

MISSING_REQUIRED_COLUMNS_TOO_MANY = [
    "Temperature[°C]",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]",
    "TOO MANY",
]


class TestMap(TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_mapping_column_map_is_none(self, mock_stdout):
        data_frame = pandas.DataFrame(
            {
                "Record number": [1, 2, 3],
                "Voltage(V)": [1.1, 2.2, 3.3],
                "Current(A)": [4.4, 5.5, 6.6],
                "Relative Time(h:min:s.ms)": ["1:00:00", "2:00:00", "3:00:00"],
                "Real Time(h:min:s.ms)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00", "2020-01-01 02:00:00"],
                "Temperature( C)": [7.7, 8.8, 9.9],
                "EISFreq(Hz)": [10, 11, 12],
                "Zre(Ohm)": [13.1, 14.1, 15.1],
                "Zim(Ohm)": [16.1, 17.1, 18.1],
                "DC_Current(A)": [19.1, 20.1, 21.1],
            }
        )
        with self.assertRaises(ValueError):
            mapping(data_frame, None, MISSING_REQUIRED_COLUMNS)

    def test_mapping_missing_column_is_none(self):
        data_frame = pandas.DataFrame(
            {
                "Record number": [1, 2, 3],
                "Voltage(V)": [1.1, 2.2, 3.3],
                "Current(A)": [4.4, 5.5, 6.6],
                "Relative Time(h:min:s.ms)": ["1:00:00", "2:00:00", "3:00:00"],
                "Real Time(h:min:s.ms)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00", "2020-01-01 02:00:00"],
                "Temperature( C)": [7.7, 8.8, 9.9],
                "EISFreq(Hz)": [10, 11, 12],
                "Zre(Ohm)": [13.1, 14.1, 15.1],
                "Zim(Ohm)": [16.1, 17.1, 18.1],
                "DC_Current(A)": [19.1, 20.1, 21.1],
            }
        )
        with self.assertRaises(ValueError):
            mapping(data_frame, COLUMN_MAP, None)

    def test_mapping_data_frame_is_none(self):
        data_frame = None
        with self.assertRaises(ValueError):
            mapping(data_frame, COLUMN_MAP, MISSING_REQUIRED_COLUMNS)

    @patch("sys.stdout", new_callable=StringIO)
    def test_mapping_column_map_is_not_dict(self, mock_stdout):
        data_frame = pandas.DataFrame(
            {
                "Record number": [1, 2, 3],
                "Voltage(V)": [1.1, 2.2, 3.3],
                "Current(A)": [4.4, 5.5, 6.6],
                "Relative Time(h:min:s.ms)": ["1:00:00", "2:00:00", "3:00:00"],
                "Real Time(h:min:s.ms)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00", "2020-01-01 02:00:00"],
                "Temperature( C)": [7.7, 8.8, 9.9],
                "EISFreq(Hz)": [10, 11, 12],
                "Zre(Ohm)": [13.1, 14.1, 15.1],
                "Zim(Ohm)": [16.1, 17.1, 18.1],
                "DC_Current(A)": [19.1, 20.1, 21.1],
            }
        )
        with self.assertRaises(ValueError):
            mapping(data_frame, 1, MISSING_REQUIRED_COLUMNS)

    def test_mapping_missing_column_is_not_list(self):
        data_frame = pandas.DataFrame(
            {
                "Record number": [1, 2, 3],
                "Voltage(V)": [1.1, 2.2, 3.3],
                "Current(A)": [4.4, 5.5, 6.6],
                "Relative Time(h:min:s.ms)": ["1:00:00", "2:00:00", "3:00:00"],
                "Real Time(h:min:s.ms)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00", "2020-01-01 02:00:00"],
                "Temperature( C)": [7.7, 8.8, 9.9],
                "EISFreq(Hz)": [10, 11, 12],
                "Zre(Ohm)": [13.1, 14.1, 15.1],
                "Zim(Ohm)": [16.1, 17.1, 18.1],
                "DC_Current(A)": [19.1, 20.1, 21.1],
            }
        )
        with self.assertRaises(ValueError):
            mapping(data_frame, COLUMN_MAP, 1)

    def test_mapping_data_frame_is_not_data_frame(self):
        data_frame = 1
        with self.assertRaises(ValueError):
            mapping(data_frame, COLUMN_MAP, MISSING_REQUIRED_COLUMNS)

    def test_not_all_values_in_map_and_missing_columns(self):
        data_frame = pandas.DataFrame(
            {
                "Record number": [1, 2, 3],
                "Voltage(V)": [1.1, 2.2, 3.3],
                "Current(A)": [4.4, 5.5, 6.6],
                "Relative Time(h:min:s.ms)": ["1:00:00", "2:00:00", "3:00:00"],
                "Real Time(h:min:s.ms)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00", "2020-01-01 02:00:00"],
                "Temperature( C)": [7.7, 8.8, 9.9],
                "EISFreq(Hz)": [10, 11, 12],
                "Zre(Ohm)": [13.1, 14.1, 15.1],
                "Zim(Ohm)": [16.1, 17.1, 18.1],
                "DC_Current(A)": [19.1, 20.1, 21.1],
            }
        )
        with self.assertRaises(ValueError):
            mapping(data_frame, COLUMN_MAP_INCOMPLETE, MISSING_REQUIRED_COLUMNS_INCOMPLETE)

    def test_not_all_values_in_map(self):
        data_frame = pandas.DataFrame(
            {
                "Record number": [1, 2, 3],
                "Voltage(V)": [1.1, 2.2, 3.3],
                "Current(A)": [4.4, 5.5, 6.6],
                "Relative Time(h:min:s.ms)": ["1:00:00", "2:00:00", "3:00:00"],
                "Real Time(h:min:s.ms)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00", "2020-01-01 02:00:00"],
                "Temperature( C)": [7.7, 8.8, 9.9],
                "EISFreq(Hz)": [10, 11, 12],
                "Zre(Ohm)": [13.1, 14.1, 15.1],
                "Zim(Ohm)": [16.1, 17.1, 18.1],
                "DC_Current(A)": [19.1, 20.1, 21.1],
            }
        )
        with self.assertRaises(ValueError):
            mapping(data_frame, COLUMN_MAP_INCOMPLETE, MISSING_REQUIRED_COLUMNS)

    def test_not_all_values_inmissing_columns(self):
        data_frame = pandas.DataFrame(
            {
                "Record number": [1, 2, 3],
                "Voltage(V)": [1.1, 2.2, 3.3],
                "Current(A)": [4.4, 5.5, 6.6],
                "Relative Time(h:min:s.ms)": ["1:00:00", "2:00:00", "3:00:00"],
                "Real Time(h:min:s.ms)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00", "2020-01-01 02:00:00"],
                "Temperature( C)": [7.7, 8.8, 9.9],
                "EISFreq(Hz)": [10, 11, 12],
                "Zre(Ohm)": [13.1, 14.1, 15.1],
                "Zim(Ohm)": [16.1, 17.1, 18.1],
                "DC_Current(A)": [19.1, 20.1, 21.1],
            }
        )
        with self.assertRaises(ValueError):
            mapping(data_frame, COLUMN_MAP, MISSING_REQUIRED_COLUMNS_INCOMPLETE)

    def test_too_many_columns(self):
        data_frame = pandas.DataFrame(
            {
                "Record number": [1, 2, 3],
                "Voltage(V)": [1.1, 2.2, 3.3],
                "Current(A)": [4.4, 5.5, 6.6],
                "Relative Time(h:min:s.ms)": ["1:00:00", "2:00:00", "3:00:00"],
                "Real Time(h:min:s.ms)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00", "2020-01-01 02:00:00"],
                "Temperature( C)": [7.7, 8.8, 9.9],
                "EISFreq(Hz)": [10, 11, 12],
                "Zre(Ohm)": [13.1, 14.1, 15.1],
                "Zim(Ohm)": [16.1, 17.1, 18.1],
                "DC_Current(A)": [19.1, 20.1, 21.1],
            }
        )
        with self.assertRaises(ValueError):
            mapping(data_frame, COLUMN_MAP_TOO_MANY, MISSING_REQUIRED_COLUMNS)
