import unittest
from unittest.mock import MagicMock, patch

from pandas import DataFrame

from pydpeet.io.configs.config import Config, FORMATTER_CONFIGS
from pydpeet.io.convert import _get_data_into_format
from utils import mock_config


class TestGetDataIntoFormat(unittest.TestCase):
    def test_data_frame_is_none(self):
        with self.assertRaises(ValueError):
            _get_data_into_format(None, Config.Zahner_1)

    def test_config_is_none(self):
        with self.assertRaises(ValueError):
            _get_data_into_format(DataFrame(), None)

    def test_custom_folder_is_none_for_custom_config(self):
        with self.assertRaises(ValueError):
            _get_data_into_format(DataFrame(), Config.Custom)

    def test_unknown_config(self):
        with self.assertRaises(ValueError):
            _get_data_into_format(DataFrame(), mock_config())

    @patch('ppb.convert.load_custom_module')
    def test_custom_formatter_loaded_and_applied(self, mock_load_custom_module):
        data_frame = DataFrame()
        mock_formatter = MagicMock()
        mock_load_custom_module.return_value = mock_formatter
        _get_data_into_format(data_frame, Config.Custom, __file__)
        mock_formatter.get_data_into_format.assert_called_once_with(data_frame)

    def test_built_in_formatter_applied(self):
        data_frame = DataFrame()
        mock_formatter = MagicMock()
        FORMATTER_CONFIGS[Config.Zahner_1] = mock_formatter
        _get_data_into_format(data_frame, Config.Zahner_1)
        mock_formatter.assert_called_once_with(data_frame)


if __name__ == '__main__':
    unittest.main()
