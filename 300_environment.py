import os
from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger


class EnvironmentLoader:
    """
    Deterministic environment loader for Beast System 3.0 (Module 300).
    Provides a single authoritative source for:
    - Runtime mode
    - File paths
    - Secrets
    - Network endpoints
    - Feature toggles
    """

    def __init__(self):
        self.audit = AuditLogger()

        # Deterministic environment defaults
        self.defaults = {
            "RUNTIME_MODE": "DEVELOPMENT",
            "AUDIT_LOG_PATH": "300_audit_log.jsonl",
            "STATE_FILE": "300_state.json",
            "SSA_ENDPOINT": "https://ssa.gov/api/submit",
            "ENABLE_AUTO_SUBMISSION": "true",
            "ENABLE_SIMULATION_MODE": "true",
            "SECRET_KEY": "BEAST_SYSTEM_300_SECRET"
        }

        self.environment = self._load_environment()

        self.audit.log(
            "environment_loaded",
            "SYSTEM",
            self.environment
        )

    def _load_environment(self) -> Dict[str, Any]:
        """
        Loads deterministic environment variables.
        If a variable is missing, the default is used.
        """

        env = {}

        for key, default in self.defaults.items():
            value = os.environ.get(key, default)
            env[key] = value

        env["timestamp"] = datetime.utcnow().isoformat()

        return env

    def get(self, key: str) -> Any:
        """
        Deterministically retrieves an environment value.
        """

        value = self.environment.get(key, None)

        self.audit.log(
            "environment_value_retrieved",
            "SYSTEM",
            {"key": key, "value": value}
        )

        return value

    def export(self) -> Dict[str, Any]:
        """
        Returns a deterministic snapshot of all environment values.
        """

        snapshot = dict(self.environment)

        self.audit.log(
            "environment_exported",
            "SYSTEM",
            snapshot
        )

        return snapshot


# Example deterministic run
if __name__ == "__main__":
    env = EnvironmentLoader()

    print("ENVIRONMENT SNAPSHOT:")
    print(env.export())

    print("\nGET SINGLE VALUE:")
    print(env.get("RUNTIME_MODE"))
