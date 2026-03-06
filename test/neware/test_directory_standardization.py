import sys
import unittest

from pydpeet.io.convert import convert_files_in_directory

sys.path.append(r"C:\Users\Anton\Nextcloud\Organisation\Arbeit\Projekte\PyDPEET\pydpeet_dev\pydpeet\test")

# from test.utils import with_zip_file_for_path, RES_PATH
from utils import RES_PATH, with_zip_file_for_path


class MyTestCase(unittest.TestCase):
    def test_neware(self):
        zip_file = RES_PATH / "neware" / "for_directory_standardization" / "data.zip"
        with_zip_file_for_path(
            zip_file,
            lambda input_path: convert_files_in_directory(
                "Neware", str(input_path), str(RES_PATH / "neware" / "for_directory_standardization" / "output"), True
            ),
        )


if __name__ == "__main__":
    unittest.main()
