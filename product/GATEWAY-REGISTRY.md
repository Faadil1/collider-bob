# Conditional Gateway Registry

Every registered gateway receives an explicit status. Nothing is silently forgotten.

| Gateway / Gate | Status | Reason / promotion condition |
|---|---|---|
| QUALIFY→DECIDE→DESIGN→DELIVER→AUDIT→EXPAND | ACTIVE | Global lifecycle: currently in DESIGN |
| RUBRIC→PAIN→PROBLEM→DIFFERENTIATOR→EXECUTION→EVIDENCE→STORY→DEMO→Q&A | ACTIVE | Hackathon loop: at EXECUTION entry |
| Real Negative Event Gate | PROVEN | Mars Climate Orbiter anchors failure class (class evidence only; MCO causation claim forbidden) |
| Competitive Novelty / Kill Gate | PROVISIONAL_PASS | Continue monitoring; kill condition documented in DIFFERENTIATOR.md |
| Technical Reality Check | COMPLETE | product/TECHNICAL-REALITY-CHECK.md — 15 questions answered with epistemic labels |
| Demo-First Architecture | COMPLETE | product/DEMO-FIRST-ARCHITECTURE.md — fixture, classifier, canon routing, 15-step demo sequence |
| Fixture Design | COMPLETE | fixtures/failed-payment/BRIEF.md, EXPECTED-TRUTH.md, BASELINE-CONTRACT.md |
| Evidence Schema | COMPLETE | evidence/EVIDENCE-SCHEMA.md — all artifact types defined |
| Truth Boundary | ACTIVE | Core runtime behavior; missing_evidence_policy: UNKNOWN enforced |
| Negative Path | ACTIVE | SPEC_GAP→UNKNOWN mandatory; demo/NEGATIVE-PATH.md governs |
| Evidence Integrity | ACTIVE | Proof labels (OBSERVED/INFERRED/UNKNOWN) required on all claims |
| Bob-Native Integration | ACTIVE | product/BOB-NATIVE-INTEGRATION.md — designed load-bearing roles; runtime proof PENDING (INFERRED until canonical session evidence) |
| Runtime / Commit Binding | PENDING | Activate when the first real agent run is committed with SHA |
| Deterministic Demo | PENDING | Required before final evidence capture; fixture committed, run not yet executed |
| Judge Performance Assurance | PENDING | Required before submission |
| Submission Integrity | PENDING | Required before submission; no claims written to submission/ until canonical run exists |
| x402 | N/A | No payment rail |
| Nanopayments | N/A | No payment rail |
| Wallets | N/A | No wallet value movement |
| Smart Contracts | N/A | No on-chain execution |
| App Kit / sponsor gateway | N/A | No applicable integration yet; re-evaluate if architecture changes |
| LIVE_GATEWAY promotion | N/A | No external settlement gateway |

## Re-evaluation rule
N/A is not permanent. Re-evaluate all conditional gateways at every major concept or architecture change.

## x402 proof rule when activated
Never claim paid unlock or settlement without a real chain of evidence:
payment requirement → verification → settlement → successful unlock/HTTP response,
with network/amount/transaction or equivalent references and receipts when applicable.

LOCAL_STUB or simulation must never be narrated as LIVE_GATEWAY.
