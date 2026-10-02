from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger
from 300_security import SecurityEngine
from 300_config import Config


class AuthorizationEngine:
    """
    Deterministic authorization module for Beast System 3.0 (Module 300).
    Ensures that only approved systems, agents, or processes can
    execute disability‑benefits automation actions.
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.security = SecurityEngine()
        self.config = Config()

        # Deterministic list of authorized callers
        self.authorized_callers = {
            "BEAST_SYSTEM_CORE",
            "NWO_HEALTH_PORTAL",
            "NWO_DAO_AUTOMATION",
            "PIPELINE_API",
            "SYSTEM_MONITOR",
            "SCHEDULER"
        }

    def is_authorized(self, caller_id: str) -> bool:
        """
        Determines whether a caller is authorized.
        """

        authorized = caller_id in self.authorized_callers

        self.audit.log(
            "authorization_check",
            caller_id,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "caller_id": caller_id,
                "authorized": authorized
            }
        )

        return authorized

    def require_authorization(self, caller_id: str) -> Dict[str, Any]:
        """
        Deterministic enforcement wrapper.
        Returns structured authorization result.
        """

        authorized = self.is_authorized(caller_id)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "caller_id": caller_id,
            "authorized": authorized
        }

        if not authorized:
            result["reason"] = "Caller is not authorized to execute Module 300 operations."

            self.audit.log(
                "authorization_denied",
                caller_id,
                result
            )

            return {
                "success": False,
                "authorized": False,
                "details": result
            }

        self.audit.log(
            "authorization_granted",
            caller_id,
            result
        )

        return {
            "success": True,
            "authorized": True,
            "details": result
        }

    def add_authorized_caller(self, caller_id: str) -> Dict[str, Any]:
        """
        Deterministically adds a new authorized caller.
        """

        self.authorized_callers.add(caller_id)

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "caller_id": caller_id,
            "action": "added_to_authorized_callers"
        }

        self.audit.log("authorization_added", caller_id, record)

        return {
            "success": True,
            "details": record
        }

    def remove_authorized_caller(self, caller_id: str) -> Dict[str, Any]:
        """
        Deterministically removes an authorized caller.
        """

        existed = caller_id in self.authorized_callers
        if existed:
            self.authorized_callers.remove(caller_id)

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "caller_id": caller_id,
            "action": "removed_from_authorized_callers",
            "existed": existed
        }

        self.audit.log("authorization_removed", caller_id, record)

        return {
            "success": True,
            "details": record
        }


# Example deterministic run
if __name__ == "__main__":
    auth = AuthorizationEngine()

    print("\nCHECK AUTHORIZED:")
    print(auth.require_authorization("PIPELINE_API"))

    print("\nCHECK UNAUTHORIZED:")
    print(auth.require_authorization("UNKNOWN_CALLER"))

    print("\nADD AUTHORIZED CALLER:")
    print(auth.add_authorized_caller("NEW_SYSTEM"))

    print("\nREMOVE AUTHORIZED CALLER:")
    print(auth.remove_authorized_caller("NEW_SYSTEM"))
