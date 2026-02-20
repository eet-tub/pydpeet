import unittest

from pydpeet.io.device.digatron_4_20_6_236 import reader
from pydpeet.io.device.digatron_eis_4_20_6_236 import reader as reader_eis
from test.utils import RES_PATH, with_zip_files


class MyTestCase(unittest.TestCase):
    def test_digatron(self):
        with_zip_files(RES_PATH / "digatron", lambda file: reader.to_dataframe(file))

    def test_digatron_eis(self):
        with_zip_files(RES_PATH / "digatron_eis", lambda file: reader_eis.to_dataframe(file))


if __name__ == "__main__":
    unittest.main()
