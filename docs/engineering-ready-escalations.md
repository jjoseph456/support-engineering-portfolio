# From Symptom to Engineering-Ready Escalation

Technical support creates the most value when it reduces uncertainty before an
issue reaches engineering.

An escalation should not be a forwarded customer message with a priority label.
It should be a compact investigation package: impact, reproduction, evidence,
working hypotheses, workaround status, and a specific question that engineering
can answer.

The examples in this article are synthetic. They do not represent a real
customer, employer system, or production incident.

## The Cost of an Incomplete Escalation

Consider this escalation:

> The API is broken for an important customer. Please investigate urgently.

It communicates emotion and priority but gives engineering no reliable starting
point. The first engineering response will be a request for timestamps,
environment details, request identifiers, logs, and reproduction steps. Support
and engineering then repeat the same discovery work while the customer waits.

A useful escalation changes the first engineering question from "What
happened?" to "Does this evidence indicate a product defect, and which component
owns it?"

## The Five-Layer Escalation Model

### 1. Impact

State what users cannot do, how broadly they are affected, when the behavior
started, and whether a workaround exists.

Weak:

> Requests are failing.

Stronger:

> Since 01:05 UTC, approximately 34% of synthetic agent executions in the US
> test region return HTTP 503 at high concurrency. Existing sessions remain
> available, and reducing concurrency prevents the failure.

Impact should describe customer-visible behavior. It should not guess at the
cause.

### 2. Reproduction

The smallest reliable reproduction is more valuable than a large collection of
unfiltered logs. A good reproduction identifies:

- The exact operation
- Required configuration or preconditions
- Expected and actual behavior
- Reproduction frequency
- Whether the same test succeeds in another environment

If the issue cannot be reproduced, document the attempts and differences rather
than writing "not reproducible" without context.

### 3. Evidence

Evidence must be attributable and time-bound. Useful examples include:

- Request and correlation IDs
- Sanitized request and response data
- Log events, metrics, and traces
- Deployment history
- Container termination reasons
- Version and environment information

Each observation should include a timestamp and source. A raw log archive is not
an analysis; identify the lines and events that matter.

### 4. Hypotheses

Observations and hypotheses are different data types.

Observation:

> Three failed requests correlate with container restarts.

Hypothesis:

> The workload may exceed the container memory limit.

Confirmed root cause:

> Runtime telemetry and a controlled load test confirmed that the new
> concurrency setting caused memory use to exceed the configured limit.

Label hypotheses as `unverified`, `confirmed`, or `ruled_out`. A confirmed
hypothesis must cite supporting evidence. This prevents a plausible early theory
from becoming an accidental customer-facing root cause.

### 5. Engineering Question

End with a bounded question. Examples:

- Can the service owner confirm whether this status code originates from the
  gateway or the upstream provider?
- Is the observed retry behavior expected for this API version?
- Does the deployment change explain the new memory profile?
- Is there additional telemetry support should collect?

"Please investigate" is not a question and does not define what support needs
from engineering.

## Customer Communication Is Part of the Package

Every update should state:

1. Current impact
2. Actions completed
3. What is being investigated
4. Workaround or mitigation status
5. Time of the next update

An update can be useful even when there is no confirmed root cause:

> We reproduced the failure and correlated it with service restarts. Engineering
> is reviewing whether a recent configuration change altered resource usage.
> Reducing concurrency remains an effective temporary workaround. The next
> update will be provided by 01:45 UTC.

## Automating the Quality Gate

The `escalation-check` project in this repository turns these expectations into
a repeatable validation step. It checks that:

- Required fields are present
- Timestamps use an unambiguous format
- Reproduction steps are actionable
- Evidence includes identifiers, sources, observations, and timestamps
- Hypotheses reference known evidence
- Confirmed hypotheses are not evidence-free
- The engineering request is a focused question
- The customer update has impact, actions, and a next-update time

The tool does not determine whether a diagnosis is correct. It checks whether
the investigation package is structured well enough for another team to act on
it.

## Closing the Loop

The final step is to convert the incident into leverage:

- Add a reproducer for a recurring failure
- Turn the diagnostic path into a runbook
- Improve alert context
- Record a safe workaround
- Update customer documentation
- Track the corrective action to completion

The goal is not merely to close one case. It is to make the next occurrence
faster to identify, easier to communicate, and less likely to require an
escalation.
