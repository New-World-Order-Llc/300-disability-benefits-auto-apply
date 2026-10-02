import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from 300_audit_logger import AuditLogger
from 300_environment import EnvironmentLoader


class StorageAdapter:
    """
    Deterministic storage adapter for Beast System 3.0 (Module 300).
    Provides a unified interface for:
    - Local filesystem storage
    - Deterministic JSON read/write
    - Deterministic binary read/write
    - Future extension: S3, IPFS, database adapters

    All operations are logged and reproducible.
    """

    def __init__(self):
        self.env = EnvironmentLoader()
        self.audit = AuditLogger()

        self.base_path = self.env.get("STATE_FILE")
        self.default_dir = os.path.dirname(self.base_path) or "."

        if not os.path.exists(self.default_dir):
            os.makedirs(self.default_dir)

    def _full_path(self, filename: str) -> str:
        """
        Deterministically resolves a full path for a file.
        """

        return os.path.join(self.default_dir, filename)

    def write_json(self, filename: str, data: Dict[str, Any]) -> None:
        """
        Deterministically writes JSON to disk.
        """

        path = self._full_path(filename)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        self.audit.log(
            "storage_json_written",
            data.get("member_id", "SYSTEM"),
            {"filename": filename, "timestamp": datetime.utcnow().isoformat()}
        )

    def read_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Deterministically reads JSON from disk.
        Returns None if file does not exist.
        """

        path = self._full_path(filename)

        if not os.path.exists(path):
            self.audit.log(
                "storage_json_missing",
                "SYSTEM",
                {"filename": filename}
            )
            return None

        with open(path, "r") as f:
            data = json.load(f)

        self.audit.log(
            "storage_json_read",
            data.get("member_id", "SYSTEM"),
            {"filename": filename}
        )

        return data

    def write_bytes(self, filename: str, data: bytes) -> None:
        """
        Deterministically writes bytes to disk.
        """

        path = self._full_path(filename)

        with open(path, "wb") as f:
            f.write(data)

        self.audit.log(
            "storage_bytes_written",
            "SYSTEM",
            {"filename": filename, "size": len(data)}
        )

    def read_bytes(self, filename: str) -> Optional[bytes]:
        """
        Deterministically reads bytes from disk.
        Returns None if file does not exist.
        """

        path = self._full_path(filename)

        if not os.path.exists(path):
            self.audit.log(
                "storage_bytes_missing",
                "SYSTEM",
                {"filename": filename}
            )
            return None

        with open(path, "rb") as f:
            data = f.read()

        self.audit.log(
            "storage_bytes_read",
            "SYSTEM",
            {"filename": filename, "size": len(data)}
        )

        return data

    def exists(self, filename: str) -> bool:
        """
        Deterministically checks file existence.
        """

        path = self._full_path(filename)
        exists = os.path.exists(path)

        self.audit.log(
            "storage_exists_check",
            "SYSTEM",
            {"filename": filename, "exists": exists}
        )

        return exists


# Example deterministic run
if __name__ == "__main__":
    storage = StorageAdapter()

    example_json = {
        "member_id": "M-0018",
        "qualified": True,
        "submitted": False,
        "timestamp": datetime.utcnow().isoformat()
    }

    print("WRITE JSON:")
    storage.write_json("example.json", example_json)

    print("\nREAD JSON:")
    print(storage.read_json("example.json"))

    print("\nWRITE BYTES:")
    storage.write_bytes("example.bin", b"deterministic binary data")

    print("\nREAD BYTES:")
    print(storage.read_bytes("example.bin"))

    print("\nCHECK EXISTS:")
    print(storage.exists("example.json"))
