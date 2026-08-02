import unittest
from webhook.delivery import WebhookStore, retry_delay
from webhook.signing import verify_signature


class HiddenWebhook(unittest.TestCase):
    def test_malformed_signatures(self):
        for value in ("", "x", "sha1=abc", "sha256=z", "sha256="):
            self.assertFalse(verify_signature(b"s", b"x", value))

    def test_payload_conflict(self):
        store = WebhookStore()
        store.accept("e", b"a")
        with self.assertRaises(ValueError):
            store.accept("e", b"b")

    def test_attempt_schedule(self):
        self.assertEqual([retry_delay(i, 500) for i in (1, 2, 3)], [0, 60, 300])
        self.assertIsNone(retry_delay(4, 500))

    def test_any_2xx_is_terminal(self):
        for status in (200, 201, 204, 299):
            self.assertIsNone(retry_delay(1, status))

    def test_invalid_attempt(self):
        with self.assertRaises(ValueError):
            retry_delay(0, 500)


if __name__ == "__main__":
    unittest.main()
