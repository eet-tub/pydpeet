import unittest

from ppb.zyklisierer.digatron import reader
from ppb.zyklisierer.digatron_eis import reader as reader_eis
from test.utils import RES_PATH, with_zip_files


class MyTestCase(unittest.TestCase):
    def test_digatron(self):
        with_zip_files(RES_PATH / "digatron", lambda file: reader.to_DataFrame(file))

    def test_digatron_eis(self):
        with_zip_files(RES_PATH / "digatron_eis", lambda file: reader_eis.to_DataFrame(file))


if __name__ == '__main__':
    unittest.main()
