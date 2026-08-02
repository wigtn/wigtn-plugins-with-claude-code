import unittest
from implementation import discount
class T(unittest.TestCase):
 def test_cap(self): self.assertLessEqual(discount(1000),100)
 def test_auth(self):
  with self.assertRaises(PermissionError): discount(10,50,"member")
