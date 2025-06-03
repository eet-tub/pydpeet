import unittest

from ppb.zyklisierer.basytec.reader import to_DataFrame
from test.utils import with_zip_files, RES_PATH


class MyTestCase(unittest.TestCase):
    def test_is_readable(self):
        zip_files_path = RES_PATH / "basytec" / "for_readable_test" / "ziped_test_data"
        with_zip_files(zip_files_path, lambda file: to_DataFrame(file))
