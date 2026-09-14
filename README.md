# Support Engineering Portfolio

[![CI](https://github.com/jjoseph456/support-engineering-portfolio/actions/workflows/test.yml/badge.svg)](https://github.com/jjoseph456/support-engineering-portfolio/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Practical examples of how I investigate production issues, communicate during
incidents, and turn recurring support problems into reusable tooling and
documentation.

I am an Enterprise Support Engineer at GitHub, where I work with enterprise
customers and collaborate daily with engineering and product teams on complex
technical issues involving CI/CD, infrastructure, security, and developer
workflows.

> This is a personal portfolio. It is not an official GitHub project and does
> not contain GitHub source code, customer information, internal documentation,
> ticket data, or confidential operational details. All examples and data are
> synthetic.

## Start Here

| If you are evaluating... | Review |
| --- | --- |
| Python and support automation | [Incident Triage CLI](#1-incident-triage-cli) and [Engineering Escalation Checker](#2-engineering-escalation-checker) |
| Incident ownership and communication | [Incident response playbook](docs/incident-response-playbook.md) and [sample postmortem](docs/sample-postmortem.md) |
| Applied support-engineering judgment | [Synthetic case-study patterns](docs/synthetic-case-study-patterns.md) |
| Support-system design | [Support operations architecture](docs/support-operations-architecture.md) |
| GitHub platform expertise | [Actions](best-practices/github-actions-secure-reliable-workflows.md), [GHES](best-practices/ghes-operational-readiness.md), and [Advanced Security](best-practices/github-advanced-security-rollout.md) guidance |
| Standalone public projects | [Workflow Auditor](#github-actions-workflow-auditor) and [GHES Bundle Triage](#ghes-support-bundle-triage) |
| Project breadth | [Capabilities demonstrated](#capabilities-demonstrated) |

## Quick Start

Requires Python 3.10 or later and has no runtime dependencies.

```bash
git clone https://github.com/jjoseph456/support-engineering-portfolio.git
cd support-engineering-portfolio
python -m pip install -e .
support-triage examples/incidents.json
escalation-check examples/escalation.json
```

## Featured Projects

### 1. Incident Triage CLI

`support-triage` is a dependency-free Python command-line tool that turns a
small batch of synthetic service signals into a prioritized investigation
queue.

It demonstrates a support-engineering workflow:

1. Validate the incoming diagnostic data.
2. Classify severity consistently.
3. Identify a likely failure category without presenting it as a confirmed
   root cause.
4. Recommend the next diagnostic action.
5. Produce human-readable or machine-readable output.
6. Return a meaningful exit code for CI and automation.

### Run it

```bash
python -m support_triage examples/incidents.json
```

Machine-readable output:

```bash
python -m support_triage examples/incidents.json --json
```

Fail an automation step when a high- or critical-severity incident is present:

```bash
python -m support_triage examples/incidents.json --fail-on high
```

### Example output

```text
SEVERITY  INCIDENT       SERVICE          LIKELY CATEGORY       NEXT ACTION
CRITICAL  INC-1042       agent-runtime    resource exhaustion   Inspect container termination reason and memory limits.
HIGH      INC-1041       evaluation-api   upstream dependency   Compare upstream provider errors and request correlation IDs.
MEDIUM    INC-1040       trace-ingest     rate limiting         Inspect rate-limit headers and client backoff behavior.
LOW       INC-1039       control-plane    no clear fault        Continue monitoring and compare against the service baseline.
```

### 2. Engineering Escalation Checker

`escalation-check` reviews a synthetic escalation package before it reaches an
engineering team. It verifies that the package includes a clear impact
statement, reproduction steps, timestamped evidence, explicitly labeled
hypotheses, a focused engineering question, workaround status, and a complete
customer update.

```bash
python -m escalation_check examples/escalation.json
```

Machine-readable output and an automation gate:

```bash
python -m escalation_check examples/escalation.json --json
python -m escalation_check examples/escalation.json --minimum-score 90
```

The tool treats observations, hypotheses, and confirmed root cause as different
types of information. That distinction reduces premature conclusions and gives
engineering a cleaner starting point.

## Documentation Samples

- [`docs/incident-response-playbook.md`](docs/incident-response-playbook.md) -
  a concise process for triage, escalation, communication, and closure.
- [`docs/sample-postmortem.md`](docs/sample-postmortem.md) - a blameless
  postmortem built from a fictional container-memory incident.
- [`docs/engineering-ready-escalations.md`](docs/engineering-ready-escalations.md) -
  a technical article on converting an ambiguous report into an actionable
  engineering escalation.
- [`docs/synthetic-case-study-patterns.md`](docs/synthetic-case-study-patterns.md) -
  fictional, privacy-safe examples of evidence-led diagnosis, escalation
  ownership, and durable operational improvements.
- [`docs/support-operations-architecture.md`](docs/support-operations-architecture.md) -
  a visual map of how the public tools support intake, investigation,
  escalation, customer continuity, and knowledge maintenance.

## Best-Practice Articles

- [Secure and Reliable GitHub Actions Workflows](best-practices/github-actions-secure-reliable-workflows.md)
- [GitHub Enterprise Server Operational Readiness](best-practices/ghes-operational-readiness.md)
- [GitHub Advanced Security Rollout and Operations](best-practices/github-advanced-security-rollout.md)

## Engineering Practices Demonstrated

- Python data modeling, validation, CLI design, and JSON serialization
- Unit tests covering severity, diagnostic categorization, validation, and
  command exit behavior
- GitHub Actions continuous integration
- Clear separation between observed evidence, working hypotheses, and confirmed
  root cause
- Actionable incident communication and escalation criteria
- Reusable documentation designed to reduce repeat support effort

## Capabilities Demonstrated

These projects show how I approach common support-engineering problems:

| Area | Example output | Intended outcome |
| --- | --- | --- |
| Incident and escalation process review | Triage rules, escalation-quality checks, and runbooks | Faster handoffs and fewer incomplete engineering escalations |
| GitHub Actions workflow health check | Security and reliability findings with prioritized remediation | Reduced workflow risk and more predictable CI/CD |
| GHES operational-readiness review | Readiness checklist and operational recommendations | Clearer upgrade, backup, monitoring, and incident preparation |
| Support automation prototype | Tested Python CLI with machine-readable output and exit codes | Repeatable triage and less manual support work |
| Technical documentation sprint | Troubleshooting guides, postmortems, and knowledge articles | Better case deflection and reusable operational knowledge |

The repository demonstrates the method and output quality without using
employer, customer, or support-case material.

## Standalone Public Projects

### GitHub Actions Workflow Auditor

[`github-actions-workflow-auditor`](https://github.com/jjoseph456/github-actions-workflow-auditor)
is a Python CLI for repeatable workflow security and reliability reviews.

It provides:

- Ten focused checks covering permissions, action pinning, shell interpolation,
  privileged pull-request patterns, timeouts, concurrency, OIDC boundaries, and
  reusable-workflow secret handling
- Human-readable and JSON reports
- Configurable CI failure thresholds
- Secure and intentionally insecure synthetic workflow examples
- Eleven unit tests, pinned CI dependencies, and an MIT license

### GHES Support Bundle Triage

[`gh-bundle`](https://github.com/jjoseph456/gh-bundle) is a read-only `gh` CLI
extension for an initial review of GitHub Enterprise Server support bundles.

It demonstrates:

- Selective extraction of diagnostic files instead of expanding an entire
  multi-gigabyte archive
- Topology-aware handling of single-node and multi-node bundles
- Disk, memory, out-of-memory, service-health, and connectivity signals
- Defensive handling of missing or malformed diagnostic files
- Human-readable and JSON output with automation-friendly exit codes

The tool is designed as an initial screen that points to source evidence, not
as a substitute for complete diagnosis.

## Development

Install the package in editable mode and run the test suite:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Repository Structure

```text
.
|-- .github/workflows/test.yml
|-- pyproject.toml
|-- SECURITY.md
|-- best-practices/
|   |-- README.md
|   |-- ghes-operational-readiness.md
|   |-- github-actions-secure-reliable-workflows.md
|   `-- github-advanced-security-rollout.md
|-- docs/
|   |-- engineering-ready-escalations.md
|   |-- incident-response-playbook.md
|   |-- sample-postmortem.md
|   |-- support-operations-architecture.md
|   `-- synthetic-case-study-patterns.md
|-- escalation_check/
|   |-- __init__.py
|   |-- __main__.py
|   `-- checker.py
|-- examples/
|   |-- escalation.json
|   `-- incidents.json
|-- support_triage/
|   |-- __init__.py
|   |-- __main__.py
|   `-- triage.py
`-- tests/
    |-- test_escalation_check.py
    `-- test_triage.py
```

## Contact

- LinkedIn: [Joseph P. Joseph](https://www.linkedin.com/in/josephpjoseph/)
