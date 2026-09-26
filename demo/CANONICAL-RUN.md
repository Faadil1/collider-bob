# Canonical Run

## Canonical LOCAL comparative evidence

Status: **PASS**

Date: 2026-09-26

### Evidence binding

Comparative evidence commit:

`49d59a6c48aae5dce5ebad9f36909b5c71e77bb6`

Baseline:

- run: `evidence/runs/baseline-001/`
- runtime input:
  `45fd342c6322178ee505456d2b95d301744d198f`
- evidence commit:
  `27676adbb0cd2df6702d3cf6cb07f26a6d08d779`

COLLIDER:

- run: `evidence/runs/local-resolved-004/`
- runtime input:
  `289415b06f69a9ea346606c07c4cb388f127c1bf`

Comparative receipt:

- `evidence/comparisons/baseline-001-vs-local-resolved-004.json`
- `evidence/comparisons/baseline-001-vs-local-resolved-004.md`

### Observed baseline

The three workstreams begin from byte-identical implementation artifacts
relative to the COLLIDER run.

Observed:

- 30 local workstream tests pass
- 3/3 workstreams are locally green
- 0 contradictions are surfaced before integration
- integration discovers 2 incompatible interfaces
- result: `INTEGRATION_BLOCKED`
- no root-cause classification is performed

Conflicts:

1. `customer_identity`
   - API: `email`
   - Ledger: `account_id`

2. money field
   - API: `refund_amount`
   - Ledger: `credit_amount`

### Observed COLLIDER classification

`customer_identity`

- classification: `SPEC_GAP`
- epistemic state: `UNKNOWN`
- source does not decide
- automatic resolution: false
- human clarification required: 1

`field_name`

- classification: `AGENT_DRIFT`
- explicit source value: `refund_amount`
- drifted workstream: Ledger
- human clarification required: false

`money_representation`

- all workstreams agree on integer cents
- classification subtype: `SHARED_INFERRED`
- consensus does not upgrade the claim to fact

### Observed repairs

Source-grounded AGENT_DRIFT repair:

`Ledger: credit_amount -> refund_amount`

Repair source:

`AGENT_DRIFT_EVIDENCE`

Human-resolved SPEC_GAP repair:

`API: email -> account_id`

Repair source:

`CANON_PATCH`

Notifications is unchanged.

### Observed result

After the two targeted repairs:

- executable integration conflicts: 0
- result: `INTEGRATION_READY`
- tests after repair: pass
- transient source state restored: true
- transient Python module state restored: verified
- restored baseline again exposes the original 2 conflicts

### Truth boundary

This is **LOCAL / PRESEEDED evidence**.

Observed:

- COLLIDER reconciliation
- classifications
- abstention semantics
- source-grounded AGENT_DRIFT repair
- human-decision-driven SPEC_GAP repair
- impact routing
- cryptographic before/after/restored evidence
- baseline-vs-COLLIDER executable integration result

Not established:

- LIVE_BOB-generated interpretations
- live interactive human clarification
- wall-clock productivity improvement
- percentage productivity improvement
- production-scale generalization

Bob-native claims remain bounded by actual Bob Task Session Summary evidence.

### Preserved failures

The evidence history intentionally preserves:

- overwritten early local-run incident
- baseline integrity-test false positive
- transient repair / Python module-cache contamination

These failures were not erased from the project history.

Real failure > fake success.
