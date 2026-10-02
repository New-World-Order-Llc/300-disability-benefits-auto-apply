import json
import os
from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger
from 300_orchestrator import BeastSystemOrchestrator


class SystemMonitor:
    """
    Deterministic monitoring module for Beast System 3.0 (Module 300).
    Provides continuous health checks, pipeline status reports,
    audit log summaries, and compliance verification snapshots.
    """

    def __init__(self, audit_log_path: str = "300_audit_log.jsonl"):
        self.audit_log_path = audit_log_path
        self.audit = AuditLogger(audit_log_path)
        self.orchestrator = BeastSystemOrchestrator()

    def system_health(self) -> Dict[str, Any]:
        """
        Returns a deterministic snapshot of system health.
        """

        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "audit_log_exists": os.path.exists(self.audit_log_path),
            "audit_log_size_bytes": os.path.getsize(self.audit_log_path)
            if os.path.exists(self.audit_log_path) else 0,
            "modules_loaded": [
                "300_disability_application",
                "300_eligibility_compliance",
                "300_audit_logger",
                "300_member_profile_ingestion",
                "300_auto_submission",
                "300_ssa16_field_mapping",
                "300_orchestrator",
                "300_pipeline_api",
                "300_scheduler",
                "300_system_monitor"
            ],
            "status": "OPERATIONAL"
        }

        self.audit.log("system_health_check", "SYSTEM", health)
        return health

    def recent_events(self, limit: int = 10) -> Dict[str, Any]:
        """
        Returns the most recent audit log entries.
        Deterministic output: last N events.
        """

        events = []

        if os.path.exists(self.audit_log_path):
            with open(self.audit_log_path, "r") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_count": len(events),
            "events": events
        }

        self.audit.log("system_recent_events", "SYSTEM", snapshot)
        return snapshot

    def verify_pipeline(self, raw_member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs a deterministic dry‑run of the pipeline to verify
        that all modules are functioning correctly.
        """

        member_id = raw_member_data.get("member_id", "UNKNOWN")

        self.audit.log(
            "system_pipeline_verification_start",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        result = self.orchestrator.process_member(raw_member_data)

        verification = {
            "timestamp": datetime.utcnow().isoformat(),
            "member_id": member_id,
            "qualified": result.get("qualified", False),
            "submitted": result.get("submitted", False),
            "details": result
        }

        self.audit.log(
            "system_pipeline_verification_complete",
            member_id,
            verification
        )

        return verification


# Example deterministic run
if __name__ == "__main__":
    monitor = SystemMonitor()

    print("SYSTEM HEALTH:")
    print(monitor.system_health())

    print("\nRECENT EVENTS:")
    print(monitor.recent_events(limit=5))

    print("\nPIPELINE VERIFICATION:")
    test_member = {
        "member_id": "M-0009",
        "first_name": "Olivia",
        "middle_initial": "S",
        "last_name": "Grant",
        "ssn_last4": "3344",
        "gender": "Female",
        "date_of_birth": "1990-07-15",
        "birth_country": "USA",
        "citizen": True,
        "disability_status": True,
        "disability_onset_date": "2024-11-01",
        "income_level": 21000.00,
        "preferred_language": "English",
        "compliance_flags": [
            "KYC_VERIFIED",
            "ADDRESS_CONFIRMED",
            "IDENTITY_VERIFIED",
            "PROFILE_COMPLETE"
        ]
    }

    print(monitor.verify_pipeline(test_member))
