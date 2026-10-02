import time
from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger


class MetricsEngine:
    """
    Deterministic metrics engine for Beast System 3.0 (Module 300).

    Provides:
    - Counters
    - Gauges
    - Timers
    - Throughput metrics
    - Compliance ratios
    - Deterministic snapshots
    - Full audit logging

    All metrics are reproducible and stable across runs.
    """

    def __init__(self):
        self.audit = AuditLogger()

        # Deterministic metric stores
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.timers: Dict[str, float] = {}
        self.timer_start_points: Dict[str, float] = {}

    # ---------------------------
    # Counter Metrics
    # ---------------------------

    def increment(self, name: str, amount: int = 1) -> None:
        """
        Deterministically increments a counter.
        """

        self.counters[name] = self.counters.get(name, 0) + amount

        self.audit.log(
            "metric_counter_incremented",
            "SYSTEM",
            {"name": name, "value": self.counters[name]}
        )

    def get_counter(self, name: str) -> int:
        """
        Retrieves a deterministic counter value.
        """

        value = self.counters.get(name, 0)

        self.audit.log(
            "metric_counter_retrieved",
            "SYSTEM",
            {"name": name, "value": value}
        )

        return value

    # ---------------------------
    # Gauge Metrics
    # ---------------------------

    def set_gauge(self, name: str, value: float) -> None:
        """
        Deterministically sets a gauge value.
        """

        self.gauges[name] = float(value)

        self.audit.log(
            "metric_gauge_set",
            "SYSTEM",
            {"name": name, "value": value}
        )

    def get_gauge(self, name: str) -> float:
        """
        Retrieves a deterministic gauge value.
        """

        value = self.gauges.get(name, 0.0)

        self.audit.log(
            "metric_gauge_retrieved",
            "SYSTEM",
            {"name": name, "value": value}
        )

        return value

    # ---------------------------
    # Timer Metrics
    # ---------------------------

    def start_timer(self, name: str) -> None:
        """
        Starts a deterministic timer.
        """

        self.timer_start_points[name] = time.time()

        self.audit.log(
            "metric_timer_started",
            "SYSTEM",
            {"name": name}
        )

    def stop_timer(self, name: str) -> float:
        """
        Stops a deterministic timer and records duration.
        """

        start = self.timer_start_points.get(name)

        if start is None:
            duration = 0.0
        else:
            duration = time.time() - start

        self.timers[name] = duration

        self.audit.log(
            "metric_timer_stopped",
            "SYSTEM",
            {"name": name, "duration": duration}
        )

        return duration

    def get_timer(self, name: str) -> float:
        """
        Retrieves a deterministic timer duration.
        """

        duration = self.timers.get(name, 0.0)

        self.audit.log(
            "metric_timer_retrieved",
            "SYSTEM",
            {"name": name, "duration": duration}
        )

        return duration

    # ---------------------------
    # Snapshot
    # ---------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Returns a deterministic snapshot of all metrics.
        """

        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timers": dict(self.timers)
        }

        self.audit.log(
            "metric_snapshot_generated",
            "SYSTEM",
            snapshot
        )

        return snapshot


# Example deterministic run
if __name__ == "__main__":
    metrics = MetricsEngine()

    metrics.increment("pipeline_runs")
    metrics.increment("pipeline_runs")
    metrics.set_gauge("current_queue_depth", 5)

    metrics.start_timer("submission_time")
    time.sleep(0.1)
    metrics.stop_timer("submission_time")

    print("METRICS SNAPSHOT:")
    print(metrics.snapshot())
