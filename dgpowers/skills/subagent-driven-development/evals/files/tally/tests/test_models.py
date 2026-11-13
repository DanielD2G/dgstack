import unittest

from tally.models import format_amount, parse_amount


class AmountTests(unittest.TestCase):
    def test_parse_whole_and_fraction(self):
        self.assertEqual(parse_amount("12.50"), 1250)
        self.assertEqual(parse_amount("12"), 1200)
        self.assertEqual(parse_amount("0.5"), 50)

    def test_parse_rejects_garbage(self):
        for bad in ["", "abc", "1.234", "-3", "1,50"]:
            with self.assertRaises(ValueError):
                parse_amount(bad)

    def test_format(self):
        self.assertEqual(format_amount(1250), "12.50")
        self.assertEqual(format_amount(5), "0.05")


if __name__ == "__main__":
    unittest.main()
