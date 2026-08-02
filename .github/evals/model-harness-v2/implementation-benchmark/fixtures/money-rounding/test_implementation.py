import unittest
from implementation import allocate_cents
class T(unittest.TestCase):
    def test_sum_and_deterministic_remainder(self):
        self.assertEqual(allocate_cents(10, [1,1,1]), [4,3,3])
        self.assertEqual(sum(allocate_cents(101, [2,3,5])), 101)
    def test_invalid(self):
        with self.assertRaises(ValueError): allocate_cents(5, [0,0])
        with self.assertRaises(ValueError): allocate_cents(-1, [1])
if __name__ == "__main__": unittest.main()
