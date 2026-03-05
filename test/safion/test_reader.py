import unittest

from pydpeet.io.device.safion_1_9.reader import to_dataframe
from test.utils import RES_PATH, with_zip_files


class MyTestCase(unittest.TestCase):
    def test_is_safion(self):
        zip_files_path = RES_PATH / "safion" / "for_readable_test" / "zipped_test_data"
        with_zip_files(zip_files_path, lambda file: to_dataframe(file))


if __name__ == "__main__":
    unittest.main()
