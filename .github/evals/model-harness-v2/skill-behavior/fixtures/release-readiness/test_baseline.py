import unittest
from baseline import add
class T(unittest.TestCase):
 def test_add(self): self.assertEqual(add(2,3),5)
