# Baseline Comparison Scope

Date: 2026-09-26

## Purpose

Define the capabilities that may be compared between the baseline workflow and
COLLIDER using observed evidence only.

## Canonical runtime input

COLLIDER runtime-input commit:

`f581c332782bc4945110b8ea1fdcb155dc00b502`

Canonical local evidence commit:

`3719d1bc1f37558c61ce6458cfd09472f076c515`

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
- preserving `money_representation` as `SHARED_INFERRED`
- filtering the internal-response-body negative control as `OUT_OF_SCOPE`

## Not yet eligible for comparative claims

The current runtime does NOT yet have executable observed evidence that it:

- automatically repairs Ledger `credit_amount` -> `refund_amount`
- runs live Bob parallel subagents for the canonical comparison
- reduces wall-clock time in a live agent execution
- achieves any percentage improvement over baseline

Therefore those claims must not be included as observed comparative wins.

## Comparison rule

The baseline comparison must use the same fixture and must measure only directly
observed behavior.

No predicted values from `BASELINE-CONTRACT.md` may be copied into observed fields.

Real failure > fake success.
