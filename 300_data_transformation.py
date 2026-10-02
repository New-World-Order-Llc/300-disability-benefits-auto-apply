from datetime import datetime
from typing import Dict, Any, List

from 300_audit_logger import AuditLogger


class DataTransformationEngine:
    """
    Deterministic data transformation module for Beast System 3.0 (Module 300).
    Provides canonical transformations:
    - Flattening nested structures
    - Expanding compact structures
    - Renaming fields deterministically
    - Converting lists to deterministic maps
    - Converting maps to deterministic lists
    - Structural reshaping for pipeline compatibility
    """

    def __init__(self):
        self.audit = AuditLogger()

    def flatten(self, data: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
        """
        Deterministically flattens nested dictionaries.
        Example:
            {"a": {"b": 1}} → {"a.b": 1}
        """

        items = {}

        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key

            if isinstance(value, dict):
                items.update(self.flatten(value, new_key, sep))
            else:
                items[new_key] = value

        return items

    def expand(self, flat: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
        """
        Deterministically expands flattened dictionaries.
        Example:
            {"a.b": 1} → {"a": {"b": 1}}
        """

        expanded = {}

        for key, value in flat.items():
            parts = key.split(sep)
            current = expanded

            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[parts[-1]] = value

        return expanded

    def rename_fields(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Deterministically renames fields according to a mapping table.
        """

        transformed = {}

        for key, value in data.items():
            new_key = mapping.get(key, key)
            transformed[new_key] = value

        return transformed

    def list_to_map(self, items: List[Any], key_prefix: str = "item") -> Dict[str, Any]:
        """
        Converts a list into a deterministic map:
        ["a", "b"] → {"item_0": "a", "item_1": "b"}
        """

        return {f"{key_prefix}_{i}": v for i, v in enumerate(items)}

    def map_to_list(self, mapping: Dict[str, Any]) -> List[Any]:
        """
        Converts a deterministic map back into a list.
        Assumes keys are in the form prefix_index.
        """

        sorted_items = sorted(mapping.items(), key=lambda x: int(x[0].split("_")[-1]))
        return [v for _, v in sorted_items]

    def transform_profile_for_pipeline(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies deterministic transformations to a member profile
        before pipeline ingestion.
        """

        transformed = self.flatten(profile)
        transformed["transformation_timestamp"] = datetime.utcnow().isoformat()

        self.audit.log(
            "profile_transformed",
            profile.get("member_id", "UNKNOWN"),
            transformed
        )

        return transformed

    def transform_payload_for_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies deterministic transformations to an SSA‑16 payload
        before submission.
        """

        transformed = self.flatten(payload)
        transformed["transformation_timestamp"] = datetime.utcnow().isoformat()

        self.audit.log(
            "payload_transformed",
            payload.get("member_id", "UNKNOWN"),
            transformed
        )

        return transformed


# Example deterministic run
if __name__ == "__main__":
    engine = DataTransformationEngine()

    nested_profile = {
        "member_id": "M-0016",
        "name": {
            "first": "Laura",
            "last": "Benson"
        },
        "contact": {
            "address": {
                "street": "123 Main St",
                "city": "Terre Haute"
            }
        }
    }

    print("FLATTENED PROFILE:")
    print(engine.transform_profile_for_pipeline(nested_profile))

    flat_payload = {
        "member_id": "M-0016",
        "application_type": "SSA-16",
        "disability.status": True,
