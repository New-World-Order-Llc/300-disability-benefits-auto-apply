from dataclasses import dataclass
from typing import List, Dict

# Deterministic compliance requirements for Beast System 3.0
REQUIRED_FLAGS = {
    "KYC_VERIFIED",
    "ADDRESS_CONFIRMED",
    "IDENTITY_VERIFIED",
    "PROFILE_COMPLETE"
}

# Example income threshold for disability qualification
INCOME_THRESHOLD = 32000.00


@dataclass
class MemberProfile:
    member_id: str
    disability_status: bool
    income_level: float
    compliance_flags: List[str]
    disability_onset_date: str


def check_compliance(member: MemberProfile) -> Dict:
    """
    Deterministic compliance verification.
    Ensures all required flags are present.
    """
    flags = set(member.compliance_flags)
    missing = REQUIRED_FLAGS - flags

    if missing:
        return {
            "member_id": member.member_id,
            "compliant": False,
            "missing_flags": list(missing),
            "reason": "Member account missing required compliance flags."
        }

    return {
        "member_id": member.member_id,
        "compliant": True,
        "missing_flags": [],
        "reason": "All compliance flags verified."
    }


def check_eligibility(member: MemberProfile) -> Dict:
    """
    Determines whether the member qualifies for disability benefits.
    """
    if not member.disability_status:
        return {
            "member_id": member.member_id,
            "eligible": False,
            "reason": "Member does not have a qualifying disability status."
        }

    if member.income_level > INCOME_THRESHOLD:
        return {
            "member_id": member.member_id,
            "eligible": False,
            "reason": "Income exceeds disability qualification threshold."
        }

    return {
        "member_id": member.member_id,
        "eligible": True,
        "reason": "Member meets disability and income eligibility criteria."
    }


def evaluate_member(member: MemberProfile) -> Dict:
    """
    Combined compliance + eligibility evaluation.
    This is the deterministic gatekeeper for auto‑application.
    """
    compliance = check_compliance(member)
    eligibility = check_eligibility(member)

    return {
        "member_id": member.member_id,
        "compliant": compliance["compliant"],
        "eligible": eligibility["eligible"],
        "compliance_details": compliance,
        "eligibility_details": eligibility,
        "qualified_for_auto_application": (
            compliance["compliant"] and eligibility["eligible"]
        )
    }


# Example deterministic run
if __name__ == "__main__":
    member = MemberProfile(
        member_id="M-0002",
        disability_status=True,
        income_level=24000.00,
        compliance_flags=[
            "KYC_VERIFIED",
            "ADDRESS_CONFIRMED",
            "IDENTITY_VERIFIED",
            "PROFILE_COMPLETE"
        ],
        disability_onset_date="2024-06-01"
    )

    result = evaluate_member(member)
    print(result)
