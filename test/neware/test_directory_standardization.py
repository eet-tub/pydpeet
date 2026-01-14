import unittest

from pydpeet.convert.configs.config import Config
from pydpeet.convert.directory_standardization import directory_standardization



import sys
from pathlib import Path

sys.path.append(r"C:\Users\Anton\Nextcloud\Organisation\Arbeit\Projekte\PyDPEET\pydpeet_dev\pydpeet\test")

# from test.utils import with_zip_file_for_path, RES_PATH
from utils import with_zip_file_for_path, RES_PATH


class MyTestCase(unittest.TestCase):
    def test_neware(self):
        zip_file = RES_PATH / "neware" / "for_directory_standardization" / "data.zip"
        with_zip_file_for_path(
            zip_file, lambda input_path: directory_standardization(
                'Neware',
                str(input_path),
                str(RES_PATH / "neware" / "for_directory_standardization" / "output"),
                True)
        )


if __name__ == '__main__':
    unittest.main()
