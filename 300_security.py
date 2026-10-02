import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger


class SecurityEngine:
    """
    Deterministic security and integrity module for Beast System 3.0 (Module 300).
    Provides:
    - Payload hashing
    - HMAC signing
    - Integrity verification
    - Tamper detection
    - Deterministic audit logging
    """

    def __init__(self, secret_key: str = "BEAST_SYSTEM_300_SECRET"):
        self.secret_key = secret_key.encode("utf-8")
        self.audit = AuditLogger()

    def hash_payload(self, payload: Dict[str, Any]) -> str:
        """
        Produces a deterministic SHA‑256 hash of a payload.
        """

        serialized = str(payload).encode("utf-8")
        digest = hashlib.sha256(serialized).hexdigest()

        self.audit.log(
            "payload_hashed",
            payload.get("member_id", "UNKNOWN"),
            {"hash": digest}
        )

        return digest

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        """
        Produces a deterministic HMAC signature for the payload.
        """

        serialized = str(payload).encode("utf-8")
        signature = hmac.new(self.secret_key, serialized, hashlib.sha256).hexdigest()

        self.audit.log(
            "payload_signed",
            payload.get("member_id", "UNKNOWN"),
            {"signature": signature}
        )

        return signature

    def verify_signature(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """
        Verifies that a payload matches its HMAC signature.
        Deterministic output: success/failure + details.
        """

        expected = self.sign_payload(payload)
        valid = (expected == signature)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "member_id": payload.get("member_id", "UNKNOWN"),
            "valid": valid,
            "expected_signature": expected,
            "provided_signature": signature
        }

        self.audit.log(
            "signature_verification",
            payload.get("member_id", "UNKNOWN"),
            result
        )

        return result

    def detect_tampering(self, original_hash: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detects whether a payload has been altered since hashing.
        """

        new_hash = self.hash_payload(payload)
        tampered = (new_hash != original_hash)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "member_id": payload.get("member_id", "UNKNOWN"),
            "tampered": tampered,
            "original_hash": original_hash,
            "current_hash": new_hash
        }

        self.audit.log(
            "tamper_detection",
            payload.get("member_id", "UNKNOWN"),
            result
        )

        return result


# Example deterministic run
if __name__ == "__main__":
    security = SecurityEngine()

    payload = {
        "member_id": "M-0012",
        "application_type": "SSA-16",
        "timestamp": datetime.utcnow().isoformat(),
        "income_level": 18000.00
    }

    print("HASH:")
    h = security.hash_payload(payload)
    print(h)

    print("\nSIGNATURE:")
    s = security.sign_payload(payload)
    print(s)

    print("\nVERIFY:")
    print(security.verify_signature(payload, s))

    print("\nTAMPER DETECTION:")
    tampered_payload = dict(payload)
    tampered_payload["income_level"] = 99999.00
    print(security.detect_tampering(h, tampered_payload))
