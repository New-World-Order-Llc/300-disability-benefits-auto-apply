import time
from datetime import datetime
from typing import Dict, Any, Callable

from 300_pipeline_api import PipelineAPI
from 300_audit_logger import AuditLogger


class DeterministicScheduler:
    """
    Deterministic scheduler for Module 300.
    Executes disability‑benefit auto‑application checks on a timed interval
    or via external triggers. Guarantees reproducible execution cycles.
    """

    def __init__(self, interval_seconds: int = 3600):
        self.interval = interval_seconds
        self.api = PipelineAPI()
        self.audit = AuditLogger()
        self.running = False

    def run_cycle(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes one deterministic cycle of the auto‑application pipeline.
        """

        member_id = member_data.get("member_id", "UNKNOWN")

        self.audit.log(
            "scheduler_cycle_start",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        result = self.api.apply_for_disability(member_data)

        self.audit.log(
            "scheduler_cycle_complete",
            member_id,
            {"result": result}
        )

        return result

    def start(self, member_data_provider: Callable[[], Dict[str, Any]]) -> None:
        """
        Starts the deterministic scheduler loop.
        The member_data_provider must return raw member data for each cycle.
        """

        self.running = True

        while self.running:
            raw_member_data = member_data_provider()
            member_id = raw_member_data.get("member_id", "UNKNOWN")

            self.audit.log(
                "scheduler_tick",
                member_id,
                {"timestamp": datetime.utcnow().isoformat()}
            )

            self.run_cycle(raw_member_data)

            time.sleep(self.interval)

    def stop(self) -> None:
        """
        Stops the deterministic scheduler loop.
        """

        self.running = False
        self.audit.log(
            "scheduler_stopped",
            "SYSTEM",
            {"timestamp": datetime.utcnow().isoformat()}
        )


# Example deterministic run
if __name__ == "__main__":
    def example_member_provider():
        return {
            "member_id": "M-0008",
            "first_name": "Henry",
            "middle_initial": "Q",
            "last_name": "Miller",
            "ssn_last4": "9911",
            "gender": "Male",
            "date_of_birth": "1970-12-01",
            "birth_country": "USA",
            "citizen": True,
            "disability_status": True,
            "disability_onset_date": "2024-10-01",
            "income_level": 18000.00,
            "preferred_language": "English",
            "compliance_flags": [
                "KYC_VERIFIED",
                "ADDRESS_CONFIRMED",
                "IDENTITY_VERIFIED",
                "PROFILE_COMPLETE"
            ]
        }

    scheduler = DeterministicScheduler(interval_seconds=5)
    scheduler.run_cycle(example_member_provider())
