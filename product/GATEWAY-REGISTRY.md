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
| Concept Compression & Validation | PROVEN | product/CONCEPT-COMPRESSION-VALIDATION.md — internal checks pass and the documented waiver path was exercised; external comprehension remains unmeasured. |
| Real-User / Outsider Break Test | PROVISIONAL_PASS | Not executed; explicitly waived for this submission in evidence/validation/OUTSIDER-BREAK-TEST-WAIVER-2026-09-27.md. This status must never be narrated as a completed user test. |
| Technical Reality Check | PROVEN | product/TECHNICAL-REALITY-CHECK.md — 15 questions answered with epistemic labels. |
| Demo-First Architecture | PROVEN | product/DEMO-FIRST-ARCHITECTURE.md — fixture, classifier, canon routing, demo sequence. |
| Fixture Design | PROVEN | fixtures/failed-payment/BRIEF.md, fixtures/failed-payment/EXPECTED-TRUTH.md, fixtures/failed-payment/BASELINE-CONTRACT.md. |
| Evidence Schema | PROVEN | evidence/EVIDENCE-SCHEMA.md — artifact types and provenance labels defined. |
| Truth Boundary | PROVEN | product/TRUTH-BOUNDARY.md — OBSERVED/INFERRED/UNKNOWN enforced; shared assumptions visible in ACTIVE MODE and never upgraded (tests/test_guard_suite.py). |
| Negative Path | PROVEN | KEEP UNKNOWN (no canon, no repair) plus a false-positive control: harmless change is MERGE_ALLOWED (tests/test_guard_suite.py; public guard receipt confirms MERGE_ALLOWED). |
| Evidence Integrity | PROVEN | tests/test_active_repair.py pins canonical evidence hashes; suite no longer writes evidence/. Fresh LIVE_BOB replay is a boundary, not claimed. |
| Bob-Native Integration | ACTIVE | product/BOB-NATIVE-INTEGRATION.md — Bob load-bearing in implementation/design; canonical interpretations PRESEEDED, not LIVE_BOB. |
| Runtime / Commit Binding | PROVEN | evidence/runtime/RUNTIME-COMMIT-BINDING-2026-09-27.md binds public Worker UUID `364ad4fd-7eb3-4918-aef8-f9ad049ee20a` → Cloudflare version `364ad4fd` → Workers Build commit `e185e84d` → GitHub commit `e185e84d9d1cf00dfa1700b6bd2439e57887a291`. |
| Public Runtime / Live Proof | PROVEN | Three-verdict guard, separate-session isolation, real-iPhone mobile smoke, and exact runtime↔commit binding are proven by evidence/runtime/ receipts. CSP/header confirmation remains a Ship Assurance item, not a runtime-truth blocker. |
| Deterministic Demo | PROVEN | Public desktop and real-iPhone runs reproduce the three guard verdicts, exact restoration, Evidence/Active modes, and isolated sessions; runtime binding is proven. |
| Judge Performance Assurance | PENDING | Run after remaining public-runtime checks, before video lock. |
| Pre-Launch / Ship Assurance | PROVEN | product/PRE-LAUNCH-SHIP-ASSURANCE.md + evidence/runtime/LIVE-CSP-HEADERS-2026-09-27.md — public runtime, mobile, isolation, runtime binding, rollback documentation, and live CSP/security headers are proven or explicitly bounded. |
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
