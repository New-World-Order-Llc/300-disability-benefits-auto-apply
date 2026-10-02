"""Module 300 - deterministic disability-benefits auto-apply (Beast System 3.0).

Pipeline: ingest -> compliance -> eligibility -> auto-fill -> payload -> submit,
with every step recorded in a hash-chained audit log.

Determinism: no wall-clock, randomness or network access. The effective time is
supplied by the caller, and identical inputs always yield identical payloads,
IDs, audit hashes and outcomes. Governance is non-punitive: a non-compliant or
ineligible member is never penalised; the application is HELD or DECLINED with
plain remediation guidance and nothing is submitted.
"""
import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Dict, List, Optional

MODULE_ID = "300"
SYSTEM = "Beast System 3.0"
VERSION = "1.0.0"

REQUIRED_FIELDS = ("member_id", "full_name", "date_of_birth", "ssn_last4",
                   "address", "disability_type", "disability_onset_date",
                   "work_credits")
REQUIRED_COMPLIANCE_FLAGS = ("identity_verified", "consent_on_file",
                             "account_in_good_standing", "documents_current")
MIN_WORK_CREDITS = 20          # credits required for eligibility
MIN_AGE, MAX_AGE = 18, 66      # working-age band
FORMS = ("DB-APP-1 Application", "DB-MED-2 Medical Statement",
         "DB-AUTH-3 Authorization")


class IngestionError(ValueError):
    pass


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class AuditLog:
    """Append-only, hash-chained log; any edit breaks verify()."""
    entries: List[dict] = field(default_factory=list)

    def record(self, member_id: str, action: str, detail: dict, as_of: str) -> dict:
        prev = self.entries[-1]["hash"] if self.entries else "0" * 64
        body = {"seq": len(self.entries) + 1, "module": MODULE_ID, "system": SYSTEM,
                "member_id": member_id, "action": action, "as_of": as_of,
                "detail": detail, "prev_hash": prev}
        entry = dict(body, hash=_sha(_canon(body)))
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        prev = "0" * 64
        for e in self.entries:
            body = {k: v for k, v in e.items() if k != "hash"}
            if e["prev_hash"] != prev or e["hash"] != _sha(_canon(body)):
                return False
            prev = e["hash"]
        return True


def ingest_member_profile(raw: dict) -> dict:
    """Validate and normalise a member profile (pure, deterministic)."""
    if not isinstance(raw, dict):
        raise IngestionError("profile must be a mapping")
    missing = [f for f in REQUIRED_FIELDS if raw.get(f) in (None, "")]
    if missing:
        raise IngestionError("missing required fields: " + ", ".join(missing))
    try:
        dob = date.fromisoformat(str(raw["date_of_birth"]))
        onset = date.fromisoformat(str(raw["disability_onset_date"]))
        credits = int(raw["work_credits"])
    except (ValueError, TypeError) as exc:
        raise IngestionError("invalid date or numeric field: %s" % exc)
    if credits < 0:
        raise IngestionError("work_credits cannot be negative")
    flags = raw.get("compliance") or {}
    return {
        "member_id": str(raw["member_id"]).strip(),
        "full_name": " ".join(str(raw["full_name"]).split()),
        "date_of_birth": dob.isoformat(),
        "ssn_last4": str(raw["ssn_last4"]).strip(),
        "address": " ".join(str(raw["address"]).split()),
        "disability_type": str(raw["disability_type"]).strip().lower(),
        "disability_onset_date": onset.isoformat(),
        "work_credits": credits,
        "compliance": {k: flags.get(k) is True for k in REQUIRED_COMPLIANCE_FLAGS},
    }


def verify_compliance(profile: dict) -> dict:
    failed = [k for k in REQUIRED_COMPLIANCE_FLAGS if not profile["compliance"][k]]
    return {"compliant": not failed, "failed_flags": failed,
            "remediation": ["Please complete verification: " + k for k in failed]}


def _age(dob: str, as_of: str) -> int:
    d, a = date.fromisoformat(dob), date.fromisoformat(as_of)
    return a.year - d.year - ((a.month, a.day) < (d.month, d.day))


