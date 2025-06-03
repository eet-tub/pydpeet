import unittest

from ppb.configs.config import Config
from ppb.directory_standardization import directory_standardization
from test.utils import with_zip_file_for_path, RES_PATH


class MyTestCase(unittest.TestCase):
    def test_neware(self):
        zip_file = RES_PATH / "neware" / "for_directory_standardization" / "data.zip"
        with_zip_file_for_path(
            zip_file, lambda input_path: directory_standardization(
                Config.Neware,
                str(input_path),
                str(RES_PATH / "neware" / "for_directory_standardization" / "output"),
                True)
        )


if __name__ == '__main__':
    unittest.main()
