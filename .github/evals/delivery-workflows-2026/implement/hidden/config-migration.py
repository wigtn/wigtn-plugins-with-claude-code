import copy
import unittest
from config.migrate import migrate_config


class HiddenConfig(unittest.TestCase):
    def test_input_unchanged(self):
        raw = {"version": 2, "delivery": {"endpoint": "https://a.test", "timeout_ms": 100, "enabled": True}}
        before = copy.deepcopy(raw)
        migrate_config(raw)
        self.assertEqual(raw, before)

    def test_mixed_versions(self):
        with self.assertRaises(ValueError):
            migrate_config({"version": 2, "endpoint": "https://a.test", "delivery": {}})

    def test_unknown_top_level(self):
        with self.assertRaises(ValueError):
            migrate_config({"endpoint": "https://a.test", "timeout_seconds": 1, "extra": 1})

    def test_bool_timeout_and_bounds(self):
        for value in (True, 0, 31):
            with self.assertRaises(ValueError):
                migrate_config({"endpoint": "https://a.test", "timeout_seconds": value})

    def test_type_and_v1_default(self):
        with self.assertRaises(ValueError):
            migrate_config([])
        out = migrate_config({"endpoint": "https://a.test", "timeout_seconds": 1})
        self.assertTrue(out.enabled)


if __name__ == "__main__":
    unittest.main()