def determine_eligibility(profile: dict, as_of: str) -> dict:
    reasons = []
    age = _age(profile["date_of_birth"], as_of)
    if not MIN_AGE <= age <= MAX_AGE:
        reasons.append("age %d outside %d-%d" % (age, MIN_AGE, MAX_AGE))
    if profile["work_credits"] < MIN_WORK_CREDITS:
        reasons.append("work credits %d below %d" % (profile["work_credits"], MIN_WORK_CREDITS))
    if profile["disability_onset_date"] > as_of:
        reasons.append("disability onset date is in the future")
    return {"eligible": not reasons, "reasons": reasons, "age": age}


def autofill_documents(profile: dict, as_of: str) -> Dict[str, dict]:
    common = {"member_id": profile["member_id"], "full_name": profile["full_name"],
              "date_of_birth": profile["date_of_birth"], "address": profile["address"]}
    return {
        FORMS[0]: dict(common, ssn_last4=profile["ssn_last4"], filing_date=as_of,
                       work_credits=profile["work_credits"]),
        FORMS[1]: dict(common, disability_type=profile["disability_type"],
                       onset_date=profile["disability_onset_date"]),
        FORMS[2]: dict(common, consent_on_file=True, signed_date=as_of),
    }


def build_payload(profile: dict, documents: Dict[str, dict], as_of: str) -> dict:
    body = {"module": MODULE_ID, "system": SYSTEM, "version": VERSION,
            "member_id": profile["member_id"], "as_of": as_of, "documents": documents}
    digest = _sha(_canon(body))
    return dict(body, application_id="APP-%s-%s" % (profile["member_id"], digest[:12]),
                payload_sha256=digest)


def default_submitter(payload: dict) -> dict:
    """Deterministic offline submitter; replace with a real gateway if needed."""
    return {"status": "ACCEPTED", "confirmation": "CONF-" + payload["payload_sha256"][:16]}


@dataclass
class Result:
    status: str                      # SUBMITTED | HELD_COMPLIANCE | DECLINED_INELIGIBLE
    payload: Optional[dict] = None
    confirmation: Optional[dict] = None
    guidance: List[str] = field(default_factory=list)


def process_application(raw_profile: dict, as_of: str, audit: Optional[AuditLog] = None,
                        submitter: Callable[[dict], dict] = default_submitter) -> Result:
    """Run the full pipeline; submit only if compliant and eligible."""
    audit = audit if audit is not None else AuditLog()
    date.fromisoformat(as_of)
    mid = str(raw_profile.get("member_id", "UNKNOWN")) if isinstance(raw_profile, dict) else "UNKNOWN"
    try:
        profile = ingest_member_profile(raw_profile)
    except IngestionError as exc:
        audit.record(mid, "INGEST_REJECTED", {"error": str(exc)}, as_of)
        return Result("HELD_INVALID_PROFILE", guidance=[str(exc)])
    audit.record(mid, "PROFILE_INGESTED", {"profile_sha256": _sha(_canon(profile))}, as_of)

    comp = verify_compliance(profile)
    audit.record(mid, "COMPLIANCE_CHECKED", comp, as_of)
    if not comp["compliant"]:
        audit.record(mid, "SUBMISSION_HELD", {"reason": "compliance"}, as_of)
        return Result("HELD_COMPLIANCE", guidance=comp["remediation"])

    elig = determine_eligibility(profile, as_of)
    audit.record(mid, "ELIGIBILITY_DETERMINED", elig, as_of)
    if not elig["eligible"]:
        return Result("DECLINED_INELIGIBLE", guidance=elig["reasons"])

    docs = autofill_documents(profile, as_of)
    audit.record(mid, "DOCUMENTS_GENERATED", {"forms": list(docs)}, as_of)
    payload = build_payload(profile, docs, as_of)
    audit.record(mid, "PAYLOAD_BUILT", {"application_id": payload["application_id"],
                                        "payload_sha256": payload["payload_sha256"]}, as_of)
    confirmation = submitter(payload)
    audit.record(mid, "APPLICATION_SUBMITTED", confirmation, as_of)
    return Result("SUBMITTED", payload, confirmation)


if __name__ == "__main__":
    demo = {"member_id": "M1001", "full_name": "Jane Doe", "date_of_birth": "1975-04-02",
            "ssn_last4": "1234", "address": "1 Main St", "disability_type": "Musculoskeletal",
            "disability_onset_date": "2023-01-15", "work_credits": 40,
            "compliance": {k: True for k in REQUIRED_COMPLIANCE_FLAGS}}
    log = AuditLog()
    res = process_application(demo, "2026-01-01", log)
    print(res.status, res.confirmation)
    print(json.dumps(log.entries, indent=2), "chain valid:", log.verify())
