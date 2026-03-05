import unittest

from pydpeet.io.device.zahner.reader import to_dataframe
from pydpeet.io.device.zahner_new import reader as reader_new
from test.utils import RES_PATH, with_zip_files


class MyTestCase(unittest.TestCase):
    def test_zahner_old(self):
        zip_files_path = RES_PATH / "zahner" / "old" / "for_readable_test" / "ziped_test_data"
        with_zip_files(zip_files_path, lambda file: to_dataframe(file))

    def test_zahner_new(self):
        zip_files_path = RES_PATH / "zahner" / "new" / "for_readable_test" / "ziped_test_data"
        with_zip_files(zip_files_path, lambda file: reader_new.to_dataframe(file))


if __name__ == "__main__":
    unittest.main()
