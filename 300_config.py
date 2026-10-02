from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass(frozen=True)
class CompliancePolicy:
    """
    Deterministic compliance policy for Module 300.
    Defines the required flags and conditions a member must meet
    before any disability‑benefits auto‑application can proceed.
    """
    required_flags: List[str]
    allow_missing_optional_fields: bool
    enforce_identity_verification: bool
    enforce_address_verification: bool


@dataclass(frozen=True)
class EligibilityPolicy:
    """
    Deterministic eligibility policy for disability benefits.
    Defines income thresholds, disability requirements,
    and any additional qualification rules.
    """
    income_threshold: float
    require_disability_status: bool
    require_onset_date: bool


@dataclass(frozen=True)
class SystemPolicy:
    """
    Global deterministic system policy for Beast System 3.0 (Module 300).
    Controls logging, scheduling, fallback behavior, and reproducibility guarantees.
    """
    audit_log_path: str
    scheduler_interval_seconds: int
    enable_simulation_mode: bool
    enable_auto_submission: bool
    enable_fallback_recovery: bool


class Config:
    """
    Centralized deterministic configuration manager.
    All modules import this file to ensure consistent rules and behavior.
    """

    def __init__(self):
        self.compliance = CompliancePolicy(
            required_flags=[
                "KYC_VERIFIED",
                "ADDRESS_CONFIRMED",
                "IDENTITY_VERIFIED",
                "PROFILE_COMPLETE"
            ],
            allow_missing_optional_fields=False,
            enforce_identity_verification=True,
            enforce_address_verification=True
        )

        self.eligibility = EligibilityPolicy(
            income_threshold=32000.00,
            require_disability_status=True,
            require_onset_date=True
        )

        self.system = SystemPolicy(
            audit_log_path="300_audit_log.jsonl",
            scheduler_interval_seconds=3600,
            enable_simulation_mode=True,
            enable_auto_submission=True,
            enable_fallback_recovery=True
        )

    def export(self) -> Dict[str, Any]:
        """
        Returns a deterministic snapshot of all configuration values.
        """

        return {
            "compliance_policy": {
                "required_flags": self.compliance.required_flags,
                "allow_missing_optional_fields": self.compliance.allow_missing_optional_fields,
                "enforce_identity_verification": self.compliance.enforce_identity_verification,
                "enforce_address_verification": self.compliance.enforce_address_verification
            },
            "eligibility_policy": {
                "income_threshold": self.eligibility.income_threshold,
                "require_disability_status": self.eligibility.require_disability_status,
                "require_onset_date": self.eligibility.require_onset_date
            },
            "system_policy": {
                "audit_log_path": self.system.audit_log_path,
                "scheduler_interval_seconds": self.system.scheduler_interval_seconds,
                "enable_simulation_mode": self.system.enable_simulation_mode,
                "enable_auto_submission": self.system.enable_auto_submission,
                "enable_fallback_recovery": self.system.enable_fallback_recovery
            }
        }


# Example deterministic run
if __name__ == "__main__":
    config = Config()
    snapshot = config.export()
    print(snapshot)
