import copy
import unittest
import module_300 as m

BASE = {"member_id": "M1", "full_name": "A B", "date_of_birth": "1980-01-01",
        "ssn_last4": "1111", "address": "x", "disability_type": "Back",
        "disability_onset_date": "2023-01-01", "work_credits": 30,
        "compliance": {k: True for k in m.REQUIRED_COMPLIANCE_FLAGS}}


class T(unittest.TestCase):
    def test_submit_and_deterministic(self):
        a, b = m.AuditLog(), m.AuditLog()
        r1 = m.process_application(BASE, "2026-01-01", a)
        r2 = m.process_application(copy.deepcopy(BASE), "2026-01-01", b)
        self.assertEqual(r1.status, "SUBMITTED")
        self.assertEqual(r1.payload, r2.payload)
        self.assertEqual(a.entries, b.entries)
        self.assertTrue(a.verify())

    def test_noncompliant_held_not_submitted(self):
        p = copy.deepcopy(BASE)
        p["compliance"]["identity_verified"] = False
        r = m.process_application(p, "2026-01-01", submitter=lambda _: self.fail("submitted"))
        self.assertEqual(r.status, "HELD_COMPLIANCE")

    def test_ineligible(self):
        p = dict(BASE, work_credits=5)
        self.assertEqual(m.process_application(p, "2026-01-01").status, "DECLINED_INELIGIBLE")

    def test_invalid_and_tamper(self):
        self.assertEqual(m.process_application({}, "2026-01-01").status, "HELD_INVALID_PROFILE")
        a = m.AuditLog()
        m.process_application(BASE, "2026-01-01", a)
        a.entries[1]["detail"]["compliant"] = False
        self.assertFalse(a.verify())


if __name__ == "__main__":
    unittest.main()
