import argparse
from datetime import datetime

from 300_orchestrator import PipelineOrchestrator
from 300_state_manager import StateManager
from 300_metrics import MetricsEngine
from 300_audit_logger import AuditLogger


class BeastCLI:
    """
    Deterministic command-line interface for Beast System 3.0 (Module 300).

    Provides operator-level commands:
    - Run pipeline for a member
    - View member state
    - View pipeline history
    - View metrics snapshot
    - Manual audit log entry
    """

    def __init__(self):
        self.orchestrator = PipelineOrchestrator()
        self.state = StateManager()
        self.metrics = MetricsEngine()
        self.audit = AuditLogger()

    def run_pipeline(self, member_id: str):
        """
        Deterministically executes the full pipeline for a member.
        """

        self.metrics.increment("cli_pipeline_runs")

        result = self.orchestrator.run(member_id)

        self.audit.log(
            "cli_pipeline_run",
            member_id,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "result": result
            }
        )

        print("PIPELINE RESULT:")
        print(result)

    def view_state(self, member_id: str):
        """
        Displays deterministic member state.
        """

        state = self.state.get_member_state(member_id)

        self.audit.log(
            "cli_view_state",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        print("MEMBER STATE:")
        print(state)

    def view_history(self, member_id: str):
        """
        Displays deterministic pipeline run history.
        """

        history = self.state.get_pipeline_runs(member_id)

        self.audit.log(
            "cli_view_history",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        print("PIPELINE HISTORY:")
        print(history)

    def view_metrics(self):
        """
        Displays deterministic metrics snapshot.
        """

        snapshot = self.metrics.snapshot()

        self.audit.log(
            "cli_view_metrics",
            "SYSTEM",
            {"timestamp": datetime.utcnow().isoformat()}
        )

        print("METRICS SNAPSHOT:")
        print(snapshot)

    def manual_audit(self, event: str, member_id: str):
        """
        Allows operator to write a deterministic audit log entry.
        """

        self.audit.log(
            event,
            member_id,
            {"timestamp": datetime.utcnow().isoformat(), "cli_manual": True}
        )

        print("AUDIT ENTRY WRITTEN.")


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic CLI for Beast System 3.0 (Module 300)"
    )

    parser.add_argument("command", type=str, help="Command to execute")
    parser.add_argument("--member", type=str, help="Member ID")
    parser.add_argument("--event", type=str, help="Manual audit event")

    args = parser.parse_args()

    cli = BeastCLI()

    if args.command == "run":
        cli.run_pipeline(args.member)

    elif args.command == "state":
        cli.view_state(args.member)

    elif args.command == "history":
        cli.view_history(args.member)

    elif args.command == "metrics":
        cli.view_metrics()

    elif args.command == "audit":
        cli.manual_audit(args.event, args.member)

    else:
        print("Unknown command.")


if __name__ == "__main__":
    main()
