import unittest
from unittest.mock import Mock

from numpy.ma.testutils import assert_equal

from pydpeet.io.device.arbin_8_00_PV221201.reader import read_sheets, to_dataframe


class ArbinTests(unittest.TestCase):
    def test_invalid_input_path(self):
        for value in ["invalid", None, ""]:
            try:
                _, _ = to_dataframe(value)
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


if __name__ == "__main__":
    unittest.main()
