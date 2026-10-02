import json
from datetime import datetime
from typing import Any, Dict

from 300_audit_logger import AuditLogger


class DataSerializationEngine:
    """
    Deterministic data serialization module for Beast System 3.0 (Module 300).
    Provides canonical serialization formats:
    - Deterministic JSON
    - Canonical string serialization
    - Canonical byte serialization
    - Stable ordering guarantees
    """

    def __init__(self):
        self.audit = AuditLogger()

    def to_json(self, data: Dict[str, Any]) -> str:
        """
        Deterministically serializes a dictionary to JSON.
        - Sorted keys
        - No nondeterministic whitespace
        """

        serialized = json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":")
        )

        self.audit.log(
            "serialized_json",
            data.get("member_id", "UNKNOWN"),
            {"json": serialized}
        )

        return serialized

    def from_json(self, json_string: str) -> Dict[str, Any]:
        """
        Deterministically deserializes JSON into a dictionary.
        """

        data = json.loads(json_string)

        self.audit.log(
            "deserialized_json",
            data.get("member_id", "UNKNOWN"),
            {"data": data}
        )

        return data

    def to_string(self, data: Dict[str, Any]) -> str:
        """
        Produces a canonical string representation:
        - Sorted keys
        - Deterministic formatting
        """

        parts = []

        for key in sorted(data.keys()):
            parts.append(f"{key}={data[key]}")

        serialized = "|".join(parts)

        self.audit.log(
            "serialized_string",
            data.get("member_id", "UNKNOWN"),
            {"string": serialized}
        )

        return serialized

    def to_bytes(self, data: Dict[str, Any]) -> bytes:
        """
        Deterministically serializes data into bytes.
        Uses canonical JSON as the underlying representation.
        """

        json_string = self.to_json(data)
        byte_data = json_string.encode("utf-8")

        self.audit.log(
            "serialized_bytes",
            data.get("member_id", "UNKNOWN"),
            {"bytes_length": len(byte_data)}
        )

        return byte_data

    def serialize_pipeline_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produces a deterministic serialization bundle for pipeline results.
        """

        bundle = {
            "timestamp": datetime.utcnow().isoformat(),
            "json": self.to_json(result),
            "string": self.to_string(result),
            "bytes": self.to_bytes(result)
        }

        self.audit.log(
            "pipeline_result_serialized",
            result.get("member_id", "UNKNOWN"),
            bundle
        )

        return bundle


# Example deterministic run
if __name__ == "__main__":
    engine = DataSerializationEngine()

    example = {
        "member_id": "M-0017",
        "qualified": True,
        "submitted": True,
        "income_level": 18000.00,
        "timestamp": "2026-10-02T15:00:00Z"
    }

    print("JSON:")
    print(engine.to_json(example))

    print("\nSTRING:")
    print(engine.to_string(example))

    print("\nBYTES:")
    print(engine.to_bytes(example))

    print("\nPIPELINE RESULT BUNDLE:")
    print(engine.serialize_pipeline_result(example))
