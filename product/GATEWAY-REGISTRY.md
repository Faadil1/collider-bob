# Conditional Gateway Registry

Every registered gateway receives an explicit status. Nothing is silently forgotten.
`N/A` means not applicable now, not forgotten forever. Re-evaluate at every material concept, architecture, runtime, or submission change.

| Gateway / Gate | Status | Reason / promotion condition |
|---|---|---|
| QUALIFY→DECIDE→DESIGN→DELIVER→AUDIT→EXPAND | ACTIVE | Product/build audit is complete; remaining work is submission packaging and final snapshot. |
| RUBRIC→PAIN→PROBLEM→DIFFERENTIATOR→EXECUTION→EVIDENCE→STORY→DEMO→Q&A | ACTIVE | Judge story and demo script are locked; final media/Q&A packaging remains. |
| Real Negative Event Gate | PROVEN | product/PROBLEM-EVIDENCE.md — Mars Climate Orbiter anchors the failure class only; no prevention claim. |
| Competitive Novelty / Kill Gate | PROVISIONAL_PASS | Re-checked 2026-09-27 (product/SEMANTIC-CI-ESCALATION.md §7): no full kill-condition loop observed; lead with the DECISION_REQUIRED third verdict. |
| Creative Depth & Product Ambition | PROVEN | product/SEMANTIC-CI-ESCALATION.md — second pass against the working product; North Star preserved. |
| Distinctiveness Escalation | PROVEN | product/SEMANTIC-CI-ESCALATION.md — hard-coded memory, block-path bias and invisible assumptions were found and fixed. |
| Concept Compression & Validation | PROVEN | product/CONCEPT-COMPRESSION-VALIDATION.md — internal checks pass; explicit outsider-test waiver recorded, external comprehension remains unmeasured. |
| Real-User / Outsider Break Test | PROVISIONAL_PASS | Not executed; explicitly waived in evidence/validation/OUTSIDER-BREAK-TEST-WAIVER-2026-09-27.md. Never narrate this as a completed user test. |
| Technical Reality Check | PROVEN | product/TECHNICAL-REALITY-CHECK.md. |
| Demo-First Architecture | PROVEN | product/DEMO-FIRST-ARCHITECTURE.md. |
| Fixture Design | PROVEN | fixtures/failed-payment/. |
| Evidence Schema | PROVEN | evidence/EVIDENCE-SCHEMA.md. |
| Truth Boundary | PROVEN | product/TRUTH-BOUNDARY.md; shared assumptions remain INFERRED, not fact. |
| Negative Path | PROVEN | KEEP UNKNOWN + MERGE_ALLOWED false-positive control. |
| Evidence Integrity | PROVEN | Canonical evidence hashes are pinned; tests no longer write into committed evidence. |
| Bob-Native Integration | ACTIVE | Bob was load-bearing in development; canonical interpretations remain PRESEEDED, not LIVE_BOB. |
| Runtime / Commit Binding | PROVEN | evidence/runtime/RUNTIME-COMMIT-BINDING-2026-09-27.md. |
| Public Runtime / Live Proof | PROVEN | Three-verdict guard, session isolation, real-iPhone smoke and runtime binding are proven. |
| Deterministic Demo | PROVEN | Public desktop + real-device runs reproduce the intended demo states and restoration. |
| Judge Performance Assurance | PROVEN | product/JUDGE-PERFORMANCE-ASSURANCE.md — demo story, rubric fit, confusion checks and timing passed for Demo Lock. |
| Pre-Launch / Ship Assurance | PROVEN | product/PRE-LAUNCH-SHIP-ASSURANCE.md + runtime/header receipts. |
| Submission Integrity | PENDING | Submission copy is refreshed; final video/slides/cover/Bob Task Summary still need package-level verification. |
| Final Snapshot / CURRENT / HANDOVER | ACTIVE | Final snapshot after media/package completion. |
| x402 | N/A | No payment rail in the product. |
| Nanopayments | N/A | No payment rail in the product. |
| Wallets | N/A | No wallet or value movement. |
| Smart Contracts | N/A | No on-chain execution. |
| App Kit / sponsor gateway | N/A | No applicable sponsor SDK in the architecture. |
| LIVE_GATEWAY promotion | N/A | No external settlement gateway. |

## Canonical promotion order

`CREATIVE DEPTH → DISTINCTIVENESS → COMPRESSION/REAL-USER VALIDATION → RUNTIME BINDING → PUBLIC RUNTIME → DETERMINISTIC DEMO → JUDGE PERFORMANCE → PRE-LAUNCH/SHIP → SUBMISSION INTEGRITY → FINAL SNAPSHOT`

A gate marked `PROVEN` does not silently promote another gate.

## Machine check

`tests/test_gate_registry.py` checks allowed statuses, required reasons and consistency
with canonical state. It checks consistency, not truth: evidence still has to exist.

## Re-evaluation rule

Re-evaluate conditional gateways whenever scope, architecture, deployment topology,
evidence source, sponsor integration, or submission narrative changes.

## Evidence truth rules

- `LOCAL_STUB`, `SIMULATED`, and `PRESEEDED` must never be narrated as `LIVE` or `LIVE_BOB`.
- Consensus never upgrades inference to truth.
- Fresh-agent replay stays `NOT_EXECUTED / PENDING_LIVE_BOB` until genuinely executed.
- Public runtime claims require production evidence.

## x402 proof rule when activated

Never claim paid unlock or settlement without:
`payment requirement → verification → settlement → successful unlock/HTTP response`
plus network/amount/transaction or equivalent receipts where applicable.
