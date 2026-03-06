import unittest
from unittest.mock import patch

from pandas import DataFrame
from utils import mock_config

from pydpeet.io.configs.config import MAPPER_CONFIGS, Config
from pydpeet.io.convert import _column_mapping


class TestColumnMapping(unittest.TestCase):
    def test_data_frame_none(self):
        config = Config.BaSyTec_6_3_1_0
        with self.assertRaises(ValueError):
            _column_mapping(None, config)

    @patch("ppb.convert.mapping")
    def test_config_in_mapper_configs(self, mock_mapping):
        config = Config.BaSyTec_6_3_1_0
        data_frame = DataFrame()
        column_map = {"a": "b"}
        missing_required_columns = ["c"]
        MAPPER_CONFIGS[config] = (column_map, missing_required_columns)
        result = _column_mapping(data_frame, config)
        mock_mapping.assert_called_with(data_frame, column_map, missing_required_columns)
        self.assertEqual(result, mock_mapping.return_value)

    def test_config_not_in_mapper_configs(self):
        data_frame = DataFrame()
        with self.assertRaises(ValueError):
            _column_mapping(data_frame, mock_config())

    def test_custom_config_without_custom_folder(self):
        config = Config.Custom
        data_frame = DataFrame()
        with self.assertRaises(ValueError):
            _column_mapping(data_frame, config)

    @patch("ppb.convert.ExtPath.is_not_valid")
    def test_custom_config_with_invalid_custom_folder(self, mock_is_not_valid):
        config = Config.Custom
        data_frame = DataFrame()
        custom_folder = "invalid_folder"
        mock_is_not_valid.return_value = True
        with self.assertRaises(ValueError):
            _column_mapping(data_frame, config, custom_folder)

    @patch("pathlib.Path.is_dir")
    def test_custom_config_with_custom_folder_not_a_directory(self, mock_is_dir):
        config = Config.Custom
        data_frame = DataFrame()
        custom_folder = "not_a_directory"
        mock_is_dir.return_value = False
        with self.assertRaises(ValueError):
            _column_mapping(data_frame, config, custom_folder)

    @patch("ppb.convert.load_custom_module")
    @patch("pathlib.Path.is_dir")
    @patch("ppb.convert.ExtPath.is_not_valid")
    def test_custom_config_with_column_map_none(self, mock_is_not_valid, mock_is_dir, mock_load_custom_module):
        config = Config.Custom
        data_frame = DataFrame()
        custom_folder = "valid_folder"
        mock_is_not_valid.return_value = False
        mock_is_dir.return_value = True
        custom_mapper = mock_load_custom_module.return_value
        custom_mapper.COLUMN_MAP = None
        custom_mapper.MISSING_REQUIRED_COLUMNS = []
        with self.assertRaises(ValueError):
            _column_mapping(data_frame, config, custom_folder)

    @patch("ppb.convert.load_custom_module")
    @patch("pathlib.Path.is_dir")
    @patch("ppb.convert.ExtPath.is_not_valid")
    def test_custom_config_with_missing_required_columns_none(
        self, mock_is_not_valid, mock_is_dir, mock_load_custom_module
    ):
        config = Config.Custom
        data_frame = DataFrame()
        custom_folder = "valid_folder"
        mock_is_not_valid.return_value = False
        mock_is_dir.return_value = True
        custom_mapper = mock_load_custom_module.return_value
        custom_mapper.COLUMN_MAP = {"a": "b"}
        custom_mapper.MISSING_REQUIRED_COLUMNS = None
        with self.assertRaises(ValueError):
            _column_mapping(data_frame, config, custom_folder)

    @patch("ppb.convert.mapping")
    @patch("ppb.convert.load_custom_module")
    @patch("pathlib.Path.is_dir")
    @patch("ppb.convert.ExtPath.is_not_valid")
    def test_custom_config_with_valid_custom_folder(
        self, mock_is_not_valid, mock_is_dir, mock_load_custom_module, mock_mapping
    ):
        config = Config.Custom
        data_frame = DataFrame()
        custom_folder = "valid_folder"
        mock_is_not_valid.return_value = False
        mock_is_dir.return_value = True
        custom_mapper = mock_load_custom_module.return_value
        custom_mapper.COLUMN_MAP = {"a": "b"}
        custom_mapper.MISSING_REQUIRED_COLUMNS = ["c"]
        result = _column_mapping(data_frame, config, custom_folder)
        mock_mapping.assert_called_with(data_frame, custom_mapper.COLUMN_MAP, custom_mapper.MISSING_REQUIRED_COLUMNS)
        self.assertEqual(result, mock_mapping.return_value)


if __name__ == "__main__":
    unittest.main()
