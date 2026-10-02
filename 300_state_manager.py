import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from 300_audit_logger import AuditLogger


class StateManager:
    """
    Deterministic state manager for Beast System 3.0 (Module 300).
    Stores and retrieves reproducible state snapshots for:
    - member profiles
    - eligibility evaluations
    - compliance checks
    - SSA‑16 payloads
    - submission results
    - pipeline runs
    """

    def __init__(self, state_file: str = "300_state.json"):
        self.state_file = state_file
        self.audit = AuditLogger()

        # Initialize state file if missing
        if not os.path.exists(self.state_file):
            with open(self.state_file, "w") as f:
                json.dump({"members": {}, "pipeline_runs": {}}, f)

    def _load_state(self) -> Dict[str, Any]:
        with open(self.state_file, "r") as f:
            return json.load(f)

    def _save_state(self, state: Dict[str, Any]) -> None:
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def save_member_state(self, member_id: str, data: Dict[str, Any]) -> None:
        """
        Saves deterministic member state.
        """

        state = self._load_state()
        state["members"][member_id] = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        self._save_state(state)

        self.audit.log("state_member_saved", member_id, data)

    def get_member_state(self, member_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves deterministic member state.
        """

        state = self._load_state()
        member_state = state["members"].get(member_id)

        self.audit.log("state_member_retrieved", member_id, {"exists": member_state is not None})

        return member_state

    def save_pipeline_run(self, member_id: str, result: Dict[str, Any]) -> None:
        """
        Saves deterministic pipeline run results.
        """

        state = self._load_state()
        run_id = f"{member_id}-{datetime.utcnow().isoformat()}"

        state["pipeline_runs"][run_id] = {
            "member_id": member_id,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }

        self._save_state(state)
        self.audit.log("state_pipeline_run_saved", member_id, result)

    def get_pipeline_runs(self, member_id: str) -> Dict[str, Any]:
        """
        Retrieves all deterministic pipeline runs for a member.
        """

        state = self._load_state()
        runs = {
            run_id: data
            for run_id, data in state["pipeline_runs"].items()
            if data["member_id"] == member_id
        }

        self.audit.log("state_pipeline_runs_retrieved", member_id, {"count": len(runs)})

        return runs


# Example deterministic run
if __name__ == "__main__":
    manager = StateManager()

    example_data = {
        "qualified": True,
        "submitted": True,
        "payload": {"application_type": "SSA-16"},
        "timestamp": datetime.utcnow().isoformat()
    }

    manager.save_member_state("M-0011", example_data)
    print(manager.get_member_state("M-0011"))

    manager.save_pipeline_run("M-0011", example_data)
    print(manager.get_pipeline_runs("M-0011"))
