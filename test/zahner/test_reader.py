import unittest

from ppb.zyklisierer.zahner.reader import to_DataFrame
from ppb.zyklisierer.zahner_new import reader as reader_new
from test.utils import with_zip_files, RES_PATH


class MyTestCase(unittest.TestCase):
    def test_zahner_old(self):
        zip_files_path = RES_PATH / "zahner" / "old" / "for_readable_test" / "ziped_test_data"
        with_zip_files(zip_files_path, lambda file: to_DataFrame(file))

    def test_zahner_new(self):
        zip_files_path = RES_PATH / "zahner" / "new" / "for_readable_test" / "ziped_test_data"
        with_zip_files(zip_files_path, lambda file: reader_new.to_DataFrame(file))


if __name__ == '__main__':
    unittest.main()
