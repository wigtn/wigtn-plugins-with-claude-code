import unittest
from datetime import date
from implementation import inclusive_days
class T(unittest.TestCase):
    def test_inclusive(self):
        self.assertEqual(inclusive_days(date(2026,1,1), date(2026,1,1)), 1)
        self.assertEqual(inclusive_days(date(2026,1,1), date(2026,1,3)), 3)
    def test_reverse(self):
        with self.assertRaises(ValueError): inclusive_days(date(2026,1,2), date(2026,1,1))
if __name__ == "__main__": unittest.main()
