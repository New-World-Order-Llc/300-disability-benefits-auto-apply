import unittest
from datetime import datetime

from 300_data_normalization import DataNormalizationEngine
from 300_data_validation import DataValidationEngine
from 300_data_transformation import DataTransformationEngine
from 300_data_serialization import DataSerializationEngine
from 300_orchestrator import PipelineOrchestrator
from 300_state_manager import StateManager


class BeastSystemTests(unittest.TestCase):
    """
    Deterministic testing suite for Beast System 3.0 (Module 300).

    Provides:
    - Unit tests for normalization, validation, transformation, serialization
    - Integration tests for orchestrator
    - Reproducibility tests for state manager
    """

    def setUp(self):
        self.normalizer = DataNormalizationEngine()
        self.validator = DataValidationEngine()
        self.transformer = DataTransformationEngine()
        self.serializer = DataSerializationEngine()
        self.orchestrator = PipelineOrchestrator()
        self.state = StateManager()

    # ---------------------------
    # Normalization Tests
    # ---------------------------

    def test_normalization(self):
        raw = {
            "member_id": "M-TEST",
            "first_name": "  laURA ",
            "last_name": " BENSON ",
            "compliance_flags": [" kyc_verified ", " address_confirmed "]
        }

        normalized = self.normalizer.normalize_profile(raw)

        self.assertEqual(normalized["first_name"], "Laura")
        self.assertEqual(normalized["last_name"], "Benson")
        self.assertEqual(normalized["compliance_flags"], ["KYC_VERIFIED", "ADDRESS_CONFIRMED"])

    # ---------------------------
    # Validation Tests
    # ---------------------------

    def test_validation(self):
        profile = {
            "member_id": "M-TEST",
            "ssn_last4": "1234",
            "date_of_birth": "1985-02-14",
            "disability_onset_date": "2024-07-01",
            "income_level": 18000.00,
            "compliance_flags": ["KYC_VERIFIED"]
        }

        result = self.validator.validate_profile(profile)
        self.assertTrue(result["valid"])

    # ---------------------------
    # Transformation Tests
    # ---------------------------

    def test_transformation(self):
        nested = {
            "member_id": "M-TEST",
            "name": {"first": "Laura", "last": "Benson"}
        }

        flat = self.transformer.transform_profile_for_pipeline(nested)
        self.assertIn("name.first", flat)
        self.assertIn("name.last", flat)

    # ---------------------------
    # Serialization Tests
    # ---------------------------

    def test_serialization(self):
        data = {
            "member_id": "M-TEST",
            "qualified": True,
            "timestamp": "2026-10-02T15:00:00Z"
        }

        json_string = self.serializer.to_json(data)
        self.assertIsInstance(json_string, str)
        self.assertIn("qualified", json_string)

    # ---------------------------
    # Orchestrator Integration Test
    # ---------------------------

    def test_orchestrator_run(self):
        result = self.orchestrator.run("M-TEST")
        self.assertIn("success", result)

    # ---------------------------
    # State Manager Reproducibility Test
    # ---------------------------

    def test_state_manager(self):
        example = {
            "qualified": True,
            "submitted": False,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.state.save_member_state("M-TEST", example)
        retrieved = self.state.get_member_state("M-TEST")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["data"]["qualified"], True)


if __name__ == "__main__":
    unittest.main()
