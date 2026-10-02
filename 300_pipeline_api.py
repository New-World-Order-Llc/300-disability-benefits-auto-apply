from typing import Dict, Any

from 300_orchestrator import BeastSystemOrchestrator
from 300_audit_logger import AuditLogger


class PipelineAPI:
    """
    Public deterministic API layer for Module 300.
    External systems call this interface to trigger the
    disability‑benefits automation pipeline.
    """

    def __init__(self):
        self.orchestrator = BeastSystemOrchestrator()
        self.audit = AuditLogger()

    def apply_for_disability(self, raw_member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        External entry point.
        Accepts raw member data and runs the full deterministic pipeline.
        """

        member_id = raw_member_data.get("member_id", "UNKNOWN")

        self.audit.log(
            "pipeline_api_call",
            member_id,
            {"received_raw_data": raw_member_data}
        )

        result = self.orchestrator.process_member(raw_member_data)

        self.audit.log(
            "pipeline_api_result",
            member_id,
            {"result": result}
        )

        return result

    def simulate(self, raw_member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulation mode for testing external integrations.
        Runs the pipeline but does not perform real submission.
        """

        member_id = raw_member_data.get("member_id", "UNKNOWN")

        self.audit.log(
            "pipeline_api_simulation_call",
            member_id,
            {"received_raw_data": raw_member_data}
        )

        # Run orchestrator up to payload generation
        orchestrator = BeastSystemOrchestrator()
        result = orchestrator.process_member(raw_member_data)

        # Override submission result for simulation
        if result.get("submitted"):
            result["submitted"] = False
            result["simulation_mode"] = True

        self.audit.log(
            "pipeline_api_simulation_result",
            member_id,
            {"result": result}
        )

        return result


# Example deterministic run
if __name__ == "__main__":
    raw = {
        "member_id": "M-0007",
        "first_name": "Laura",
        "middle_initial": "K",
        "last_name": "Benson",
        "ssn_last4": "7788",
        "gender": "Female",
        "date_of_birth": "1988-04-19",
        "birth_country": "USA",
        "citizen": True,
        "disability_status": True,
        "disability_onset_date": "2024-09-01",
        "income_level": 19500.00,
        "preferred_language": "English",
        "compliance_flags": [
            "KYC_VERIFIED",
            "ADDRESS_CONFIRMED",
            "IDENTITY_VERIFIED",
            "PROFILE_COMPLETE"
        ]
    }

    api = PipelineAPI()
    result = api.apply_for_disability(raw)
    print(result)
