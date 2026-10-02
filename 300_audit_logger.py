import json
from datetime import datetime
from typing import Dict, Any


class AuditLogger:
    """
    Deterministic audit logger for Beast System 3.0.
    Every action, decision, and submission is logged with
    immutable timestamps and reproducible state snapshots.
    """

    def __init__(self, log_file: str = "300_audit_log.jsonl"):
        self.log_file = log_file

    def log(self, event_type: str, member_id: str, details: Dict[str, Any]) -> None:
        """
        Writes a deterministic audit entry to a JSON Lines file.
        Each entry is a complete snapshot of the event.
        """

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "member_id": member_id,
            "details": details
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def log_compliance_check(self, member_id: str, compliance_result: Dict[str, Any]) -> None:
        self.log("compliance_check", member_id, compliance_result)

    def log_eligibility_check(self, member_id: str, eligibility_result: Dict[str, Any]) -> None:
        self.log("eligibility_check", member_id, eligibility_result)

    def log_application_payload(self, member_id: str, payload: Dict[str, Any]) -> None:
        self.log("application_payload_generated", member_id, payload)

    def log_submission(self, member_id: str, submission_result: Dict[str, Any]) -> None:
        self.log("application_submission", member_id, submission_result)


# Example deterministic run
if __name__ == "__main__":
    logger = AuditLogger()

    logger.log(
        "test_event",
        "M-0003",
        {"message": "Audit logger initialized for deterministic testing."}
    )
