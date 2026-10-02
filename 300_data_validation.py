from datetime import datetime
from typing import Dict, Any, List

from 300_audit_logger import AuditLogger


class DataValidationEngine:
    """
    Deterministic data validation module for Beast System 3.0 (Module 300).
    Ensures all normalized member data meets structural, semantic,
    and compliance requirements before entering the pipeline.
    """

    def __init__(self):
        self.audit = AuditLogger()

    def validate_ssn_last4(self, value: str) -> bool:
        """
        Validates SSN last 4 digits:
        - Must be exactly 4 digits
        - Must be numeric
        """

        return (
            isinstance(value, str)
            and len(value) == 4
            and value.isdigit()
        )

    def validate_date(self, value: str) -> bool:
        """
        Validates ISO‑like date strings.
        """

        try:
            datetime.fromisoformat(value)
            return True
        except Exception:
            return False

    def validate_income(self, value: Any) -> bool:
        """
        Validates income:
        - Must be numeric
        - Must be non‑negative
        """

        try:
            v = float(value)
            return v >= 0
        except Exception:
            return False

    def validate_flags(self, flags: List[str]) -> bool:
        """
        Validates compliance flags:
        - Must be a list
        - Must contain only uppercase strings
        """

        if not isinstance(flags, list):
            return False

        for f in flags:
            if not isinstance(f, str):
                return False
            if f.upper() != f:
                return False

        return True

    def validate_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates all normalized profile fields deterministically.
        """

        member_id = profile.get("member_id", "UNKNOWN")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "member_id": member_id,
            "valid": True,
            "errors": []
        }

        # SSN last 4
        if not self.validate_ssn_last4(profile.get("ssn_last4", "")):
            results["valid"] = False
            results["errors"].append("Invalid SSN last 4 digits.")

        # Date of birth
        if not self.validate_date(profile.get("date_of_birth", "")):
            results["valid"] = False
            results["errors"].append("Invalid date_of_birth format.")

        # Disability onset date
        if not self.validate_date(profile.get("disability_onset_date", "")):
            results["valid"] = False
            results["errors"].append("Invalid disability_onset_date format.")

        # Income
        if not self.validate_income(profile.get("income_level", -1)):
            results["valid"] = False
            results["errors"].append("Invalid income_level value.")

        # Compliance flags
        if not self.validate_flags(profile.get("compliance_flags", [])):
            results["valid"] = False
            results["errors"].append("Invalid compliance_flags format.")

        self.audit.log("profile_validated", member_id, results)

        return results

    def validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates SSA‑16 payload fields deterministically.
        """

        member_id = payload.get("member_id", "UNKNOWN")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "member_id": member_id,
            "valid": True,
            "errors": []
        }

        # Timestamp
        if not self.validate_date(payload.get("timestamp", "")):
            results["valid"] = False
            results["errors"].append("Invalid payload timestamp.")

        # Application type
        if not isinstance(payload.get("application_type", ""), str):
            results["valid"] = False
            results["errors"].append("Invalid application_type.")

        self.audit.log("payload_validated", member_id, results)

        return results


# Example deterministic run
if __name__ == "__main__":
    validator = DataValidationEngine()

    profile = {
        "member_id": "M-0015",
        "ssn_last4": "1234",
        "date_of_birth": "1985-02-14",
        "disability_onset_date": "2024-07-01",
        "income_level": 18000.00,
        "compliance_flags": ["KYC_VERIFIED", "ADDRESS_CONFIRMED"]
    }

    print("PROFILE VALIDATION:")
    print(validator.validate_profile(profile))

    payload = {
        "member_id": "M-0015",
        "application_type": "SSA-16 Disability Insurance Benefits",
        "timestamp": "2026-10-02T15:00:00Z"
    }

    print("\nPAYLOAD VALIDATION:")
    print(validator.validate_payload(payload))
