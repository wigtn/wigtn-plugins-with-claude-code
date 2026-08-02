import unittest
from search.cursor import decode_cursor, encode_cursor
from search.service import search


class HiddenSearch(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"id": "1", "tenant_id": "a", "name": "Straße", "created_at": 3},
            {"id": "2", "tenant_id": "a", "name": "STRASSE", "created_at": 2},
            {"id": "3", "tenant_id": "b", "name": "strasse", "created_at": 4},
        ]

    def test_casefold_and_tenant(self):
        page, _ = search(self.records, "a", "STRASSE", 10)
        self.assertEqual([item["id"] for item in page], ["1", "2"])

    def test_input_unchanged(self):
        before = [dict(item) for item in self.records]
        search(self.records, "a", "", 2)
        self.assertEqual(self.records, before)

    def test_limit(self):
        for limit in (0, 51, True):
            with self.assertRaises(ValueError):
                search(self.records, "a", "", limit)

    def test_cross_tenant_cursor(self):
        cursor = encode_cursor("a", 3, "1")
        with self.assertRaises(ValueError):
            decode_cursor(cursor, "b")

    def test_malformed_cursor(self):
        with self.assertRaises(ValueError):
            search(self.records, "a", "", 2, "not-a-cursor")


if __name__ == "__main__":
    unittest.main()
