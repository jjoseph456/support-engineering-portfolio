# Incident Response Playbook

This playbook is designed for a technical support engineer coordinating with
customers, support, product, and engineering during a production issue.

## 1. Establish Impact

Record facts before proposing causes:

- Which customer workflows are affected?
- Is the impact complete failure, degradation, delay, or incorrect output?
- When did it start, and is it continuous or intermittent?
- Which regions, versions, integrations, or environments are affected?
- Is there a safe workaround?

Write the initial impact statement in one sentence:

> Since 14:05 UTC, agent execution requests in the US test region have shown a
> 34% error rate. Existing sessions remain available.

## 2. Build a Minimal Reproduction

Reduce the report to the smallest repeatable request or workflow. Preserve:

- Request and correlation IDs
- Sanitized configuration
- Timestamps with time zone
- Client and server versions
- Expected and actual behavior
- Relevant logs, traces, metrics, and response headers

Never move customer secrets or production data into a test environment.

## 3. Separate Evidence from Hypothesis

Use explicit language:

| Type | Example |
|---|---|
| Observation | Five requests returned HTTP 503 between 14:05 and 14:08 UTC. |
| Hypothesis | The errors may originate from an upstream dependency. |
| Confirmation | Provider telemetry confirmed elevated 5xx responses. |

This prevents an early theory from becoming an accidental customer-facing root
cause.

## 4. Escalate with a Complete Package

An engineering escalation should include:

- Concise impact and severity
- Reproduction steps and frequency
- First and last known occurrence
- Sanitized logs and correlation IDs
- Changes already ruled out
- Workaround status
- Specific question engineering needs to answer

## 5. Communicate on a Predictable Cadence

Every update should contain:

1. Current impact
2. What changed since the last update
3. What is being investigated
4. Workaround or mitigation status
5. Time of the next update

If there is no new technical finding, say so plainly and describe the active
investigation. Do not let the absence of a root cause become an absence of
communication.

## 6. Close the Loop

Before closure:

- Confirm recovery through telemetry and customer validation.
- Document the root cause only after it is verified.
- Record detection and communication gaps.
- Convert repeated diagnostics into tooling or a runbook.
- Track preventive actions with owners and dates.
