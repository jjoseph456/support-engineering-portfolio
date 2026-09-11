import json
import tempfile
import unittest
from pathlib import Path

from support_triage.triage import (
    Incident,
    analyze,
    analyze_incident,
    load_incidents,
    main,
)


class TriageTests(unittest.TestCase):
    def incident(self, **overrides):
        values = {
            "incident_id": "INC-1",
            "service": "api",
            "status_code": 200,
            "latency_ms": 100,
            "error_rate": 0.0,
            "retries": 0,
            "message": "healthy",
        }
        values.update(overrides)
        return Incident(**values)

    def test_oom_is_critical_resource_exhaustion(self):
        result = analyze_incident(
            self.incident(
                status_code=503,
                error_rate=0.6,
                message="worker was OOMKilled",
            )
        )

        self.assertEqual("critical", result.severity)
        self.assertEqual("resource exhaustion", result.likely_category)

    def test_rate_limit_has_specific_next_action(self):
        result = analyze_incident(
            self.incident(status_code=429, error_rate=0.08)
        )

        self.assertEqual("medium", result.severity)
        self.assertEqual("rate limiting", result.likely_category)
        self.assertIn("backoff", result.next_action)

    def test_results_are_sorted_by_severity(self):
        results = analyze(
            [
                self.incident(incident_id="LOW"),
                self.incident(incident_id="HIGH", error_rate=0.3),
            ]
        )

        self.assertEqual(["HIGH", "LOW"], [result.incident_id for result in results])

    def test_loader_rejects_invalid_error_rate(self):
        payload = [
            {
                "incident_id": "INC-1",
                "service": "api",
                "status_code": 200,
                "latency_ms": 100,
                "error_rate": 1.5,
                "retries": 0,
                "message": "invalid",
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "incidents.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "between 0 and 1"):
                load_incidents(path)

    def test_fail_on_threshold_returns_two(self):
        payload = [
            {
                "incident_id": "INC-1",
                "service": "api",
                "status_code": 503,
                "latency_ms": 4000,
                "error_rate": 0.3,
                "retries": 4,
                "message": "upstream failed",
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "incidents.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            self.assertEqual(2, main([str(path), "--fail-on", "high"]))


if __name__ == "__main__":
    unittest.main()
