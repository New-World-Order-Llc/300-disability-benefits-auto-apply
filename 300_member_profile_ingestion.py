from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class MemberProfile:
    """
    Deterministic member profile structure for Beast System 3.0.
    All disability‑benefit automation modules depend on this schema.
    """
    member_id: str
    first_name: str
    middle_initial: str
    last_name: str
    ssn_last4: str
    gender: str
    date_of_birth: str
    birth_country: str
    citizen: bool
    disability_status: bool
    disability_onset_date: str
    income_level: float
    preferred_language: str
    compliance_flags: List[str]


class MemberProfileIngestion:
    """
    Ingests raw member data and converts it into a deterministic MemberProfile object.
    Ensures all required fields exist and normalizes formats.
    """

    REQUIRED_FIELDS = {
        "member_id",
        "first_name",
        "middle_initial",
        "last_name",
        "ssn_last4",
        "gender",
        "date_of_birth",
        "birth_country",
        "citizen",
        "disability_status",
        "disability_onset_date",
        "income_level",
        "preferred_language",
        "compliance_flags"
    }

    def validate_raw(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures all required fields are present.
        Returns a deterministic validation result.
        """

        missing = self.REQUIRED_FIELDS - set(raw.keys())

        if missing:
            return {
                "valid": False,
                "missing_fields": list(missing),
                "reason": "Raw member data missing required fields."
            }

        return {
            "valid": True,
            "missing_fields": [],
            "reason": "All required fields present."
        }

    def ingest(self, raw: Dict[str, Any]) -> MemberProfile:
        """
        Converts raw input into a deterministic MemberProfile object.
        Assumes validation has already passed.
        """

        return MemberProfile(
            member_id=str(raw["member_id"]),
            first_name=str(raw["first_name"]),
            middle_initial=str(raw["middle_initial"]),
            last_name=str(raw["last_name"]),
            ssn_last4=str(raw["ssn_last4"]),
            gender=str(raw["gender"]),
            date_of_birth=str(raw["date_of_birth"]),
            birth_country=str(raw["birth_country"]),
            citizen=bool(raw["citizen"]),
            disability_status=bool(raw["disability_status"]),
            disability_onset_date=str(raw["disability_onset_date"]),
            income_level=float(raw["income_level"]),
            preferred_language=str(raw["preferred_language"]),
            compliance_flags=list(raw["compliance_flags"])
        )


# Example deterministic run
if __name__ == "__main__":
    raw_data = {
        "member_id": "M-0004",
        "first_name": "Sarah",
        "middle_initial": "L",
        "last_name": "Carter",
        "ssn_last4": "9988",
        "gender": "Female",
        "date_of_birth": "1979-03-12",
        "birth_country": "USA",
        "citizen": True,
        "disability_status": True,
        "disability_onset_date": "2024-05-10",
        "income_level": 21000.00,
        "preferred_language": "English",
        "compliance_flags": [
            "KYC_VERIFIED",
            "ADDRESS_CONFIRMED",
            "IDENTITY_VERIFIED",
            "PROFILE_COMPLETE"
        ]
    }

    ingestion = MemberProfileIngestion()
    validation = ingestion.validate_raw(raw_data)
    print(validation)

    if validation["valid"]:
        profile = ingestion.ingest(raw_data)
        print(profile)
