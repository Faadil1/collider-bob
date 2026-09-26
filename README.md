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
## Semantic CI loop: the demo is action-capable

`DETECT → DECIDE → COMPILE → PATCH → VERIFY → REMEMBER → GUARD`

```bash
python3 -m collider.gate                       # committed tree → DECISION_REQUIRED (exit 1)
python3 demo-ui/server.py                      # ACTIVE MODE UI at 127.0.0.1:4173
python3 -m collider.decision_compiler \
  --value account_id --decision-id my-decision # CLI equivalent of USE account_id
python3 -m collider.guard_probe \
  --workspace .collider/workspaces/my-decision \
  --out-dir .collider/runs/my-decision          # CLI equivalent of the guard probe
```

The SPEC_GAP panel offers exactly two choices:

- **KEEP UNKNOWN**: correct abstention. No canon, decision memory or spec patch is
  written, nothing is repaired, and the gate stays `DECISION_REQUIRED`. Only a
  bounded local action receipt (`abstention.json`) is recorded. It is not a
  canonical decision receipt.
- **USE account_id**: compiles the decision (below).

`email` is not offered as a decision. In the canonical demo it is the value a
future agent tries to reintroduce, and the guard blocks it.

Choosing `customer_identity = account_id` compiles one human decision into:

- canon decision artifact: `canon/decisions/customer_identity.json`
- source-spec patch: a BRIEF.md "Adopted Decisions" section with a machine-readable
  `collider:canon` marker, plus `canon/spec-patches/customer_identity.json`
- targeted code repair: API `email → account_id` (CANON_PATCH), Ledger
  `credit_amount → refund_amount` (AGENT_DRIFT_EVIDENCE); Notifications unchanged
- regression contract: `contracts/test_canon_customer_identity.py`
- decision memory: `canon/decision-memory.json`

It then runs verification in the compiled tree (30 workstream tests + 7 contract
tests), the integration probe (2 → 0, `INTEGRATION_READY`), and the gate
(`DECISION_REQUIRED → SEMANTICALLY_READY`).

Mutation happens in a workspace copy (`.collider/workspaces/<id>`, git-ignored).
The committed tree stays the canonical pre-decision input for baseline-001 and
local-resolved-004, and the compiler checks that its hashes did not change.

Gate verdicts: `DECISION_REQUIRED` (unresolved SPEC_GAP) · `AGENT_DRIFT` (explicit
source or resolved canon violated) · `SEMANTICALLY_READY` (canon resolved,
dependents conform, verification passes) · `VERIFICATION_FAILED`.

Committed receipt: `evidence/decisions/decision-001/` (human decision source
PRESEEDED). UI-triggered compiles record `INTERACTIVE_LOCAL_UI` and write only to
`.collider/runs/`.

GUARD is a second action. After `SEMANTICALLY_READY`, **TEST A FUTURE AGENT CHANGE**
runs `collider/guard_probe.py` in the compiled workspace. It reads the decision memory,
rewrites `api/handlers/recover.py` `CUSTOMER_IDENTITY_FIELD` from `account_id` to
`email`, runs the gate (`AGENT_DRIFT` vs `RESOLVED_CANON` → `MERGE_BLOCKED`), runs the
regression contract (fails), restores the exact prior bytes, and re-runs the gate
(`SEMANTICALLY_READY`, 0 conflicts, contract passing). The receipt is
`.collider/runs/<id>/guard-probe.json`. GUARD is shown as complete only after this
probe has run. The guard is not the fresh-agent replay.

Modes: **ACTIVE MODE** (default; truth label `LOCAL ACTIVE DEMO · PRESEEDED
INTERPRETATIONS · INTERACTIVE HUMAN DECISION`) needs the local action server. If the
server is unreachable, the UI says `ACTIVE MODE UNAVAILABLE` and never substitutes
receipts. **EVIDENCE MODE** (`COMMITTED EVIDENCE · LOCAL / PRESEEDED`) shows baseline-001,
local-resolved-004 and decision-001 as committed receipts.

Fresh-agent replay: the interface and acceptance contract exist
(`collider/replay.py`), but execution is **NOT_EXECUTED / PENDING_LIVE_BOB**. It only
accepts results from an independent `LIVE_BOB_SESSION`.

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
  tests/test_semantic_ci.py \
  tests/test_active_repair.py \
  -q

Current result:
175 passed, 6 subtests passed

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
