# Baseline Comparison Scope

Date: 2026-09-26

## Purpose

Define the capabilities that may be compared between the baseline workflow and
COLLIDER using observed evidence only.

## Canonical runtime input

Current comparative COLLIDER runtime-input commit:

`289415b06f69a9ea346606c07c4cb388f127c1bf`

Canonical baseline evidence commit:

`27676adbb0cd2df6702d3cf6cb07f26a6d08d779`

Canonical comparative run:

`evidence/runs/local-resolved-004/`

## Implemented and eligible for comparison

The current COLLIDER runtime has observed evidence for:

- detecting the `customer_identity` disagreement
- classifying it as `SPEC_GAP`
- preserving `UNKNOWN`
- refusing automatic resolution
- requiring one human decision
- emitting a canon patch after that decision
- routing impact for the resolved decision
- repairing the API identity implementation
- preserving Ledger when already canonical
- excluding Notifications from the identity repair
- identifying `field_name` as `AGENT_DRIFT`
- automatically repairing Ledger `credit_amount` -> `refund_amount` from explicit source evidence
- producing an executable post-repair integration receipt with zero conflicts
- restoring all transiently repaired workstream source and Python module state
- preserving `money_representation` as `SHARED_INFERRED`
- filtering the internal-response-body negative control as `OUT_OF_SCOPE`

## Not yet eligible for comparative claims

The current runtime does NOT yet have executable observed evidence that it:

- runs live Bob parallel subagents for the canonical comparison
- reduces wall-clock time in a live agent execution
- achieves any percentage improvement over baseline

Therefore those claims must not be included as observed comparative wins.

## Comparison rule

The baseline comparison must use the same fixture and must measure only directly
observed behavior.

No predicted values from `BASELINE-CONTRACT.md` may be copied into observed fields.

Real failure > fake success.
