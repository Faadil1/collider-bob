# Baseline vs COLLIDER — Canonical Local Comparative Receipt

Date: 2026-09-26

## Evidence status

**OBSERVED LOCAL evidence**

This receipt does not claim LIVE_BOB execution, wall-clock savings,
percentage productivity improvement, or production-scale generalization.

## Fairness gate

The starting executable workstream artifacts were byte-identical:

- API: **True**
- Ledger: **True**
- Notifications: **True**

Baseline runtime input:

`45fd342c6322178ee505456d2b95d301744d198f`

COLLIDER runtime input:

`289415b06f69a9ea346606c07c4cb388f127c1bf`

The repository commits differ because COLLIDER's runtime and verification
harness evolved. The three application workstream artifacts compared at the
start were byte-identical.

## Baseline — observed

- Local workstream tests passed: **30**
- Workstream suites green: **3/3**
- Contradictions surfaced before integration: **0**
- Integration conflicts discovered: **2**
- Integration status: **INTEGRATION_BLOCKED**
- Root-cause classification: **none**

Observed mismatches:

1. `customer_identity`: `email != account_id`
2. money field: `refund_amount != credit_amount`

## COLLIDER — observed

COLLIDER separated the two mismatches by evidence:

### Missing specification decision

`customer_identity`

- classification: **SPEC_GAP**
- epistemic state: **UNKNOWN**
- automatic resolution: **false**
- human clarifications required: **1**
- canonical decision used in this LOCAL run:
  `account_id` via a **PRESEEDED human decision**

Executable repair:

`API: email → account_id`

Repair source:

`CANON_PATCH`

### Agent deviation from explicit source

`field_name`

- classification: **AGENT_DRIFT**
- authoritative source value: `refund_amount`
- human clarification required: **no**

Executable repair:

`Ledger: credit_amount → refund_amount`

Repair source:

`AGENT_DRIFT_EVIDENCE`

### Unaffected work

Notifications was not changed by either targeted repair.

## Executable outcome

Baseline:

**2 conflicts → INTEGRATION_BLOCKED**

COLLIDER after targeted repair:

**0 conflicts → INTEGRATION_READY**

The repaired API and Ledger states were captured cryptographically and the
repository baseline was then restored successfully.

## What this evidence supports

On this canonical fixture, independently green workstreams can still contain
incompatible cross-boundary assumptions.

COLLIDER demonstrated that it can distinguish an undecided specification
question from an agent deviation against explicit source evidence, preserve
UNKNOWN where evidence is insufficient, request one human decision, apply
targeted executable repairs, and reach a conflict-free integration probe.

## What this evidence does not support

This receipt does not establish:

- LIVE_BOB-generated interpretations
- live interactive human clarification
- wall-clock time savings
- percentage productivity improvement
- fewer total repair cycles than a completely repaired alternative baseline
- production-scale generalization
