from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger
from 300_security import SecurityEngine


class CommunicationsEngine:
    """
    Deterministic communications module for Beast System 3.0 (Module 300).
    Provides outbound notifications, alerts, confirmations, and
    pipeline‑status messages with full audit logging and integrity guarantees.
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.security = SecurityEngine()

    def _build_message(self, member_id: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Constructs a deterministic message object.
        """

        message = {
            "timestamp": datetime.utcnow().isoformat(),
            "member_id": member_id,
            "subject": subject,
            "body": body
        }

        # Integrity signature
        message["signature"] = self.security.sign_payload(message)

        return message

    def send_notification(self, member_id: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Sends a deterministic outbound notification.
        Replace the stubbed send logic with your actual delivery system.
        """

        message = self._build_message(member_id, subject, body)

        self.audit.log("notification_sent", member_id, message)

        # Stubbed delivery action
        print("NOTIFICATION SENT:")
        print("Member:", member_id)
        print("Subject:", subject)
        print("Body:", body)

        return {
            "success": True,
            "delivered": True,
            "message": message
        }

    def send_pipeline_status(self, member_id: str, status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a deterministic pipeline‑status message.
        """

        subject = "Disability Benefits Pipeline Status Update"
        body = f"Pipeline status for member {member_id}: {status}"

        message = self._build_message(member_id, subject, body)

        self.audit.log("pipeline_status_sent", member_id, message)

        # Stubbed delivery action
        print("PIPELINE STATUS MESSAGE:")
        print("Member:", member_id)
        print("Status:", status)

        return {
            "success": True,
            "delivered": True,
            "message": message
        }

    def send_error_alert(self, member_id: str, error_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a deterministic error alert.
        """

        subject = "Pipeline Error Alert"
        body = f"An error occurred for member {member_id}: {error_details}"

        message = self._build_message(member_id, subject, body)

        self.audit.log("error_alert_sent", member_id, message)

        # Stubbed delivery action
        print("ERROR ALERT:")
        print("Member:", member_id)
        print("Error:", error_details)

        return {
            "success": True,
            "delivered": True,
            "message": message
        }


# Example deterministic run
if __name__ == "__main__":
    comms = CommunicationsEngine()

    print("\nTEST NOTIFICATION:")
    comms.send_notification(
        "M-0013",
        "Disability Application Received",
        "Your SSA‑16 disability application has been successfully submitted."
    )

    print("\nTEST PIPELINE STATUS:")
    comms.send_pipeline_status(
        "M-0013",
        {"qualified": True, "submitted": True}
    )

    print("\nTEST ERROR ALERT:")
    comms.send_error_alert(
        "M-0013",
        {"error": "Simulated pipeline failure for deterministic testing."}
    )
