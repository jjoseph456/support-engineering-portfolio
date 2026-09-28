# Closure Is Not Customer Recovery

An engineering escalation can close for many reasons: a fix shipped, a
product decision was made, the customer confirmed recovery, or nobody replied
for seven days. Only some of those mean the customer is working again. When a
reporting system counts all of them as "resolved," queue health looks better
than customer health.

This note describes the gap and a small set of controls that close it. All
numbers below come from a **synthetic** 200-case example built for this
portfolio. They illustrate the method, not any real organization.

## The Problem

In the synthetic cohort:

| Closure path | Cases | What it actually proves |
| --- | ---: | --- |
| Customer confirmed recovery | 90 | Recovery |
| Engineering decision (fix, limitation, or product decision) | 70 | A technical disposition, not customer recovery |
| Inactivity auto-close after a customer-wait state | 40 | Only that no reply arrived |

If all 200 are reported as resolved, 20% of the "resolution rate" rests on
silence. Silence has ordinary explanations that are not recovery: the customer
is waiting for a maintenance window, the failure is intermittent, a workaround
is in place but untested, or the person who filed the case moved on.

The same cohort shows two more weak signals:

- 30 cases closed without ever having an assigned engineer.
- 15 cases were reopened, and 6 of those had no new technical decision
  within one business day of the reopen.

## Separate the States

A single `closed` flag carries too much meaning. Record these as separate
facts:

1. Acknowledged
2. Engineering ownership accepted
3. Technical disposition recorded
4. Mitigation deployed
5. Affected customers exposed to the mitigation
6. Observation window completed
7. Customer outcome: verified, workaround accepted, informed limitation, or
   **unconfirmed**

An inactivity close is still valid queue hygiene. It should simply record the
customer outcome as `unconfirmed` rather than borrowing the label of a
verified recovery.

## Controls That Make This Checkable

The [Escalation Lifecycle Guard](https://github.com/jjoseph456/escalation-lifecycle-guard)
implements these as rules over structured case data:

| Rule | Catches |
| --- | --- |
| `SILENCE_COUNTED_AS_RECOVERY` | An inactivity auto-close recorded as a verified or accepted outcome |
| `UNCLEAR_CLOSE_OUTCOME` | A close with no recorded customer outcome |
| `CLOSED_WITHOUT_ASSIGNMENT` | A close that never had an accountable engineer |
| `REOPEN_WITHOUT_REDISPOSITION` | A reopen with no new technical decision after one business day |
| `MISSED_ENGINEERING_RESPONSE` | No engineering response within the severity's business-day target |

## Measure the Right Things

Report these separately rather than as one resolution rate:

- time to named engineering owner
- time to technical disposition
- mitigation deployed versus customer outcome verified
- share of closes with an `unconfirmed` outcome
- unresolved-after-reopen and time to redisposition

Do not set a target to reduce reopens. A reopen is a correction mechanism. The
useful question is how quickly a reopened case gets a fresh owner and
decision.

## Takeaway

A closed queue item is an operational fact. A recovered customer is a
different fact that needs its own evidence. Keeping them apart costs one extra
field and makes every resolution metric honest.
