import unittest

from pandas.testing import assert_index_equal
from pandas import Index

from pydpeet.io.configs.config import STANDARD_COLUMNS
from pydpeet.io.convert import _rename_duplicate_extra_columns


class TestRenameDuplicateExtraColumns(unittest.TestCase):
    def test_no_duplicates(self):
        expected = Index(['A', 'B', 'C'])
        actual = _rename_duplicate_extra_columns(Index(['A', 'B', 'C']))
        assert_index_equal(expected, actual)

    def test_single_duplicate(self):
        expected = Index(['A', 'B', 'B_1'])
        actual = _rename_duplicate_extra_columns(Index(['A', 'B', 'B']))
        assert_index_equal(actual, expected)

    def test_multiple_duplicates(self):
        expected = Index(['A', 'B', 'B_1', 'C', 'C_1', 'C_2'])
        actual = _rename_duplicate_extra_columns(Index(['A', 'B', 'B', 'C', 'C', 'C']))
        assert_index_equal(actual, expected)

    def test_no_extra_columns(self):
        expected = Index([STANDARD_COLUMNS[0], STANDARD_COLUMNS[1]])
        actual = _rename_duplicate_extra_columns(Index([STANDARD_COLUMNS[0], STANDARD_COLUMNS[1]]))
        assert_index_equal(actual, expected)

    def test_single_duplicate_with_STANDARD_COLUMNS(self):
        expected = Index([STANDARD_COLUMNS[0], 'A', 'A_1', STANDARD_COLUMNS[1]])
        actual = _rename_duplicate_extra_columns(Index([STANDARD_COLUMNS[0], 'A', 'A', STANDARD_COLUMNS[1]]))
        assert_index_equal(actual, expected)

    def test_multiple_duplicates_with_STANDARD_COLUMNS(self):
        expected = Index([STANDARD_COLUMNS[0], 'B', 'B_1', 'C', 'C_1', 'C_2', STANDARD_COLUMNS[1]])
        actual = _rename_duplicate_extra_columns(Index([STANDARD_COLUMNS[0], 'B', 'B', 'C', 'C', 'C', STANDARD_COLUMNS[1]]))
        assert_index_equal(actual, expected)

    def test_empty_columns(self):
        expected = Index([])
        actual = _rename_duplicate_extra_columns(Index([]))
        assert_index_equal(actual, expected)


if __name__ == '__main__':
    unittest.main()
