# Support Engineering Portfolio

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

## Featured Project: Incident Triage CLI

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

## Documentation Samples

- [`docs/incident-response-playbook.md`](docs/incident-response-playbook.md) -
  a concise process for triage, escalation, communication, and closure.
- [`docs/sample-postmortem.md`](docs/sample-postmortem.md) - a blameless
  postmortem built from a fictional container-memory incident.

## Engineering Practices Demonstrated

- Python data modeling, validation, CLI design, and JSON serialization
- Unit tests covering severity, diagnostic categorization, validation, and
  command exit behavior
- GitHub Actions continuous integration
- Clear separation between observed evidence, working hypotheses, and confirmed
  root cause
- Actionable incident communication and escalation criteria
- Reusable documentation designed to reduce repeat support effort

## Test

```bash
python -m unittest discover -s tests -v
```

## Repository Structure

```text
.
|-- .github/workflows/test.yml
|-- docs/
|   |-- incident-response-playbook.md
|   `-- sample-postmortem.md
|-- examples/incidents.json
|-- support_triage/
|   |-- __init__.py
|   |-- __main__.py
|   `-- triage.py
`-- tests/test_triage.py
```

## Contact

- GitHub: [jjoseph456](https://github.com/jjoseph456)
- LinkedIn: [Joseph P. Joseph](https://www.linkedin.com/in/josephpjoseph/)
