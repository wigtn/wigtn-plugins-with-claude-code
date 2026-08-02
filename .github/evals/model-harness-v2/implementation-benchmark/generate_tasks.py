#!/usr/bin/env python3
"""Generate ten dependency-free implementation tasks with hidden-style unit tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TASKS = {
    "money-rounding": {
        "impl": '''def allocate_cents(total, weights):
    """Allocate integer cents proportionally; output must sum to total."""
    s = sum(weights)
    return [round(total * w / s) for w in weights]
''',
        "test": '''import unittest
from implementation import allocate_cents
class T(unittest.TestCase):
    def test_sum_and_deterministic_remainder(self):
        self.assertEqual(allocate_cents(10, [1,1,1]), [4,3,3])
        self.assertEqual(sum(allocate_cents(101, [2,3,5])), 101)
    def test_invalid(self):
        with self.assertRaises(ValueError): allocate_cents(5, [0,0])
        with self.assertRaises(ValueError): allocate_cents(-1, [1])
if __name__ == "__main__": unittest.main()
''',
    },
    "date-range": {
        "impl": '''from datetime import date
def inclusive_days(start, end):
    return (end - start).days
''',
        "test": '''import unittest
from datetime import date
from implementation import inclusive_days
class T(unittest.TestCase):
    def test_inclusive(self):
        self.assertEqual(inclusive_days(date(2026,1,1), date(2026,1,1)), 1)
        self.assertEqual(inclusive_days(date(2026,1,1), date(2026,1,3)), 3)
    def test_reverse(self):
        with self.assertRaises(ValueError): inclusive_days(date(2026,1,2), date(2026,1,1))
if __name__ == "__main__": unittest.main()
''',
    },
    "authorization": {
        "impl": '''def can_edit(user, document):
    return user["role"] == "admin" or user["id"] == document["owner_id"]
''',
        "test": '''import unittest
from implementation import can_edit
class T(unittest.TestCase):
    def test_tenant_boundary(self):
        admin={"id":"a","role":"admin","org_id":"o1"}
        doc={"owner_id":"b","org_id":"o2"}
        self.assertFalse(can_edit(admin,doc))
    def test_owner_same_org(self):
        user={"id":"u","role":"member","org_id":"o1"}
        self.assertTrue(can_edit(user,{"owner_id":"u","org_id":"o1"}))
        self.assertFalse(can_edit(user,{"owner_id":"u","org_id":"o2"}))
if __name__ == "__main__": unittest.main()
''',
    },
    "webhook-signature": {
        "impl": '''import hashlib, hmac
def verify(secret, body, signature):
    expected = hashlib.sha256(secret + body).hexdigest()
    return expected == signature
''',
        "test": '''import unittest, hashlib, hmac
from implementation import verify
class T(unittest.TestCase):
    def test_hmac_sha256(self):
        secret=b"key"; body=b"payload"
        sig=hmac.new(secret,body,hashlib.sha256).hexdigest()
        self.assertTrue(verify(secret,body,sig))
        self.assertFalse(verify(secret,body,sig[:-1]+"0"))
    def test_bad_format(self):
        self.assertFalse(verify(b"k",b"x","not-hex"))
if __name__ == "__main__": unittest.main()
''',
    },
    "pagination": {
        "impl": '''def page(rows, cursor=None, limit=2):
    start = int(cursor or 0)
    items = rows[start:start+limit]
    next_cursor = str(start + limit) if start + limit < len(rows) else None
    return items, next_cursor
''',
        "test": '''import unittest
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
''',
    },
    "retry-backoff": {
        "impl": '''def retry_delays(attempts, base=1, cap=30):
    return [base * (2 ** i) for i in range(attempts)]
''',
        "test": '''import unittest
from implementation import retry_delays
class T(unittest.TestCase):
    def test_cap(self):
        self.assertEqual(retry_delays(7,2,30),[2,4,8,16,30,30,30])
    def test_invalid(self):
        with self.assertRaises(ValueError): retry_delays(-1)
        with self.assertRaises(ValueError): retry_delays(2,0,30)
if __name__ == "__main__": unittest.main()
''',
    },
    "safe-path": {
        "impl": '''from pathlib import Path
def safe_join(root, user_path):
    return Path(root) / user_path
''',
        "test": '''import tempfile, unittest
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
''',
    },
    "state-transition": {
        "impl": '''def transition(state, action):
    table={"approve":"APPROVED","reject":"REJECTED","cancel":"CANCELLED"}
    return table[action]
''',
        "test": '''import unittest
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
''',
    },
    "event-dedupe": {
        "impl": '''def accept_event(event_id, seen):
    seen.add(event_id)
    return True
''',
        "test": '''import unittest
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
''',
    },
    "csv-injection": {
        "impl": '''def csv_cell(value):
    return str(value)
''',
        "test": '''import unittest
from implementation import csv_cell
class T(unittest.TestCase):
    def test_formula_prefixes(self):
        for value in ("=1+1","+cmd","-2+3","@SUM(A1)","\\t=1","\\r=1"):
            self.assertTrue(csv_cell(value).startswith("'"))
    def test_safe(self):
        self.assertEqual(csv_cell("hello"),"hello")
        self.assertEqual(csv_cell(123),"123")
if __name__ == "__main__": unittest.main()
''',
    },
}


def main(root_arg: str) -> int:
    root = Path(root_arg)
    root.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, files in TASKS.items():
        task = root / name
        task.mkdir(parents=True, exist_ok=True)
        (task / "implementation.py").write_text(files["impl"], encoding="utf-8")
        (task / "test_implementation.py").write_text(files["test"], encoding="utf-8")
        (task / "TASK.md").write_text(
            "Fix `implementation.py` so all tests pass. Preserve the public function signature. "
            "Use only the Python standard library. Run `python3 -m unittest -v` and report evidence. "
            "Do not edit the tests.\n",
            encoding="utf-8",
        )
        manifest[name] = sorted(("implementation.py", "test_implementation.py", "TASK.md"))
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
