import importlib.util
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("300.py")
SPEC = importlib.util.spec_from_file_location("disability_benefits_300", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class MemoryAudit:
    def __init__(self):
        self.events = []

    def write(self, event):
        self.events.append(event)


class AutomationTests(unittest.TestCase):
    def setUp(self):
        self.audit = MemoryAudit()
        self.profile = module.MemberProfile(
            member_id="member-1",
            disability_status=True,
            annual_income=Decimal("12000"),
            compliance_flags={"kyc": True, "address": True, "identity": True},
            identity_attributes={"first_name": "Ada", "last_name": "Lovelace"},
        )
        self.engine = module.DisabilityBenefitsAutomation(
            module.EligibilityPolicy(Decimal("20000")),
            "https://benefits.example/applications",
            self.audit,
            transport=lambda endpoint, payload, timeout: module.ApiResponse(201),
            clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    def test_qualified_profile_builds_stable_payload_and_submits(self):
        first = self.engine.build_payload(self.profile)
        second = self.engine.build_payload(self.profile)
        self.assertEqual(first, second)
        self.assertEqual(first["application"]["first_name"], "Ada")

        result = self.engine.apply(self.profile)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.submission_id, first["submission_id"])
        self.assertEqual(self.audit.events[-1].action, "submission_completed")

    def test_compliance_failure_prevents_eligibility_and_submission(self):
        profile = module.MemberProfile(
            member_id="member-2",
            disability_status=True,
            annual_income=Decimal("1000"),
            compliance_flags={"kyc": True, "address": False, "identity": True},
        )
        calls = []
        self.engine.transport = lambda *args: calls.append(args)

        result = self.engine.apply(profile)

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "compliance_failed")
        self.assertEqual(calls, [])
        self.assertEqual([event.action for event in self.audit.events], [
            "compliance_check", "submission_halted",
        ])

    def test_ineligible_profile_is_not_submitted(self):
        profile = module.MemberProfile(
            member_id="member-3",
            disability_status=False,
            annual_income=Decimal("1000"),
            compliance_flags={"kyc": True, "address": True, "identity": True},
        )
        calls = []
        self.engine.transport = lambda *args: calls.append(args)

        result = self.engine.apply(profile)

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "ineligible")
        self.assertEqual(calls, [])

    def test_http_failure_is_recorded(self):
        self.engine.transport = lambda *args: module.ApiResponse(503)

        result = self.engine.apply(self.profile)

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "http_error")
        self.assertEqual(result.status_code, 503)


if __name__ == "__main__":
    unittest.main()
