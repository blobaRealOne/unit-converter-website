import unittest

from src.main import format_number


class TestFormatNumber(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(format_number(1000.0), "1000")

    def test_decimal(self):
        self.assertEqual(format_number(10.5000), "10.5")

    def test_zero(self):
        self.assertEqual(format_number(0.0), "0")

    def test_small_decimal(self):
        self.assertEqual(format_number(0.000001), "0.000001")

    def test_non_finite(self):
        with self.assertRaises(ValueError):
            _ = format_number(float("inf"))


if __name__ == "__main__":
    _ = unittest.main()
