from datetime import datetime
from typing import Dict, Any

from 300_member_profile_ingestion import MemberProfileIngestion
from 300_eligibility_compliance import evaluate_member
from 300_disability_application import generate_ssa16_payload
from 300_auto_submission import AutoSubmissionEngine
from 300_audit_logger import AuditLogger
from 300_ssa16_field_mapping import SSA16FieldMapping


class BeastSystemOrchestrator:
    """
    Deterministic orchestrator for disability‑benefits automation.
    This module coordinates ingestion, compliance, eligibility,
    SSA‑16 payload generation, field mapping, and submission.
    """

    def __init__(self):
        self.ingestion = MemberProfileIngestion()
        self.submission_engine = AutoSubmissionEngine()
        self.audit = AuditLogger()
        self.mapper = SSA16FieldMapping()

    def process_member(self, raw_member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full deterministic pipeline:
        1. Validate raw data
        2. Ingest profile
        3. Evaluate compliance + eligibility
        4. Generate SSA‑16 payload
        5. Map fields to SSA‑16 structure
        6. Submit application
        7. Log all actions
        """

        # Step 1: Validate raw data
        validation = self.ingestion.validate_raw(raw_member_data)
        self.audit.log("validation", raw_member_data.get("member_id", "UNKNOWN"), validation)

        if not validation["valid"]:
            return {
                "qualified": False,
                "submitted": False,
                "reason": "Raw member data invalid.",
                "details": validation
            }

        # Step 2: Ingest profile
        profile = self.ingestion.ingest(raw_member_data)
        profile_dict = profile.__dict__
        profile_dict["timestamp"] = datetime.utcnow().isoformat()
        self.audit.log("profile_ingested", profile.member_id, profile_dict)

        # Step 3: Compliance + eligibility
        evaluation = evaluate_member(profile)
        self.audit.log("evaluation", profile.member_id, evaluation)

        if not evaluation["qualified_for_auto_application"]:
            return {
                "qualified": False,
                "submitted": False,
                "reason": "Member not eligible or not compliant.",
                "details": evaluation
            }

        # Step 4: Generate SSA‑16 payload
        payload = generate_ssa16_payload(profile)
        self.audit.log_application_payload(profile.member_id, payload)

        # Step 5: Map fields to SSA‑16 structure
        mapped_payload = self.mapper.map_profile_to_ssa16(payload)
        self.audit.log("ssa16_mapping", profile.member_id, mapped_payload)

        # Step 6: Submit application
        submission_result = self.submission_engine.submit(profile.member_id, mapped_payload)

        # Step 7: Final log
        self.audit.log("pipeline_complete", profile.member_id, submission_result)

        return {
            "qualified": True,
            "submitted": True,
            "payload": mapped_payload,
            "submission": submission_result
        }


# Example deterministic run
if __name__ == "__main__":
    raw = {
        "member_id": "M-0006",
        "first_name": "Daniel",
        "middle_initial": "R",
        "last_name": "Hughes",
        "ssn_last4": "5566",
        "gender": "Male",
        "date_of_birth": "1982-11-05",
        "birth_country": "USA",
        "citizen": True,
        "disability_status": True,
        "disability_onset_date": "2024-08-01",
        "income_level": 20000.00,
        "preferred_language": "English",
        "compliance_flags": [
            "KYC_VERIFIED",
            "ADDRESS_CONFIRMED",
            "IDENTITY_VERIFIED",
            "PROFILE_COMPLETE"
        ]
    }

    orchestrator = BeastSystemOrchestrator()
    result = orchestrator.process_member(raw)
    print(result)
