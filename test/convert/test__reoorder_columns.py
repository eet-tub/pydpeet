import unittest

from pandas import DataFrame

from pydpeet.io.configs.config import STANDARD_COLUMNS
from pydpeet.io.convert import _reorder_columns


class TestReorderColumns(unittest.TestCase):
    def test_none_data_frame(self):
        with self.assertRaises(ValueError):
            _reorder_columns(None)

    def test_empty_data_frame(self):
        with self.assertRaises(ValueError):
            _reorder_columns(DataFrame())

    def test_data_frame_with_no_columns(self):
        with self.assertRaises(ValueError):
            _reorder_columns(DataFrame(columns=[]))

    def test_data_frame_with_standard_columns_only(self):
        data_frame = DataFrame(columns=STANDARD_COLUMNS)
        reordered = _reorder_columns(data_frame)
        self.assertEqual(reordered.columns.tolist(), STANDARD_COLUMNS)

    def test_data_frame_with_extra_columns_only(self):
        data_frame = DataFrame(columns=["extra1", "extra2"])
        reordered = _reorder_columns(data_frame)
        self.assertEqual(reordered.columns.tolist(), ["extra1", "extra2"])

    def test_data_frame_with_both_standard_and_extra_columns(self):
        data_frame = DataFrame(columns=STANDARD_COLUMNS + ["extra1", "extra2"])
        reordered = _reorder_columns(data_frame)
        self.assertEqual(reordered.columns.tolist(), STANDARD_COLUMNS + ["extra1", "extra2"])

    def test_data_frame_with_duplicate_extra_columns(self):
        data_frame = DataFrame(columns=["extra1", "extra1", "extra2"])
        reordered = _reorder_columns(data_frame)
        self.assertEqual(reordered.columns.tolist(), ["extra1", "extra1_1", "extra2"])

    def test_data_frame_with_duplicate_extra_columns_values(self):
        data = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        data_frame = DataFrame(data=data, columns=["extra1", "extra1", "extra2"])
        reordered = _reorder_columns(data_frame)
        self.assertEqual(reordered.columns.tolist(), ["extra1", "extra1_1", "extra2"])
        self.assertEqual(reordered["extra1"].tolist(), [1, 2, 3])
        self.assertEqual(reordered["extra1_1"].tolist(), [4, 5, 6])
        self.assertEqual(reordered["extra2"].tolist(), [7, 8, 9])


if __name__ == "__main__":
    unittest.main()
