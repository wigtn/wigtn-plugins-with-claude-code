import unittest
from implementation import normalize_name
class T(unittest.TestCase):
 def test_trim_and_empty(self):
  self.assertEqual(normalize_name('  Kim  '),'Kim')
  with self.assertRaises(ValueError): normalize_name('   ')
