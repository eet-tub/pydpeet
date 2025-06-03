import unittest
from pathlib import Path

from ppb.convert import convert, Config

from test.utils import RES_PATH, with_zip_files


class MyTestCase(unittest.TestCase):
    # Define the expected data types
    _EXPECTED_DATATYPES = {
        "Metadata": object,
        "StepID": int,
        "Voltage[V]": float,
        "Current[A]": float,
        "Temperature[\u00b0C]": float,
        "Testtime[s]": float,
        "Absolute Time[yyyy-mm-dd hh:mm:ss]": object,
        "EISFreq[Hz]": float,
        "Zre[Ohm]": float,
        "Zim[Ohm]": float,
        "DC_Current[A]": float,
    }

    def test_expected_datatypes_arbin(self):
        self._datatype_test(RES_PATH / "arbin" / "new", Config.Arbin)

    def test_expected_datatypes_arbin_old(self):
        self._datatype_test(RES_PATH / "arbin" / "old", Config.Arbin_Old)

    def test_expected_datatypes_basytec(self):
        self._datatype_test(RES_PATH / "basytec" / "for_datatype_test", Config.BaSyTec)

    def test_expected_datatypes_Digatron(self):
        self._datatype_test(RES_PATH / "digatron", Config.Digatron)

    def test_expected_datatypes_Digatron_EIS(self):
        self._datatype_test(RES_PATH / "digatron_eis", Config.Digatron_EIS)

    def test_expected_datatypes_Neware(self):
        self._datatype_test(RES_PATH / "neware" / "for_datatype_test", Config.Neware)

    def test_expected_datatypes_Parstat(self):
        self._datatype_test(RES_PATH / "parstat" / "for_datatype_test", Config.Parstat)

    def test_expected_datatypes_Safion(self):
        self._datatype_test(RES_PATH / "safion" / "for_datatype_test", Config.Safion)

    def test_expected_datatypes_Zahner_1(self):
        self._datatype_test(RES_PATH / "zahner" / "old" / "for_datatype_test" / "cfg1", Config.Zahner_1)

    def test_expected_datatypes_Zahner_2(self):
        self._datatype_test(RES_PATH / "zahner" / "old" /"for_datatype_test" / "cfg2", Config.Zahner_2)

    def test_expected_datatypes_Zahner_new_1(self):
        self._datatype_test(RES_PATH / "zahner" / "new" /"for_datatype_test" / "cfg1", Config.Zahner_new_1)

    def test_expected_datatypes_Zahner_new_2(self):
        self._datatype_test(RES_PATH / "zahner" / "new" /"for_datatype_test" / "cfg2", Config.Zahner_new_2)

    def test_expected_datatypes_Zahner_new_3(self):
        self._datatype_test(RES_PATH / "zahner" / "new" /"for_datatype_test" / "cfg3", Config.Zahner_new_3)

    def _datatype_test(self, input_path: Path, config: Config):
        with_zip_files(
            input_path,
            lambda file: self._validate_dataframe(
                convert(config, file, False)
            )
        )

    def _validate_dataframe(self, df):
        errors = []
        for column, expected_type in self._EXPECTED_DATATYPES.items():
            # If the column is not in the DataFrame, skip -> already handled
            if column not in df.columns:
                continue

            # Test the type
            for entry in df[column]:
                if not (isinstance(entry, expected_type) or entry is None):
                    errors.append(f"Entry in column '{column}' is not of expected type {expected_type.__name__} but {type(entry).__name__}")

        if errors:
            raise AssertionError("\n".join(errors))



if __name__ == "__main__":
    unittest.main()
