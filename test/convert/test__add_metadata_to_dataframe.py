import unittest

from pandas import DataFrame

from pydpeet.io.convert import _add_metadata_to_dataframe


class TestAddMetadataToDataFrame(unittest.TestCase):
    def test_none_data_frame(self):
        with self.assertRaises(ValueError):
            _add_metadata_to_dataframe(None, "test metadata")

    def test_valid_input(self):
        data_frame = DataFrame({"A": [1, 2, 3]})
        meta_data = "test metadata"
        actual = _add_metadata_to_dataframe(data_frame, meta_data)["Meta_Data"][0]
        self.assertEqual(actual, meta_data)

    def test_non_string_metadata(self):
        data_frame = DataFrame({"A": [1, 2, 3]})
        meta_data = 123
        actual = _add_metadata_to_dataframe(data_frame, meta_data)["Meta_Data"][0]
        self.assertEqual(actual, str(meta_data))

    def test_empty_metadata(self):
        data_frame = DataFrame({"A": [1, 2, 3]})
        meta_data = ""
        actual = _add_metadata_to_dataframe(data_frame, meta_data)["Meta_Data"][0]
        self.assertEqual(actual, meta_data)

    def test_only_one_row__of_metadata(self):
        data_frame = DataFrame({"A": [1, 2, 3]})
        meta_data = "test metadata"
        actual = _add_metadata_to_dataframe(data_frame, meta_data)["Meta_Data"].iloc[1::]
        self.assertTrue(all(row is None for row in actual))


if __name__ == "__main__":
    unittest.main()
