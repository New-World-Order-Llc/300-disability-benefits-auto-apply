import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional

from 300_audit_logger import AuditLogger
from 300_environment import EnvironmentLoader
from 300_error_recovery import ErrorRecovery


class NetworkAdapter:
    """
    Deterministic network adapter for Beast System 3.0 (Module 300).
    Provides:
    - Deterministic outbound HTTP requests
    - SSA submission stubs
    - DAO / Health & Wellbeing API stubs
    - Deterministic retry logic
    - Full audit logging
    - Error‑safe execution
    """

    def __init__(self):
        self.env = EnvironmentLoader()
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "BeastSystem300/1.0"
        }

        self.max_retries = 3

    def _request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic HTTP POST request with retry logic.
        """

        serialized = json.dumps(payload).encode("utf-8")

        for attempt in range(1, self.max_retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    data=serialized,
                    headers=self.default_headers,
                    method="POST"
                )

                with urllib.request.urlopen(req) as response:
                    body = response.read().decode("utf-8")
                    result = json.loads(body)

                    self.audit.log(
                        "network_request_success",
                        payload.get("member_id", "SYSTEM"),
                        {
                            "url": url,
                            "attempt": attempt,
                            "response": result
                        }
                    )

                    return {
                        "success": True,
                        "attempt": attempt,
                        "response": result
                    }

            except urllib.error.HTTPError as e:
                error_details = {
                    "url": url,
                    "attempt": attempt,
                    "status": e.code,
                    "reason": e.reason
                }

                self.audit.log(
                    "network_http_error",
                    payload.get("member_id", "SYSTEM"),
                    error_details
                )

            except urllib.error.URLError as e:
                error_details = {
                    "url": url,
                    "attempt": attempt,
                    "reason": str(e)
                }

                self.audit.log(
                    "network_url_error",
                    payload.get("member_id", "SYSTEM"),
                    error_details
                )

        # All retries failed — deterministic fallback
        return self.recovery.fallback(
            {
                "member_id": payload.get("member_id", "SYSTEM"),
                "url": url,
                "payload": payload
            }
        )

    def submit_to_ssa(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic SSA submission stub.
        Uses SSA_ENDPOINT from environment.
        """

        url = self.env.get("SSA_ENDPOINT")

        self.audit.log(
            "ssa_submission_attempt",
            payload.get("member_id", "SYSTEM"),
            {"url": url}
        )

        return self._request(url, payload)

    def post_to_nwo_dao(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic stub for posting to New World Order DAO systems.
        """

        url = "https://nwo-dao.example/api/ingest"

        self.audit.log(
            "dao_post_attempt",
            payload.get("member_id", "SYSTEM"),
            {"url": url}
        )

        return self._request(url, payload)

    def post_to_health_wellbeing(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic stub for posting to New World Order Health & Wellbeing systems.
        """

        url = "https://nwo-health.example/api/ingest"

        self.audit.log(
            "health_post_attempt",
            payload.get("member_id", "SYSTEM"),
            {"url": url}
        )

        return self._request(url, payload)


# Example deterministic run
if __name__ == "__main__":
    net = NetworkAdapter()

    example_payload = {
        "member_id": "M-0019",
        "application_type": "SSA-16",
        "timestamp": datetime.utcnow().isoformat(),
        "qualified": True,
        "submitted": False
    }

    print("SSA SUBMISSION:")
    print(net.submit_to_ssa(example_payload))

    print("\nDAO POST:")
    print(net.post_to_nwo_dao(example_payload))

    print("\nHEALTH & WELLBEING POST:")
    print(net.post_to_health_wellbeing(example_payload))
