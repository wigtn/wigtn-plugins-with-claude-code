import unittest
from implementation import page
class T(unittest.TestCase):
    def test_stable_id_cursor(self):
        rows=[{"id":"a"},{"id":"b"},{"id":"c"}]
        items,c=page(rows,None,2); self.assertEqual([x["id"] for x in items],["a","b"])
        changed=[{"id":"x"}]+rows
        items,c2=page(changed,c,2); self.assertEqual([x["id"] for x in items],["c"])
        self.assertIsNone(c2)
    def test_limit(self):
        with self.assertRaises(ValueError): page([],None,0)
if __name__ == "__main__": unittest.main()
