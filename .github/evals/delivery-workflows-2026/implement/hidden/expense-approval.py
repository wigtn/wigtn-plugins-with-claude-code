import unittest
from expense.repository import Repository
from expense.service import ExpenseService


class HiddenExpense(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        self.svc = ExpenseService(self.repo)

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.svc.submit("u", "t", 0, "k")

    def test_key_payload_conflict(self):
        self.svc.submit("u", "t", 10, "k")
        with self.assertRaises(ValueError):
            self.svc.submit("u", "t", 11, "k")

    def test_owner_key_namespace(self):
        a = self.svc.submit("u1", "t", 10, "k")
        b = self.svc.submit("u2", "t", 10, "k")
        self.assertNotEqual(a.id, b.id)

    def test_self_approval_and_double_decision(self):
        item = self.svc.submit("u", "t", 10, "k")
        with self.assertRaises(PermissionError):
            self.svc.decide("u", "t", item.id, "APPROVE")
        self.svc.decide("m", "t", item.id, "APPROVE")
        with self.assertRaises(ValueError):
            self.svc.decide("m", "t", item.id, "APPROVE")

    def test_reject_reason_and_audit(self):
        item = self.svc.submit("u", "t", 10, "k")
        with self.assertRaises(ValueError):
            self.svc.decide("m", "t", item.id, "REJECT", " ")
        self.svc.decide("m", "t", item.id, "REJECT", "duplicate")
        self.assertEqual(len(self.repo.audit), 2)


if __name__ == "__main__":
    unittest.main()
