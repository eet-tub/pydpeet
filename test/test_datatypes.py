import unittest
from pathlib import Path

from pydpeet.io.convert import Config, convert
from test.utils import RES_PATH, with_zip_files


class MyTestCase(unittest.TestCase):
    # Define the expected data types
    _EXPECTED_DATATYPES = {
        "Meta_Data": object,
        "Step_Count": int,
        "Voltage[V]": float,
        "Current[A]": float,
        "Temperature[\u00b0C]": float,
        "Test_Time[s]": float,
        "Date_Time": object,
        "EIS_f[Hz]": float,
        "EIS_Z_Real[Ohm]": float,
        "EIS_Z_Imag[Ohm]": float,
        "EIS_DC[A]": float,
    }

    def test_expected_datatypes_arbin(self):
        self._datatype_test(RES_PATH / "arbin" / "new", Config.Arbin)

    def test_expected_datatypes_arbin_old(self):
        self._datatype_test(RES_PATH / "arbin" / "old", Config.Arbin_4_23_PV090331)

    def test_expected_datatypes_basytec(self):
        self._datatype_test(RES_PATH / "basytec" / "for_datatype_test", Config.BaSyTec_6_3_1_0)

    def test_expected_datatypes_Digatron(self):
        self._datatype_test(RES_PATH / "digatron", Config.Digatron_4_20_6_236)

    def test_expected_datatypes_Digatron_EIS(self):
        self._datatype_test(RES_PATH / "digatron_eis", Config.Digatron_EIS_4_20_6_236)

    def test_expected_datatypes_Neware(self):
        self._datatype_test(RES_PATH / "neware" / "for_datatype_test", Config.Neware_8_0_0_516)

    def test_expected_datatypes_Parstat(self):
        self._datatype_test(RES_PATH / "parstat" / "for_datatype_test", Config.Parstat_2_63_3)

    def test_expected_datatypes_Safion(self):
        self._datatype_test(RES_PATH / "safion" / "for_datatype_test", Config.Safion_1_9)

    def test_expected_datatypes_Zahner_1(self):
        self._datatype_test(RES_PATH / "zahner" / "old" / "for_datatype_test" / "cfg1", Config.Zahner_1)

    def test_expected_datatypes_Zahner_2(self):
        self._datatype_test(RES_PATH / "zahner" / "old" / "for_datatype_test" / "cfg2", Config.Zahner_2)

    def test_expected_datatypes_Zahner_new_1(self):
        self._datatype_test(RES_PATH / "zahner" / "new" / "for_datatype_test" / "cfg1", Config.Zahner_new_1)

    def test_expected_datatypes_Zahner_new_2(self):
        self._datatype_test(RES_PATH / "zahner" / "new" / "for_datatype_test" / "cfg2", Config.Zahner_new_2)

    def test_expected_datatypes_Zahner_new_3(self):
        self._datatype_test(RES_PATH / "zahner" / "new" / "for_datatype_test" / "cfg3", Config.Zahner_new_3)

    def _datatype_test(self, input_path: Path, config: Config):
        with_zip_files(input_path, lambda file: self._validate_dataframe(convert(config, file, False)))

    def _validate_dataframe(self, df):
        errors = []
        for column, expected_type in self._EXPECTED_DATATYPES.items():
            # If the column is not in the DataFrame, skip -> already handled
            if column not in df.columns:
                continue

            # Test the type
            for entry in df[column]:
                if not (isinstance(entry, expected_type) or entry is None):
                    errors.append(
                        f"Entry in column '{column}' is not of expected type {expected_type.__name__} but {type(entry).__name__}"
                    )

        if errors:
            raise AssertionError("\n".join(errors))


if __name__ == "__main__":
    unittest.main()
