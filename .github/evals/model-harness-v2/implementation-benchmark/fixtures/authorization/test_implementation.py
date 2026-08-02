import unittest
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
