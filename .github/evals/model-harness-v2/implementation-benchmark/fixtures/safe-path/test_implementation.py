import tempfile, unittest
from pathlib import Path
from implementation import safe_join
class T(unittest.TestCase):
    def test_inside(self):
        root=Path(tempfile.mkdtemp())
        self.assertEqual(safe_join(root,"a/b.txt"),root/"a/b.txt")
    def test_escape(self):
        root=Path(tempfile.mkdtemp())
        for p in ("../x","/tmp/x","a/../../x"):
            with self.assertRaises(ValueError): safe_join(root,p)
if __name__ == "__main__": unittest.main()
