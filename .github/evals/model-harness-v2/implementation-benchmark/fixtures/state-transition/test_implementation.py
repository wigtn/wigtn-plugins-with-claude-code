import unittest
from implementation import transition
class T(unittest.TestCase):
    def test_pending(self):
        self.assertEqual(transition("PENDING","approve"),"APPROVED")
    def test_terminal_immutable(self):
        for state in ("APPROVED","REJECTED","CANCELLED"):
            with self.assertRaises(ValueError): transition(state,"approve")
    def test_unknown(self):
        with self.assertRaises(ValueError): transition("PENDING","delete")
if __name__ == "__main__": unittest.main()
