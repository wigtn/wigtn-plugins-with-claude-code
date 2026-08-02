import unittest
from implementation import csv_cell
class T(unittest.TestCase):
    def test_formula_prefixes(self):
        for value in ("=1+1","+cmd","-2+3","@SUM(A1)","\t=1","\r=1"):
            self.assertTrue(csv_cell(value).startswith("'"))
    def test_safe(self):
        self.assertEqual(csv_cell("hello"),"hello")
        self.assertEqual(csv_cell(123),"123")
if __name__ == "__main__": unittest.main()
