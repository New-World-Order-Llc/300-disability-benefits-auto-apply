from typing import Dict, Any


class SSA16FieldMapping:
    """
    Deterministic SSA‑16 field mapping module.
    Converts Beast System member profile attributes into
    SSA‑16 application fields without reproducing copyrighted form text.
    """

    def __init__(self):
        # Mapping table: Beast System field -> SSA‑16 field identifier
        self.mapping = {
            "first_name": "applicant.name.first",
            "middle_initial": "applicant.name.middle",
            "last_name": "applicant.name.last",
            "ssn_last4": "applicant.ssn_last4",
            "gender": "applicant.gender",
            "date_of_birth": "applicant.birth.date",
            "birth_country": "applicant.birth.country",
            "citizen": "applicant.citizenship.status",
            "preferred_language": "applicant.language.preferred",
            "disability_status": "disability.status",
            "disability_onset_date": "disability.onset.date",
            "income_level": "income.current",
            "compliance_flags": "system.compliance.flags"
        }

    def map_profile_to_ssa16(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a deterministic member profile dictionary into
        SSA‑16 structured fields using the mapping table.
        """

        mapped = {}

        for source_field, target_field in self.mapping.items():
            if source_field in profile:
                mapped[target_field] = profile[source_field]

        # Additional deterministic fields required for SSA‑16 submission
        mapped["application.type"] = "SSA-16 Disability Insurance Benefits"
        mapped["application.timestamp"] = profile.get("timestamp")

        return mapped


# Example deterministic run
if __name__ == "__main__":
    example_profile = {
        "first_name": "Michael",
        "middle_initial": "T",
        "last_name": "Reeves",
        "ssn_last4": "1122",
        "gender": "Male",
        "date_of_birth": "1975-09-22",
        "birth_country": "USA",
        "citizen": True,
        "preferred_language": "English",
        "disability_status": True,
        "disability_onset_date": "2024-04-01",
        "income_level": 19000.00,
        "compliance_flags": [
            "KYC_VERIFIED",
            "ADDRESS_CONFIRMED",
            "IDENTITY_VERIFIED",
            "PROFILE_COMPLETE"
        ],
        "timestamp": "2026-10-02T14:48:00Z"
    }

    mapper = SSA16FieldMapping()
    mapped_payload = mapper.map_profile_to_ssa16(example_profile)
    print(mapped_payload)
