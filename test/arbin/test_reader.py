import unittest
from unittest.mock import Mock

from numpy.ma.testutils import assert_equal
from ppb.zyklisierer.arbin.reader import to_DataFrame, read_sheets


class ArbinTests(unittest.TestCase):
    def test_invalid_input_path(self):

        for value in ["invalid", None, ""]:
            try:
                _, _ = to_DataFrame(value)
                self.fail()
            except FileNotFoundError:
                pass
            except ValueError:
                pass

    def test_read_sheets(self):
        mock_obj = Mock()
        mock_obj.sheet_names = []

        df, md = read_sheets(mock_obj)

        assert_equal(df, None)
        assert_equal(md, "")


if __name__ == '__main__':
    unittest.main()
