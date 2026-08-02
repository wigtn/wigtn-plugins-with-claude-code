import unittest
from implementation import retry_delays
class T(unittest.TestCase):
    def test_cap(self):
        self.assertEqual(retry_delays(7,2,30),[2,4,8,16,30,30,30])
    def test_invalid(self):
        with self.assertRaises(ValueError): retry_delays(-1)
        with self.assertRaises(ValueError): retry_delays(2,0,30)
if __name__ == "__main__": unittest.main()
