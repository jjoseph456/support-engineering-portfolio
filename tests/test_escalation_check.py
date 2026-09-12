import json
import tempfile
import unittest
from pathlib import Path

from escalation_check.checker import EscalationPackage, check_package, load_package, main


class EscalationCheckTests(unittest.TestCase):
    def package_data(self):
        return {
            "incident_id": "INC-1",
            "summary": "Requests fail when concurrency rises above the test baseline",
            "impact": "Thirty percent of synthetic requests fail in the test environment.",
            "started_at": "2026-09-12T01:00:00Z",
            "affected_services": ["runtime"],
            "reproduction_steps": ["Raise concurrency.", "Submit requests."],
            "evidence": [
                {
                    "id": "E1",
                    "observed_at": "2026-09-12T01:05:00Z",
                    "source": "request log",
                    "observation": "Three of ten requests returned HTTP 503.",
                }
            ],
            "hypotheses": [
                {
                    "statement": "The runtime may be resource constrained.",
                    "status": "unverified",
                    "evidence_refs": ["E1"],
                }
            ],
            "workaround_status": "Reducing concurrency avoids the failure.",
            "engineering_question": "Can engineering confirm the resource limit?",
            "customer_update": {
                "current_impact": "Synthetic requests remain degraded.",
                "actions_taken": "The issue was reproduced and a workaround identified.",
                "next_update_at": "2026-09-12T01:30:00Z",
            },
        }

    def test_complete_package_is_ready(self):
        result = check_package(EscalationPackage.from_mapping(self.package_data()))

        self.assertTrue(result.ready)
        self.assertEqual(100, result.score)
        self.assertEqual(0, result.errors)

    def test_confirmed_hypothesis_requires_evidence(self):
        data = self.package_data()
        data["hypotheses"][0]["status"] = "confirmed"
        data["hypotheses"][0]["evidence_refs"] = []

        result = check_package(EscalationPackage.from_mapping(data))

        self.assertFalse(result.ready)
        self.assertTrue(
            any(
                finding.field == "hypotheses[0].evidence_refs"
                and finding.level == "error"
                for finding in result.findings
            )
        )

    def test_invalid_timestamp_is_an_error(self):
        data = self.package_data()
        data["started_at"] = "last Tuesday"

        result = check_package(EscalationPackage.from_mapping(data))

        self.assertEqual(1, result.errors)
        self.assertFalse(result.ready)

    def test_loader_rejects_missing_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "escalation.json"
            path.write_text(json.dumps({"incident_id": "INC-1"}), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing required fields"):
                load_package(path)

    def test_minimum_score_gate(self):
        data = self.package_data()
        data["summary"] = "Too short"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "escalation.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            self.assertEqual(2, main([str(path), "--minimum-score", "100"]))


if __name__ == "__main__":
    unittest.main()
