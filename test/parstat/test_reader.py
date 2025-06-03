import unittest

from ppb.zyklisierer.parstat.reader import to_DataFrame
from test.utils import with_zip_files, RES_PATH


class MyTestCase(unittest.TestCase):
    def test_parstat(self):
        zip_files_path = RES_PATH / "parstat" / "for_readable_test"
        with_zip_files(zip_files_path, lambda file: to_DataFrame(file))


if __name__ == '__main__':
    unittest.main()
