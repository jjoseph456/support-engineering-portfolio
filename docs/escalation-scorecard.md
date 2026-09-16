# Escalation Effectiveness Scorecard

This scorecard measures the quality of a support escalation without treating
engineering response time, closure count, or ticket volume as an individual
performance score. Those outcomes also depend on incident load, severity,
product ownership, and the availability of a reproducible failure.

## Use

Review a rolling 90-day sample. Segment results by product area and severity.
Use anonymized, manager-approved cohort data for comparisons rather than raw
individual rankings.

| Measure | What to record | Why it matters |
| --- | --- | --- |
| Evidence-complete at filing | Timestamp, immutable identifier, expected result, observed result, customer impact, and one engineering decision requested | Reduces clarification loops and makes the case actionable |
| Correct routing rate | Whether the first owner was able to answer the requested decision | Measures investigation and routing quality |
| Clarification loops | Number of follow-ups needed for basic context already available at filing | Highlights missing scope, artifacts, or an unclear ask |
| First engineering response | Time to the first independent, non-automated response, grouped by owner and severity | Identifies queue risk without treating it as a personal score |
| Customer update cadence | Days between substantive customer-visible updates while the issue remains unresolved | Prevents customers from having to chase status |
| Outcome quality | Confirmed cause, supported mitigation, expected behavior with evidence, or a documented evidence gap | Rewards accurate outcomes, not premature closure |
| Reopen rate | Tickets reopened after a proposed resolution | Tests whether the customer's actual need was addressed |
| Reusable output | A privacy-safe tool, reproduction, process improvement, or documentation result | Captures durable value beyond the individual ticket |

## Filing Checklist

An escalation should make the requested decision visible before its detailed
evidence:

```text
Decision requested:
Is this expected behavior, a known defect, or a different owning area?

Customer impact:
<One concrete business or operational consequence.>

Evidence:
- <UTC timestamp, immutable ID, and observed behavior>
- <Expected behavior>
- <Comparison or control that bounds the hypothesis>

Already ruled out:
- <Only customer-side explanations actually tested>

Exact engineering ask:
Please confirm <one bounded technical decision>.
If this is not the owning area, please identify the correct owner.

Customer state:
<Blocked, monitoring, or using a supported mitigation.>
Next customer update due: <date or event>.
```

## Operating Rhythm

1. At filing, record the evidence checklist and the one requested decision.
2. On business day three without a material answer, post a concise
   re-engagement that names the pending decision and the next customer update.
3. Update the customer on the same cadence with confirmed facts, current
   owner, and the next verification event.
4. At close, record the evidence-backed outcome and any reusable learning.

## Guardrails

- Do not use ticket volume or close rate as a quality proxy.
- Do not compare individual engineers without normalization and approval.
- Do not treat a customer going silent as proof of recovery.
- Do not claim a platform cause until an appropriate artifact establishes it.
- Keep customer, employer, and internal operational information out of public
  portfolio material.
