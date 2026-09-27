# Conditional Gateway Registry

Every registered gateway receives an explicit status. Nothing is silently forgotten.
`N/A` means not applicable now, not forgotten forever. Re-evaluate at every material concept, architecture, runtime, or submission change.

| Gateway / Gate | Status | Reason / promotion condition |
|---|---|---|
| QUALIFY→DECIDE→DESIGN→DELIVER→AUDIT→EXPAND | ACTIVE | AUDIT of the escalated build; EXPAND items are preserved as North Star in product/SEMANTIC-CI-ESCALATION.md. |
| RUBRIC→PAIN→PROBLEM→DIFFERENTIATOR→EXECUTION→EVIDENCE→STORY→DEMO→Q&A | ACTIVE | STORY/DEMO is now centered on the three guard verdicts (demo/DEMO-SCRIPT-ACTIVE.md); final judge/video lock remains. |
| Real Negative Event Gate | PROVEN | product/PROBLEM-EVIDENCE.md — Mars Climate Orbiter anchors the failure class only; no prevention claim. |
| Competitive Novelty / Kill Gate | PROVISIONAL_PASS | Re-checked 2026-09-27 (product/SEMANTIC-CI-ESCALATION.md §7): no full kill-condition loop observed; decision-memory merge gates now exist, so lead with the DECISION_REQUIRED third verdict. |
| Creative Depth & Product Ambition | PROVEN | product/SEMANTIC-CI-ESCALATION.md — second pass against the working product: third verdict, same-diff counterfactual, continuous specification fuzzing; North Star preserved. |
| Distinctiveness Escalation | PROVEN | product/SEMANTIC-CI-ESCALATION.md — block-path bias, hard-coded memory and invisible shared assumptions found and fixed; sponsor-native strength stays PARTIAL (PRESEEDED, not LIVE_BOB). |
| Concept Compression & Validation | ACTIVE | product/CONCEPT-COMPRESSION-VALIDATION.md — internal checks pass; external Real-User / Outsider Break Test not yet run. |
| Real-User / Outsider Break Test | PENDING | Needs one person who did not build COLLIDER (protocol in product/CONCEPT-COMPRESSION-VALIDATION.md). No agent substitutes for it. |
| Technical Reality Check | PROVEN | product/TECHNICAL-REALITY-CHECK.md — 15 questions answered with epistemic labels. |
| Demo-First Architecture | PROVEN | product/DEMO-FIRST-ARCHITECTURE.md — fixture, classifier, canon routing, demo sequence. |
| Fixture Design | PROVEN | fixtures/failed-payment/BRIEF.md, fixtures/failed-payment/EXPECTED-TRUTH.md, fixtures/failed-payment/BASELINE-CONTRACT.md. |
| Evidence Schema | PROVEN | evidence/EVIDENCE-SCHEMA.md — artifact types and provenance labels defined. |
| Truth Boundary | PROVEN | product/TRUTH-BOUNDARY.md — OBSERVED/INFERRED/UNKNOWN enforced; shared assumptions visible in ACTIVE MODE and never upgraded (tests/test_guard_suite.py). |
| Negative Path | PROVEN | KEEP UNKNOWN (no canon, no repair) plus a false-positive control: harmless change is MERGE_ALLOWED (tests/test_guard_suite.py; public guard receipt confirms MERGE_ALLOWED). |
| Evidence Integrity | PROVEN | tests/test_active_repair.py pins canonical evidence hashes; suite no longer writes evidence/. Fresh LIVE_BOB replay is a boundary, not claimed. |
| Bob-Native Integration | ACTIVE | product/BOB-NATIVE-INTEGRATION.md — Bob load-bearing in implementation/design; canonical interpretations PRESEEDED, not LIVE_BOB. |
| Runtime / Commit Binding | ACTIVE | Mechanism shipped: every API response carries x-collider-worker-version (cloudflare/README.md). PROVEN after one live read of that id matched to its Workers Builds commit. |
| Public Runtime / Live Proof | ACTIVE | Escalated three-verdict guard is proven live by evidence/runtime/PUBLIC-THREE-VERDICT-GUARD-2026-09-27.md. Remaining: two-session isolation, mobile smoke, live CSP/header check, exact version↔commit binding. |
| Deterministic Demo | ACTIVE | Public desktop guard flow now captured end-to-end for MERGE_BLOCKED / MERGE_ALLOWED / DECISION_REQUIRED with restore; live mobile/session-isolation closure still pending. |
| Judge Performance Assurance | PENDING | Run after remaining public-runtime checks, before video lock. |
| Pre-Launch / Ship Assurance | ACTIVE | product/PRE-LAUNCH-SHIP-ASSURANCE.md — LIVE_RUNTIME_CHECK is partially proven on escalated build; remaining ship blockers are binding, isolation, mobile, and live CSP/header confirmation. |
| Submission Integrity | PENDING | submission/ copy predates the active loop and third verdict; refresh to proven truth boundary. |
| Final Snapshot / CURRENT / HANDOVER | ACTIVE | state/CURRENT.yaml and state/HANDOVER.yaml updated through the public three-verdict proof; final snapshot after remaining gates. |
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

`tests/test_gate_registry.py` parses this table and fails if a status is outside
`PROVEN / PROVISIONAL_PASS / ACTIVE / PENDING / BLOCKED / N/A`, if a PROVEN
gate cites a repository path that does not exist, if an N/A gate has no
reason, or if `state/HANDOVER.yaml` reports a different status for the same
gate. It checks consistency, not truth: evidence still has to exist.

## Re-evaluation rule

Re-evaluate all conditional gateways whenever scope, architecture, deployment topology, evidence source, sponsor integration, or submission narrative changes.

## Evidence truth rules

- `LOCAL_STUB`, `SIMULATED`, and `PRESEEDED` must never be narrated as `LIVE` or `LIVE_BOB`.
- Consensus never upgrades inference to truth.
- Fresh-agent replay stays `NOT_EXECUTED / PENDING_LIVE_BOB` until genuinely executed.
- Public runtime claims require production evidence, not repository inspection alone.

## x402 proof rule when activated

Never claim paid unlock or settlement without:
`payment requirement → verification → settlement → successful unlock/HTTP response`
plus network/amount/transaction or equivalent receipts where applicable.
