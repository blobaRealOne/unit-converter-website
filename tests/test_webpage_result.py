import unittest

from src.main import webpage_result_mod_rt


class TestWebpageResult(unittest.TestCase):
    def test_length_conversion(self):
        data = {
            "input_data": ["1500"],
            "units_from": ["meter"],
            "units_to": ["kilometer"],
        }
        result = webpage_result_mod_rt(data).decode("utf-8")
        self.assertIn("1500 m = 1.5 km", result)

    def test_temperature_conversion(self):
        data = {
            "input_data": ["32"],
            "units_from": ["fahrenheit"],
            "units_to": ["celsius"],
        }
        result = webpage_result_mod_rt(data).decode("utf-8")
        self.assertIn("32 °F = 0 °C", result)

    def test_incompatible_units(self):
        data = {
            "input_data": ["100"],
            "units_from": ["meter"],
            "units_to": ["kilogram"],
        }
        with self.assertRaises(ValueError):
            _ = webpage_result_mod_rt(data)

    def test_negative_weight(self):
        data = {"input_data": ["-10"], "units_from": ["kilogram"], "units_to": ["gram"]}
        with self.assertRaises(ValueError):
            _ = webpage_result_mod_rt(data)

    def test_unknown_unit(self):
        data = {"input_data": ["100"], "units_from": ["unknown"], "units_to": ["meter"]}
        with self.assertRaises(ValueError):
            _ = webpage_result_mod_rt(data)

    def test_non_finite_input(self):
        for value in ["inf", "-inf", "nan"]:
            with self.subTest(value=value):
                data = {
                    "input_data": [value],
                    "units_from": ["meter"],
                    "units_to": ["centimeter"],
                }
                with self.assertRaises(ValueError):
                    _ = webpage_result_mod_rt(data)

    def test_temperature_below_absolute_zero(self):
        data = {
            "input_data": ["-500"],
            "units_from": ["celsius"],
            "units_to": ["fahrenheit"],
        }
        with self.assertRaises(ValueError):
            _ = webpage_result_mod_rt(data)


if __name__ == "__main__":
    _ = unittest.main()
