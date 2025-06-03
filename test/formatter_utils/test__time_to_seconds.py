import unittest
from ppb.utils.formatter_utils import _time_to_seconds



class TestTimeToSeconds(unittest.TestCase):

    def test_time_to_seconds_empty_dataframe(self):
        data = None
        expected = None
        result = _time_to_seconds(data)
        self.assertEqual(expected, result)


    def test_time_string_in_HH_MM_SS_format(self):
        data = "01:30:00"
        expected = 5400
        result = _time_to_seconds(data)
        self.assertEqual(expected, result)

    def test_time_string_in_HH_MM_SS_MS_format_with_float(self):
        data = "01:30:00.5"
        expected = 5400.5
        result = _time_to_seconds(data)
        self.assertEqual(expected, result)

    def test_time_string_with_only_seconds(self):
        data = "10"
        expected = 10.0
        result = _time_to_seconds(data)
        self.assertEqual(expected, result)

    def test_time_string_with_invalid_format(self):
        with self.assertRaises(ValueError):
            _time_to_seconds("invalid time string")

    def test_time_string_with_non_numeric_values(self):
        with self.assertRaises(ValueError):
            _time_to_seconds("01:30:abc")
