import unittest

from pydpeet.io.device.parstat_2_63_3.reader import to_dataframe
from test.utils import RES_PATH, with_zip_files


class MyTestCase(unittest.TestCase):
    def test_parstat(self):
        zip_files_path = RES_PATH / "parstat" / "for_readable_test"
        with_zip_files(zip_files_path, lambda file: to_dataframe(file))


if __name__ == "__main__":
    unittest.main()
