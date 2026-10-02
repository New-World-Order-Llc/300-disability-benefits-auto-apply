from datetime import datetime
from typing import Dict, Any, Callable, List

from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class PipelineHooks:
    """
    Deterministic pipeline hooks engine for Beast System 3.0 (Module 300).

    Provides:
    - Pre‑ingestion hooks
    - Pre‑validation hooks
    - Pre‑transformation hooks
    - Pre‑submission hooks
    - Post‑submission hooks
    - Deterministic ordering
    - Error‑safe execution
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

        # Deterministic hook registries
        self.pre_ingestion_hooks: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []
        self.pre_validation_hooks: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []
        self.pre_transformation_hooks: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []
        self.pre_submission_hooks: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []
        self.post_submission_hooks: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []

    def _run_hooks(self, hooks: List[Callable], data: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """
        Deterministically executes a list of hooks.
        Each hook receives and returns a data dictionary.
        """

        member_id = data.get("member_id", "UNKNOWN")

        for hook in hooks:
            try:
                data = hook(data)

                self.audit.log(
                    f"hook_executed_{stage}",
                    member_id,
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "stage": stage,
                        "hook": hook.__name__
                    }
                )

            except Exception as e:
                # Deterministic error capture
                data = self.recovery.capture(
                    e,
                    {
                        "member_id": member_id,
                        "stage": stage,
                        "hook": hook.__name__
                    }
                )

        return data

    # Registration methods
    def register_pre_ingestion(self, hook: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self.pre_ingestion_hooks.append(hook)

    def register_pre_validation(self, hook: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self.pre_validation_hooks.append(hook)

    def register_pre_transformation(self, hook: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self.pre_transformation_hooks.append(hook)

    def register_pre_submission(self, hook: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self.pre_submission_hooks.append(hook)

    def register_post_submission(self, hook: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self.post_submission_hooks.append(hook)

    # Execution methods
    def run_pre_ingestion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._run_hooks(self.pre_ingestion_hooks, data, "pre_ingestion")

    def run_pre_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._run_hooks(self.pre_validation_hooks, data, "pre_validation")

    def run_pre_transformation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._run_hooks(self.pre_transformation_hooks, data, "pre_transformation")

    def run_pre_submission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._run_hooks(self.pre_submission_hooks, data, "pre_submission")

    def run_post_submission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._run_hooks(self.post_submission_hooks, data, "post_submission")


# Example deterministic run
if __name__ == "__main__":
    hooks = PipelineHooks()

    # Example hook
    def add_flag(data):
        data["pipeline_flag"] = "PRE_INGESTION_OK"
        return data

    hooks.register_pre_ingestion(add_flag)

    example = {
        "member_id": "M-0020",
        "first_name": "Laura",
        "last_name": "Benson"
    }

    print("RUN PRE‑INGESTION HOOKS:")
    print(hooks.run_pre_ingestion(example))
