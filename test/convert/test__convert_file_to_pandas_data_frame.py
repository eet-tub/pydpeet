import unittest
from unittest.mock import patch, MagicMock

from pandas import DataFrame

from pydpeet.io.configs.config import Config, READER_CONFIGS
from pydpeet.io.convert import _convert_file_to_pandas_data_frame
from utils import mock_config


class TestConvertFileToPandasDataFrame(unittest.TestCase):
    @patch('ppb.configs.config.Config.not_exists')
    def test_unknown_config(self, mock_not_exists):
        mock_not_exists.return_value = True
        with self.assertRaises(ValueError):
            _convert_file_to_pandas_data_frame(mock_config(), 'input_path')

    def test_custom_config_with_invalid_custom_folder(self):
        with self.assertRaises(ValueError):
            _convert_file_to_pandas_data_frame(Config.Custom, 'input_path', 'custom_folder')

    @patch('ppb.configs.config.Config.not_exists')
    def test_config_in_READER_CONFIGS(self, mock_not_exists):
        mock_not_exists.return_value = False
        mock_reader = MagicMock()
        mock_reader.return_value = (DataFrame(), 'meta_data')
        mocked_config = mock_config()
        READER_CONFIGS[mocked_config] = mock_reader
        data_frame, meta_data = _convert_file_to_pandas_data_frame(mocked_config, 'input_path')
        self.assertIsInstance(data_frame, DataFrame)
        self.assertEqual(meta_data, 'meta_data')

    @patch('ppb.configs.config.Config.not_exists')
    def test_config_in_READER_CONFIGS_with_invalid_input_path(self, mock_not_exists):
        mock_not_exists.return_value = False
        mock_reader = MagicMock(side_effect=Exception('Invalid input path'))
        mocked_config = mock_config()
        READER_CONFIGS[mocked_config] = mock_reader
        with self.assertRaises(Exception):
            _convert_file_to_pandas_data_frame(mocked_config, 'input_path')


if __name__ == '__main__':
    unittest.main()
