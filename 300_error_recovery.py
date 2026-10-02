import traceback
from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger


class ErrorRecovery:
    """
    Deterministic error handling and recovery module for Beast System 3.0 (Module 300).
    Ensures that any failure in the disability‑benefits pipeline is captured,
    logged, isolated, and recoverable without halting the system.
    """

    def __init__(self, audit_log_path: str = "300_audit_log.jsonl"):
        self.audit = AuditLogger(audit_log_path)

    def capture(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Captures an exception, logs it deterministically, and returns
        a structured error object for upstream modules.
        """

        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context
        }

        member_id = context.get("member_id", "UNKNOWN")
        self.audit.log("error_captured", member_id, error_record)

        return {
            "success": False,
            "recoverable": True,
            "details": error_record
        }

    def safe_execute(self, operation, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an operation with deterministic error protection.
        If the operation fails, the error is captured and returned
        without halting the pipeline.
        """

        try:
            result = operation()
            return {
                "success": True,
                "recoverable": True,
                "result": result
            }
        except Exception as e:
            return self.capture(e, context)

    def fallback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic fallback behavior when a pipeline step fails.
        Ensures the system continues operating and provides a safe,
        reproducible output.
        """

        fallback_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "member_id": context.get("member_id", "UNKNOWN"),
            "fallback_action": "Pipeline step failed; safe fallback executed.",
            "context": context
        }

        self.audit.log("fallback_triggered", context.get("member_id", "UNKNOWN"), fallback_record)

        return {
            "success": False,
            "recoverable": True,
            "fallback": True,
            "details": fallback_record
        }


# Example deterministic run
if __name__ == "__main__":
    recovery = ErrorRecovery()

    def failing_operation():
        raise ValueError("Simulated failure for deterministic testing.")

    context = {
        "member_id": "M-0010",
        "operation": "test_failure"
    }

    print("SAFE EXECUTION RESULT:")
    print(recovery.safe_execute(failing_operation, context))

    print("\nFALLBACK RESULT:")
    print(recovery.fallback(context))
