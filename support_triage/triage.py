"""Classify synthetic service incidents and recommend diagnostic next steps."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence


SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


@dataclass(frozen=True)
class Incident:
    incident_id: str
    service: str
    status_code: int
    latency_ms: int
    error_rate: float
    retries: int
    message: str

    @classmethod
    def from_mapping(cls, value: Any, index: int) -> "Incident":
        if not isinstance(value, dict):
            raise ValueError(f"incident {index} must be a JSON object")

        required = {
            "incident_id",
            "service",
            "status_code",
            "latency_ms",
            "error_rate",
            "retries",
            "message",
        }
        missing = sorted(required.difference(value))
        if missing:
            raise ValueError(
                f"incident {index} is missing required fields: {', '.join(missing)}"
            )

        incident = cls(
            incident_id=_require_text(value["incident_id"], "incident_id", index),
            service=_require_text(value["service"], "service", index),
            status_code=_require_int(value["status_code"], "status_code", index),
            latency_ms=_require_int(value["latency_ms"], "latency_ms", index),
            error_rate=_require_number(value["error_rate"], "error_rate", index),
            retries=_require_int(value["retries"], "retries", index),
            message=_require_text(value["message"], "message", index),
        )
        incident.validate(index)
        return incident

    def validate(self, index: int) -> None:
        if not 100 <= self.status_code <= 599:
            raise ValueError(f"incident {index} status_code must be between 100 and 599")
        if self.latency_ms < 0:
            raise ValueError(f"incident {index} latency_ms cannot be negative")
        if not 0 <= self.error_rate <= 1:
            raise ValueError(f"incident {index} error_rate must be between 0 and 1")
        if self.retries < 0:
            raise ValueError(f"incident {index} retries cannot be negative")


@dataclass(frozen=True)
class TriageResult:
    incident_id: str
    service: str
    severity: str
    likely_category: str
    next_action: str
    evidence: tuple[str, ...]


def _require_text(value: Any, field: str, index: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"incident {index} {field} must be a non-empty string")
    return value.strip()


def _require_int(value: Any, field: str, index: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"incident {index} {field} must be an integer")
    return value


def _require_number(value: Any, field: str, index: int) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"incident {index} {field} must be a number")
    return float(value)


def load_incidents(path: Path) -> list[Incident]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"could not read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"{path} contains invalid JSON at line {error.lineno}, column {error.colno}"
        ) from error

    if not isinstance(raw, list):
        raise ValueError("input JSON must contain a list of incidents")
    if not raw:
        raise ValueError("input JSON must contain at least one incident")

    return [Incident.from_mapping(value, index) for index, value in enumerate(raw, 1)]


def determine_severity(incident: Incident) -> str:
    message = incident.message.lower()
    resource_failure = any(
        phrase in message for phrase in ("oomkilled", "out of memory", "disk full")
    )

    if resource_failure or incident.error_rate >= 0.5:
        return "critical"
    if (
        incident.error_rate >= 0.2
        or incident.latency_ms >= 3_000
        or (incident.status_code >= 500 and incident.retries >= 3)
    ):
        return "high"
    if (
        incident.status_code >= 400
        or incident.error_rate >= 0.05
        or incident.latency_ms >= 1_000
    ):
        return "medium"
    return "low"


def diagnose(incident: Incident) -> tuple[str, str, tuple[str, ...]]:
    message = incident.message.lower()
    evidence = [
        f"HTTP status {incident.status_code}",
        f"{incident.latency_ms} ms latency",
        f"{incident.error_rate:.1%} error rate",
        f"{incident.retries} retries",
    ]

    if any(phrase in message for phrase in ("oomkilled", "out of memory")):
        return (
            "resource exhaustion",
            "Inspect container termination reason and memory limits.",
            tuple(evidence + ["message reports an out-of-memory termination"]),
        )
    if "disk full" in message:
        return (
            "resource exhaustion",
            "Inspect filesystem utilization, growth rate, and retention settings.",
            tuple(evidence + ["message reports exhausted disk capacity"]),
        )
    if incident.status_code in (401, 403):
        return (
            "authentication or authorization",
            "Validate token scope, expiration, audience, and identity permissions.",
            tuple(evidence + ["response indicates an access-control failure"]),
        )
    if incident.status_code == 429:
        return (
            "rate limiting",
            "Inspect rate-limit headers and client backoff behavior.",
            tuple(evidence + ["response is HTTP 429"]),
        )
    if incident.status_code >= 500:
        return (
            "upstream dependency",
            "Compare upstream provider errors and request correlation IDs.",
            tuple(evidence + ["response is a server-side failure"]),
        )
    if any(phrase in message for phrase in ("timeout", "connection reset", "dns")):
        return (
            "network or dependency latency",
            "Compare client, network, and upstream timing with correlation IDs.",
            tuple(evidence + ["message contains a network or timeout signal"]),
        )
    if incident.latency_ms >= 1_000:
        return (
            "performance degradation",
            "Compare latency by dependency and inspect recent deployment changes.",
            tuple(evidence + ["latency exceeds the one-second triage threshold"]),
        )
    return (
        "no clear fault",
        "Continue monitoring and compare against the service baseline.",
        tuple(evidence),
    )


def analyze_incident(incident: Incident) -> TriageResult:
    category, next_action, evidence = diagnose(incident)
    return TriageResult(
        incident_id=incident.incident_id,
        service=incident.service,
        severity=determine_severity(incident),
        likely_category=category,
        next_action=next_action,
        evidence=evidence,
    )


def analyze(incidents: Sequence[Incident]) -> list[TriageResult]:
    results = [analyze_incident(incident) for incident in incidents]
    return sorted(
        results,
        key=lambda result: (
            -SEVERITY_RANK[result.severity],
            result.incident_id,
        ),
    )


def render_text(results: Sequence[TriageResult]) -> str:
    headers = ("SEVERITY", "INCIDENT", "SERVICE", "LIKELY CATEGORY", "NEXT ACTION")
    rows = [
        (
            result.severity.upper(),
            result.incident_id,
            result.service,
            result.likely_category,
            result.next_action,
        )
        for result in results
    ]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    def format_row(row: Sequence[str]) -> str:
        return "  ".join(
            value.ljust(widths[index]) for index, value in enumerate(row)
        ).rstrip()

    return "\n".join([format_row(headers), *(format_row(row) for row in rows)])


def render_json(results: Sequence[TriageResult]) -> str:
    return json.dumps([asdict(result) for result in results], indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prioritize synthetic service incidents for investigation."
    )
    parser.add_argument("input", type=Path, help="path to a JSON incident list")
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of a table",
    )
    parser.add_argument(
        "--fail-on",
        choices=tuple(SEVERITY_RANK),
        help="exit with status 2 when this severity or higher is present",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        results = analyze(load_incidents(args.input))
    except ValueError as error:
        print(f"support-triage: {error}", file=sys.stderr)
        return 1

    print(render_json(results) if args.json else render_text(results))

    if args.fail_on:
        threshold = SEVERITY_RANK[args.fail_on]
        if any(SEVERITY_RANK[result.severity] >= threshold for result in results):
            return 2
    return 0
