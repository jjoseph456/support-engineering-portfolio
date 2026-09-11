# Sample Postmortem: Agent Runtime Memory Exhaustion

**Status:** Fictional example
**Severity:** SEV-1
**Date:** September 10, 2026
**Duration:** 42 minutes

## Summary

A synthetic agent-runtime service experienced elevated failures after a
workload change increased per-request memory consumption. Containers exceeded
their configured limits and were terminated by the runtime. Requests routed to
restarting containers returned HTTP 503 responses.

## Impact

- 62% of synthetic agent-execution requests failed at peak.
- Existing stored sessions were not lost.
- The control plane and trace-ingestion services remained available.

## Timeline

| Time (UTC) | Event |
|---|---|
| 14:05 | Error-rate alert crossed the critical threshold. |
| 14:08 | Support confirmed repeated HTTP 503 responses and container restarts. |
| 14:13 | Engineering correlated restarts with out-of-memory termination events. |
| 14:19 | Recent workload configuration change identified. |
| 14:27 | Configuration rolled back and additional capacity added. |
| 14:35 | Error rate returned to baseline. |
| 14:47 | Recovery confirmed through synthetic requests and telemetry. |

## Root Cause

The fictional workload configuration increased concurrent in-memory processing
without a corresponding adjustment to container memory limits or concurrency
controls. The runtime terminated containers that exceeded their limits.

## Contributing Factors

- Load testing did not include the new maximum concurrency.
- The alert identified failures but did not identify container restarts.
- The deployment checklist did not require a memory-impact review.

## What Went Well

- Support supplied timestamps, correlation IDs, and a minimal reproduction in
  the initial escalation.
- Engineering quickly matched request failures with container termination
  events.
- Rollback instructions were current and tested.
- Customer updates were delivered on the announced cadence.

## What Could Be Improved

- The first alert should have included restart and memory-pressure context.
- Capacity assumptions should have been tested before deployment.
- The runbook needed a direct check for termination reason.

## Corrective Actions

| Action | Owner | Due |
|---|---|---|
| Add container restart and memory-pressure signals to the alert. | SRE | 2 weeks |
| Add maximum-concurrency coverage to load tests. | Engineering | 3 weeks |
| Add termination-reason checks to the support runbook. | Support | 1 week |
| Require resource-impact review for workload configuration changes. | Product Engineering | 3 weeks |
