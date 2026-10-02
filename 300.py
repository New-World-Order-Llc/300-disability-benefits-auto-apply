"""Deterministic disability-benefits application orchestration."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Mapping, Protocol


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Unsupported profile value: {type(value).__name__}")


@dataclass(frozen=True)
class MemberProfile:
    member_id: str
    disability_status: bool
    annual_income: Decimal
    compliance_flags: Mapping[str, bool]
    identity_attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.member_id or not isinstance(self.member_id, str):
            raise ValueError("member_id must be a non-empty string")
        if not isinstance(self.disability_status, bool):
            raise ValueError("disability_status must be a boolean")
        try:
            income = Decimal(str(self.annual_income))
        except (InvalidOperation, ValueError) as error:
            raise ValueError("annual_income must be a finite number") from error
        if not income.is_finite() or income < 0:
            raise ValueError("annual_income must be a finite, non-negative number")
        object.__setattr__(self, "annual_income", income)
        if any(not isinstance(key, str) or not isinstance(value, bool)
               for key, value in self.compliance_flags.items()):
            raise ValueError("compliance_flags must map strings to booleans")
        if not isinstance(self.identity_attributes, Mapping):
            raise ValueError("identity_attributes must be a mapping")

    def as_dict(self) -> dict[str, Any]:
        return {
            "member_id": self.member_id,
            "disability_status": self.disability_status,
            "annual_income": str(self.annual_income),
            "compliance_flags": dict(self.compliance_flags),
            "identity_attributes": _json_value(self.identity_attributes),
        }


@dataclass(frozen=True)
class EligibilityPolicy:
    annual_income_limit: Decimal
    required_compliance_flags: tuple[str, ...] = ("kyc", "address", "identity")

    def __post_init__(self) -> None:
        try:
            limit = Decimal(str(self.annual_income_limit))
        except (InvalidOperation, ValueError) as error:
            raise ValueError("annual_income_limit must be a finite number") from error
        if not limit.is_finite() or limit < 0:
            raise ValueError("annual_income_limit must be a finite, non-negative number")
        object.__setattr__(self, "annual_income_limit", limit)
        if any(not isinstance(flag, str) or not flag for flag in self.required_compliance_flags):
            raise ValueError("required compliance flag names must be non-empty strings")


@dataclass(frozen=True)
class AuditEvent:
    timestamp: str
    action: str
    member_id: str
    details: Mapping[str, Any]


class AuditSink(Protocol):
    def write(self, event: AuditEvent) -> None: ...


@dataclass(frozen=True)
class SubmissionResult:
    success: bool
    submission_id: str
    status_code: int | None
    reason: str


@dataclass(frozen=True)
class ApiResponse:
    status_code: int


Transport = Callable[[str, Mapping[str, Any], float], ApiResponse]


def _http_transport(endpoint: str, payload: Mapping[str, Any], timeout: float) -> ApiResponse:
    request = urllib.request.Request(
        endpoint,
        data=_canonical_json(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return ApiResponse(response.status)
    except urllib.error.HTTPError as error:
        return ApiResponse(error.code)


class DisabilityBenefitsAutomation:
    """Checks compliance and eligibility before building or submitting an application."""

    def __init__(
        self,
        policy: EligibilityPolicy,
        endpoint: str,
        audit_sink: AuditSink,
        *,
        transport: Transport = _http_transport,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        timeout: float = 10.0,
    ) -> None:
        if not endpoint:
            raise ValueError("A benefits API endpoint is required")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.policy = policy
        self.endpoint = endpoint
        self.audit_sink = audit_sink
        self.transport = transport
        self.clock = clock
        self.timeout = timeout

    def _audit(self, action: str, profile: MemberProfile, details: Mapping[str, Any]) -> None:
        timestamp = self.clock()
        if timestamp.tzinfo is None:
            raise ValueError("audit clock must return a timezone-aware datetime")
        snapshot = {
            "action": action,
            "profile": profile.as_dict(),
            "details": _json_value(details),
        }
        event = AuditEvent(
            timestamp=timestamp.astimezone(timezone.utc).isoformat(),
            action=action,
            member_id=profile.member_id,
            details={
                **details,
                "state_sha256": hashlib.sha256(
                    _canonical_json(snapshot).encode("utf-8")
                ).hexdigest(),
            },
        )
        self.audit_sink.write(event)

    def verify_compliance(self, profile: MemberProfile) -> tuple[bool, tuple[str, ...]]:
        missing = tuple(
            flag for flag in self.policy.required_compliance_flags
            if profile.compliance_flags.get(flag) is not True
        )
        self._audit("compliance_check", profile, {
            "passed": not missing,
            "missing_flags": list(missing),
        })
        return not missing, missing

    def determine_eligibility(self, profile: MemberProfile) -> bool:
        eligible = (
            profile.disability_status
            and profile.annual_income <= self.policy.annual_income_limit
        )
        self._audit("eligibility_check", profile, {
            "eligible": eligible,
            "disability_status": profile.disability_status,
            "annual_income": str(profile.annual_income),
            "annual_income_limit": str(self.policy.annual_income_limit),
        })
        return eligible

    def build_payload(self, profile: MemberProfile) -> dict[str, Any]:
        application = {
            **_json_value(profile.identity_attributes),
            "member_id": profile.member_id,
            "disability_status": profile.disability_status,
            "annual_income": str(profile.annual_income),
        }
        payload_base = {
            "schema_version": "1.0",
            "application": application,
        }
        submission_id = hashlib.sha256(_canonical_json(payload_base).encode("utf-8")).hexdigest()
        payload = {**payload_base, "submission_id": submission_id}
        self._audit("payload_built", profile, {
            "submission_id": submission_id,
            "field_names": sorted(application),
        })
        return payload

    def apply(self, profile: MemberProfile) -> SubmissionResult:
        compliant, missing = self.verify_compliance(profile)
        if not compliant:
            self._audit("submission_halted", profile, {
                "reason": "compliance_failed",
                "missing_flags": list(missing),
            })
            return SubmissionResult(False, "", None, "compliance_failed")

        if not self.determine_eligibility(profile):
            self._audit("submission_halted", profile, {"reason": "ineligible"})
            return SubmissionResult(False, "", None, "ineligible")

        payload = self.build_payload(profile)
        submission_id = str(payload["submission_id"])
        self._audit("submission_started", profile, {"submission_id": submission_id})
        try:
            response = self.transport(self.endpoint, payload, self.timeout)
        except Exception as error:
            self._audit("submission_completed", profile, {
                "submission_id": submission_id,
                "success": False,
                "status_code": None,
                "reason": type(error).__name__,
            })
            return SubmissionResult(False, submission_id, None, type(error).__name__)

        success = 200 <= response.status_code < 300
        reason = "submitted" if success else "http_error"
        self._audit("submission_completed", profile, {
            "submission_id": submission_id,
            "success": success,
            "status_code": response.status_code,
            "reason": reason,
        })
        return SubmissionResult(success, submission_id, response.status_code, reason)
