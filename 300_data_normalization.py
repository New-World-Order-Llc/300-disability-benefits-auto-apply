from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger


class DataNormalizationEngine:
    """
    Deterministic data normalization module for Beast System 3.0 (Module 300).
    Ensures all incoming member data is canonical, reproducible, and free
    from nondeterministic formatting variance.
    """

    def __init__(self):
        self.audit = AuditLogger()

    def normalize_string(self, value: Any) -> str:
        """
        Normalizes any string-like value:
        - Converts to string
        - Strips whitespace
        - Converts multiple spaces to single
        - Uppercases deterministic fields (names, flags)
        """

        if value is None:
            return ""

        s = str(value).strip()
        s = " ".join(s.split())  # collapse multiple spaces

        return s

    def normalize_name(self, value: Any) -> str:
        """
        Deterministic name normalization:
        - Strip whitespace
        - Title-case
        """

        s = self.normalize_string(value)
        return s.title()

    def normalize_flag(self, value: Any) -> str:
        """
        Deterministic compliance flag normalization:
        - Uppercase
        - Strip whitespace
        """

        s = self.normalize_string(value)
        return s.upper()

    def normalize_profile(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes all member profile fields deterministically.
        """

        normalized = {}

        for key, value in raw.items():
            if key in ["first_name", "middle_initial", "last_name"]:
                normalized[key] = self.normalize_name(value)

            elif key == "compliance_flags":
                normalized[key] = [self.normalize_flag(v) for v in value]

            elif isinstance(value, str):
                normalized[key] = self.normalize_string(value)

            else:
                normalized[key] = value

        normalized["normalization_timestamp"] = datetime.utcnow().isoformat()

        self.audit.log(
            "profile_normalized",
            raw.get("member_id", "UNKNOWN"),
            normalized
        )

        return normalized

    def normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes SSA‑16 payload fields deterministically.
        """

        normalized = {}

        for key, value in payload.items():
            if isinstance(value, str):
                normalized[key] = self.normalize_string(value)
            else:
                normalized[key] = value

        normalized["normalization_timestamp"] = datetime.utcnow().isoformat()

        self.audit.log(
            "payload_normalized",
            payload.get("member_id", "UNKNOWN"),
            normalized
        )

        return normalized


# Example deterministic run
if __name__ == "__main__":
    engine = DataNormalizationEngine()

    raw_profile = {
        "member_id": "M-0014",
        "first_name": "  laURA ",
        "middle_initial": " k ",
        "last_name": "  BENSON ",
        "preferred_language": " english ",
        "compliance_flags": [" kyc_verified ", " address_confirmed "]
    }

    print("NORMALIZED PROFILE:")
    print(engine.normalize_profile(raw_profile))

    payload = {
        "member_id": "M-0014",
        "application_type": " SSA-16 Disability Insurance Benefits ",
        "timestamp": " 2026-10-02T15:00:00Z "
    }

    print("\nNORMALIZED PAYLOAD:")
    print(engine.normalize_payload(payload))
