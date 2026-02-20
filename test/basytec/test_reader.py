import unittest

from pydpeet.io.device.basytec_6_3_1_0.reader import to_dataframe
from test.utils import RES_PATH, with_zip_files


class MyTestCase(unittest.TestCase):
    def test_is_readable(self):
        zip_files_path = RES_PATH / "basytec" / "for_readable_test" / "ziped_test_data"
        with_zip_files(zip_files_path, lambda file: to_dataframe(file))
