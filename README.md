# COLLIDER

## Find the decision the specification forgot to make.

**Disagreement-Driven Specification Repair for Parallel AI Agents**

Three implementation workstreams can all look correct locally and still encode
incompatible assumptions.

COLLIDER turns those disagreements into specification intelligence:

`independent interpretations → AGENT_DRIFT vs SPEC_GAP → minimal clarification → canon patch → targeted repair`

> **Three agents can be individually right and still reveal that the specification forgot to decide.**

---

## The proof in 15 seconds

The canonical fixture starts with three independently green workstreams:

- **30 local tests pass**
- **3/3 workstreams are locally green**
- **0 disagreements are surfaced before integration**

But executable integration reveals:

```text
customer_identity
API:     email
Ledger:  account_id

money field
API:     refund_amount
Ledger:  credit_amount
Result:
2 conflicts
INTEGRATION_BLOCKED

COLLIDER separates the two failures by evidence.
1. The agent is wrong
The source explicitly specifies refund_amount.
Ledger implemented credit_amount.
classification: AGENT_DRIFT
repair: Ledger credit_amount → refund_amount
repair source: AGENT_DRIFT_EVIDENCE
human question: none

2. The specification never decided
API chose email.
Ledger chose account_id.
The source never chooses a customer identity field.
classification: SPEC_GAP
epistemic state: UNKNOWN
auto-resolve: false

COLLIDER refuses to invent a canon and requires one human decision.
Canonical LOCAL decision:
customer_identity = account_id

That decision repairs only the affected API implementation:
API email → account_id
repair source: CANON_PATCH

Notifications remains unchanged.
Final executable result:
2 → 0 integration conflicts
INTEGRATION_READY

Try the evidence-bound demo
Generate its data directly from the committed canonical receipts:
python3 demo-ui/build_demo_data.py
python3 -m http.server 4173 --directory demo-ui

Open port 4173.
The UI does not hard-code the proof values independently. Its data generator
reads the canonical baseline, COLLIDER run, and comparative receipt, and fails
if their key invariants no longer hold.
Evidence
Canonical baseline
evidence/runs/baseline-001/
Observed:
- 30 local workstream tests pass
- 3/3 workstreams locally green
- 2 integration conflicts
- INTEGRATION_BLOCKED
- no COLLIDER root-cause classification
Canonical COLLIDER run
evidence/runs/local-resolved-004/
Observed:
- 1 SPEC_GAP
- 1 AGENT_DRIFT
- 1 human clarification
- 2 targeted executable repairs
- Notifications unchanged
- 0 final integration conflicts
- INTEGRATION_READY
- transient source and Python module state restored afterward
Comparative receipt
evidence/comparisons/baseline-001-vs-local-resolved-004.md
Fairness control:
API, Ledger, and Notifications implementation artifacts are byte-identical at
the start of the baseline and COLLIDER measured conditions.
Comparative evidence commit:
49d59a6c48aae5dce5ebad9f36909b5c71e77bb6
Demo UI commit:
852db864add8f24364ed91134749fe65055f811a
Truth boundary
The canonical comparative proof is LOCAL / PRESEEDED.
It proves the COLLIDER reconciliation, classification, abstention, canon,
targeted-repair, integration, and evidence-binding mechanisms.
It does not claim:
- LIVE_BOB-generated canonical interpretations
- live interactive human clarification
- wall-clock productivity improvement
- percentage productivity improvement
- production-scale generalization
Agent agreement is never upgraded into truth.
SOURCE EXPLICIT + AGENT DISAGREES
→ AGENT_DRIFT
→ evidence-grounded repair

SOURCE SILENT + AGENTS DISAGREE
→ SPEC_GAP
→ UNKNOWN
→ HUMAN DECISION REQUIRED

SOURCE SILENT + AGENTS AGREE
→ SHARED_INFERRED
→ not fact

Why this matters
Parallel coding agents increase implementation throughput, but parallelism also
creates a new coordination problem: independent agents can make different
reasonable choices where the specification is silent.
Traditional merge tools detect textual conflicts.
Tests detect behaviors they were designed to test.
COLLIDER targets a different failure mode:
locally valid implementations that reveal a missing cross-boundary decision.
The disagreement itself becomes a probe for specification quality.
Negative path
Correct abstention is a first-class product behavior.
If evidence is insufficient, conflicting, or unavailable, COLLIDER preserves
UNKNOWN rather than inventing a canonical answer.
See:
- evidence/runs/local-abstain-002/
- fixtures/failed-payment/EXPECTED-TRUTH.md
Real-world failure anchor
The Mars Climate Orbiter is used only as evidence for the broader class of
cross-boundary assumption failures: one interface received English-unit data
where metric units were expected, and verification processes failed to catch
the mismatch before mission loss.
COLLIDER does not claim it would have prevented that historical incident.
Primary references:
- NASA/JPL Mars Climate Orbiter investigation
- NASA technical report
- CodeScout, ACL Findings 2026, on underspecified software-engineering requests
See the source links and claim boundary in the project evidence/docs.
Repository map
collider/       reconciliation + classification + repair runtime
baseline/       no-COLLIDER executable control
fixtures/       canonical failed-payment specification fixture
evidence/       immutable run receipts, hashes, failures, comparisons
demo-ui/        evidence-bound judge/demo surface
demo/           canonical narrative + recording plan
product/        technical reality, failure modes, architecture
schemas/        structured interpretation contract
submission/     hackathon submission copy
state/          CURRENT + HANDOVER
tests/          integrity and regression verification

Verification
python3 -m pytest \
  tests/test_fixture.py \
  tests/test_baseline.py \
  api/tests/ \
  ledger/tests/ \
  notifications/tests/ \
  -q

Canonical current result:
102 passed, 6 subtests passed

Project status
Gate	Status
Concept Lock	PASS
Technical Reality	PASS
Local Runtime Evidence	PASS
Baseline Evidence	PASS
Comparative Evidence	PASS
Evidence Integrity	PASS
Demo Compression	PASS
Visual / Judge Performance	PASS
LIVE_BOB canonical runtime	NOT CLAIMED
Submission packaging	IN PROGRESS


Real failure > fake success.
MIT licensed.
