import unittest
from implementation import accept_event
class T(unittest.TestCase):
    def test_duplicate(self):
        seen=set()
        self.assertTrue(accept_event("e1",seen))
        self.assertFalse(accept_event("e1",seen))
        self.assertEqual(seen,{"e1"})
    def test_invalid(self):
        with self.assertRaises(ValueError): accept_event("",set())
if __name__ == "__main__": unittest.main()
