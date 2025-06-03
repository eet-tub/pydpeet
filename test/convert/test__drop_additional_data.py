import unittest
from pandas import DataFrame
from ppb.configs.config import STANDARD_COLUMNS
from ppb.convert import _drop_additional_data


class TestDropAdditionalData(unittest.TestCase):
    def test_standard_columns_only(self):
        data_frame = DataFrame(columns=STANDARD_COLUMNS)
        result = _drop_additional_data(data_frame)
        self.assertEqual(result.columns.tolist(), STANDARD_COLUMNS)

    def test_standard_and_additional_columns(self):
        data_frame = DataFrame(columns=STANDARD_COLUMNS + ['extra1', 'extra2'])
        result = _drop_additional_data(data_frame)
        self.assertEqual(result.columns.tolist(), STANDARD_COLUMNS)

    def test_additional_columns_only(self):
        data_frame = DataFrame(columns=['extra1', 'extra2'])
        result = _drop_additional_data(data_frame)
        self.assertEqual(result.columns.tolist(), [])

    def test_empty_data_frame(self):
        data_frame = DataFrame()
        result = _drop_additional_data(data_frame)
        self.assertEqual(result.columns.tolist(), [])

    def test_none_data_frame(self):
        data_frame = None
        with self.assertRaises(ValueError):
            _drop_additional_data(data_frame)


if __name__ == '__main__':
    unittest.main()
