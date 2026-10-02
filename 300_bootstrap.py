from datetime import datetime

from 300_environment import EnvironmentLoader
from 300_state_manager import StateManager
from 300_orchestrator import PipelineOrchestrator
from 300_metrics import MetricsEngine
from 300_audit_logger import AuditLogger
from 300_storage_adapter import StorageAdapter
from 300_network_adapter import NetworkAdapter
from 300_pipeline_hooks import PipelineHooks
from 300_data_normalization import DataNormalizationEngine
from 300_data_validation import DataValidationEngine
from 300_data_transformation import DataTransformationEngine
from 300_data_serialization import DataSerializationEngine
from 300_authorization import AuthorizationEngine
from 300_security import SecurityEngine
from 300_communications import CommunicationsEngine


class BeastSystemBootstrap:
    """
    Deterministic bootstrapper for Beast System 3.0 (Module 300).

    Responsibilities:
    - Initialize all modules
    - Wire dependencies
    - Register pipeline hooks
    - Produce a unified system object
    - Guarantee deterministic startup
    """

    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat()

        # Core systems
        self.env = EnvironmentLoader()
        self.audit = AuditLogger()
        self.state = StateManager()
        self.metrics = MetricsEngine()
        self.security = SecurityEngine()
        self.auth = AuthorizationEngine()

        # Data pipeline components
        self.normalizer = DataNormalizationEngine()
        self.validator = DataValidationEngine()
        self.transformer = DataTransformationEngine()
        self.serializer = DataSerializationEngine()

        # External interfaces
        self.storage = StorageAdapter()
        self.network = NetworkAdapter()
        self.comms = CommunicationsEngine()

        # Hooks
        self.hooks = PipelineHooks()

        # Orchestrator
        self.orchestrator = PipelineOrchestrator()

        # Register deterministic hooks
        self._register_hooks()

        # Log bootstrap event
        self.audit.log(
            "system_bootstrapped",
            "SYSTEM",
            {"timestamp": self.timestamp}
        )

    def _register_hooks(self):
        """
        Registers deterministic pipeline hooks.
        """

        def hook_add_bootstrap_flag(data):
            data["bootstrap_flag"] = "BOOTSTRAPPED_OK"
            return data

        def hook_timestamp(data):
            data["hook_timestamp"] = datetime.utcnow().isoformat()
            return data

        self.hooks.register_pre_ingestion(hook_add_bootstrap_flag)
        self.hooks.register_pre_validation(hook_timestamp)

        self.audit.log(
            "hooks_registered",
            "SYSTEM",
            {
                "timestamp": datetime.utcnow().isoformat(),
                "hooks": ["hook_add_bootstrap_flag", "hook_timestamp"]
            }
        )

    def system(self) -> dict:
        """
        Returns a deterministic snapshot of the entire system.
        """

        snapshot = {
            "timestamp": self.timestamp,
            "environment": self.env.export(),
            "modules": [
                "EnvironmentLoader",
                "AuditLogger",
                "StateManager",
                "MetricsEngine",
                "SecurityEngine",
                "AuthorizationEngine",
                "DataNormalizationEngine",
                "DataValidationEngine",
                "DataTransformationEngine",
                "DataSerializationEngine",
                "StorageAdapter",
                "NetworkAdapter",
                "CommunicationsEngine",
                "PipelineHooks",
                "PipelineOrchestrator"
            ]
        }

        self.audit.log(
            "system_snapshot_generated",
            "SYSTEM",
            snapshot
        )

        return snapshot


# Example deterministic run
if __name__ == "__main__":
    bootstrap = BeastSystemBootstrap()

    print("SYSTEM SNAPSHOT:")
    print(bootstrap.system())

    print("\nRUN PIPELINE FOR TEST MEMBER:")
    result = bootstrap.orchestrator.run("M-BOOTSTRAP")
    print(result)
