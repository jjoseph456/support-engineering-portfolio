"""Check whether a synthetic support escalation is ready for engineering."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence


@dataclass(frozen=True)
class EscalationPackage:
    incident_id: str
    summary: str
    impact: str
    started_at: str
    affected_services: tuple[str, ...]
    reproduction_steps: tuple[str, ...]
    evidence: tuple[dict[str, Any], ...]
    hypotheses: tuple[dict[str, Any], ...]
    workaround_status: str
    engineering_question: str
    customer_update: dict[str, Any]

    @classmethod
    def from_mapping(cls, value: Any) -> "EscalationPackage":
        if not isinstance(value, dict):
            raise ValueError("escalation input must be a JSON object")

        required = {
            "incident_id",
            "summary",
            "impact",
            "started_at",
            "affected_services",
            "reproduction_steps",
            "evidence",
            "hypotheses",
            "workaround_status",
            "engineering_question",
            "customer_update",
        }
        missing = sorted(required.difference(value))
        if missing:
            raise ValueError(f"missing required fields: {', '.join(missing)}")

        return cls(
            incident_id=_text(value["incident_id"], "incident_id"),
            summary=_text(value["summary"], "summary"),
            impact=_text(value["impact"], "impact"),
            started_at=_text(value["started_at"], "started_at"),
            affected_services=_text_list(
                value["affected_services"], "affected_services"
            ),
            reproduction_steps=_text_list(
                value["reproduction_steps"], "reproduction_steps"
            ),
            evidence=_object_list(value["evidence"], "evidence"),
            hypotheses=_object_list(value["hypotheses"], "hypotheses"),
            workaround_status=_text(
                value["workaround_status"], "workaround_status"
            ),
            engineering_question=_text(
                value["engineering_question"], "engineering_question"
            ),
            customer_update=_object(value["customer_update"], "customer_update"),
        )


@dataclass(frozen=True)
class Finding:
    level: str
    field: str
    message: str


@dataclass(frozen=True)
class CheckResult:
    incident_id: str
    score: int
    ready: bool
    errors: int
    warnings: int
    findings: tuple[Finding, ...]


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    return tuple(_text(item, f"{field}[{index}]") for index, item in enumerate(value))


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object")
    return value


def _object_list(value: Any, field: str) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    return tuple(_object(item, f"{field}[{index}]") for index, item in enumerate(value))


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _add(
    findings: list[Finding],
    condition: bool,
    level: str,
    field: str,
    message: str,
) -> None:
    if condition:
        findings.append(Finding(level=level, field=field, message=message))


def check_package(package: EscalationPackage) -> CheckResult:
    findings: list[Finding] = []

    _add(
        findings,
        len(package.summary) < 20,
        "warning",
        "summary",
        "Summary is too short to distinguish the failure.",
    )
    _add(
        findings,
        len(package.impact) < 40,
        "warning",
        "impact",
        "Impact should identify affected users, behavior, and scope.",
    )
    _add(
        findings,
        not _valid_timestamp(package.started_at),
        "error",
        "started_at",
        "Use an ISO 8601 timestamp with a time zone.",
    )
    _add(
        findings,
        len(package.reproduction_steps) < 2,
        "error",
        "reproduction_steps",
        "Provide at least two ordered reproduction steps.",
    )

    evidence_ids: set[str] = set()
    for index, item in enumerate(package.evidence):
        prefix = f"evidence[{index}]"
        evidence_id = item.get("id")
        _add(
            findings,
            not isinstance(evidence_id, str) or not evidence_id.strip(),
            "error",
            f"{prefix}.id",
            "Evidence requires a stable identifier.",
        )
        if isinstance(evidence_id, str) and evidence_id.strip():
            evidence_ids.add(evidence_id.strip())
        _add(
            findings,
            not _valid_timestamp(item.get("observed_at")),
            "error",
            f"{prefix}.observed_at",
            "Evidence requires an ISO 8601 observation timestamp.",
        )
        for field in ("source", "observation"):
            _add(
                findings,
                not isinstance(item.get(field), str) or not item[field].strip(),
                "error",
                f"{prefix}.{field}",
                f"Evidence requires a non-empty {field}.",
            )

    allowed_statuses = {"unverified", "confirmed", "ruled_out"}
    for index, item in enumerate(package.hypotheses):
        prefix = f"hypotheses[{index}]"
        status = item.get("status")
        references = item.get("evidence_refs")
        _add(
            findings,
            not isinstance(item.get("statement"), str)
            or not item["statement"].strip(),
            "error",
            f"{prefix}.statement",
            "Hypothesis requires a clear statement.",
        )
        _add(
            findings,
            status not in allowed_statuses,
            "error",
            f"{prefix}.status",
            "Status must be unverified, confirmed, or ruled_out.",
        )
        _add(
            findings,
            not isinstance(references, list),
            "error",
            f"{prefix}.evidence_refs",
            "evidence_refs must be a list.",
        )
        if isinstance(references, list):
            unknown = [
                reference
                for reference in references
                if not isinstance(reference, str) or reference not in evidence_ids
            ]
            _add(
                findings,
                bool(unknown),
                "error",
                f"{prefix}.evidence_refs",
                "Hypothesis references unknown evidence.",
            )
            _add(
                findings,
                status == "confirmed" and not references,
                "error",
                f"{prefix}.evidence_refs",
                "A confirmed hypothesis must reference supporting evidence.",
            )
            _add(
                findings,
                status == "unverified" and not references,
                "warning",
                f"{prefix}.evidence_refs",
                "Link available evidence even when the hypothesis is unverified.",
            )

    _add(
        findings,
        not package.engineering_question.endswith("?"),
        "warning",
        "engineering_question",
        "State the engineering request as a focused question.",
    )

    for field in ("current_impact", "actions_taken", "next_update_at"):
        _add(
            findings,
            not isinstance(package.customer_update.get(field), str)
            or not package.customer_update[field].strip(),
            "error",
            f"customer_update.{field}",
            f"Customer update requires {field}.",
        )
    if package.customer_update.get("next_update_at"):
        _add(
            findings,
            not _valid_timestamp(package.customer_update["next_update_at"]),
            "error",
            "customer_update.next_update_at",
            "Next update must use an ISO 8601 timestamp with a time zone.",
        )

    errors = sum(finding.level == "error" for finding in findings)
    warnings = sum(finding.level == "warning" for finding in findings)
    score = max(0, 100 - (errors * 15) - (warnings * 5))
    return CheckResult(
        incident_id=package.incident_id,
        score=score,
        ready=errors == 0 and score >= 80,
        errors=errors,
        warnings=warnings,
        findings=tuple(findings),
    )


def load_package(path: Path) -> EscalationPackage:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"could not read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"{path} contains invalid JSON at line {error.lineno}, column {error.colno}"
        ) from error
    return EscalationPackage.from_mapping(raw)


def render_text(result: CheckResult) -> str:
    lines = [
        f"Incident: {result.incident_id}",
        f"Score:    {result.score}/100",
        f"Ready:    {'yes' if result.ready else 'no'}",
        f"Findings: {result.errors} error(s), {result.warnings} warning(s)",
    ]
    if result.findings:
        lines.append("")
        lines.extend(
            f"[{finding.level.upper()}] {finding.field}: {finding.message}"
            for finding in result.findings
        )
    else:
        lines.extend(["", "No readiness issues found."])
    return "\n".join(lines)


def render_json(result: CheckResult) -> str:
    return json.dumps(asdict(result), indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check whether a synthetic escalation is ready for engineering."
    )
    parser.add_argument("input", type=Path, help="path to an escalation JSON file")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument(
        "--minimum-score",
        type=int,
        default=80,
        help="required score for a zero exit status (default: 80)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 0 <= args.minimum_score <= 100:
        print("escalation-check: minimum score must be between 0 and 100", file=sys.stderr)
        return 1

    try:
        result = check_package(load_package(args.input))
    except ValueError as error:
        print(f"escalation-check: {error}", file=sys.stderr)
        return 1

    print(render_json(result) if args.json else render_text(result))
    if result.errors or result.score < args.minimum_score:
        return 2
    return 0
