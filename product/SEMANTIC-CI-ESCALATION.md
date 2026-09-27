# Semantic CI Escalation — the third verdict

Second Creative Depth & Distinctiveness pass, run against the working product
(commit `bdfd9d3` + the public Cloudflare runtime), not against the documents
that declared the first pass PROVEN. Implemented in commit `6564720`.

## 1. What was challenged

The first pass declared "memory without consequence", "happy-path bias" and
"signature moment" as PASS. Re-deriving each from the code:

| # | Finding in the working product | Class of bias | Severity |
|---|---|---|---|
| F1 | `collider/gate.py` hard-coded `customer_identity`. Decision memory could only ever change the verdict for that one concept; the "memory" was a special case, not a mechanism. | implementation-shaped vision | high |
| F2 | The guard had exactly one probe and it could only ever block. A CI check that has never been seen to *pass* a change is unfalsifiable: nothing showed the guard was not a blanket block. | happy-path bias (inverted: block-path bias) | high |
| F3 | The third truth rule — source silent + agents agree → SHARED ASSUMPTION → INFERRED — was proven in the pipeline tests but invisible in ACTIVE MODE. The gate never reported `money_representation`. | truth boundary not in the product | medium |
| F4 | "Memory changes future behaviour" was asserted, never measured. There was no counterfactual. | memory without proven consequence | medium |
| F5 | Running the documented test command rewrote committed `evidence/runs/test-run/`; a bare `pytest` collected the committed regression contract and wrote `__pycache__` into `evidence/decisions/decision-001`, breaking its content hash. | evidence integrity hazard | medium |
| F6 | (found while shipping this pass) the API-only container image would have crashed at import if the server required a page-only file. Caught by running the real image, fixed before push. | ship risk | high, prevented |
| F7 | No security headers / CSP; no way to tell from a live response which deployment produced it. | ship readiness | medium |

### Category challenge

Alternatives considered for the category: *specification fuzzer*, *semantic
type checker for specs*, *decision compiler*, *agent-drift linter*.
**Semantic CI stays**, and this pass is what earns the name. A CI check has
two verdicts: pass or fail. COLLIDER now has three, and the third is the product:

| Verdict | Meaning | Who else can say it |
|---|---|---|
| `MERGE_ALLOWED` | no semantic concept changed; memory still holds | any CI |
| `MERGE_BLOCKED` | the change contradicts explicit source or resolved canon | tests / policy gates / decision-memory tools, *if* someone recorded the rule |
| **`DECISION_REQUIRED`** | the change is neither right nor wrong: it exposes a decision nobody made | — |

The third verdict fires on a change that violates no recorded rule and passes
every test (37/37), because the workstreams now disagree where the source is
silent. That is specification fuzzing continuing *after* the first repair:
every future agent change is a new ambiguity probe.

## 2. Deeper opportunities found

1. **Same diff, different verdict.** Each guard run now also judges the
   identical changed tree with decision memory removed. Where the verdicts
   differ, memory is provably what changed the outcome:
   - identity revert: `AGENT_DRIFT / MERGE_BLOCKED` with memory, `DECISION_REQUIRED` without;
   - harmless wording change: `MERGE_ALLOWED` with memory, `DECISION_REQUIRED` without;
   - money-unit change: `DECISION_REQUIRED` both ways — memory does not cover an undecided concept, and the product says so.
2. **Continuous specification fuzzing.** Ambiguity is not only discovered
   before or during the first integration. Future changes discover it too.
3. **A raised question is closed only by authority.** The gate distinguishes
   two kinds of agreement without canon (`collider/concepts.py`):
   `BLOCK` — the question was already raised (customer identity diverged in
   baseline-001), so later agreement does not close it; `DISCLOSE` — never yet
   diverged, reported as an unratified INFERRED assumption, non-blocking.
4. **One truth table, any concept.** Canon, explicit source, SPEC_GAP and
   shared assumption are evaluated uniformly per registered concept; decision
   memory constrains whatever concept it records.

## 3. What was built (vertical slice of the North Star)

- `collider/concepts.py` + gate refactor; `gate.assumptions[]` (INFERRED,
  `upgrades_to_fact: false`, `ratified: false`, `blocking: false`).
- Declared `MONEY_UNIT = "integer_cents"` in the three workstreams (INFERRED,
  same declaration style as `CUSTOMER_IDENTITY_FIELD`).
- `collider/guard_probe.py`: fixed suite `IDENTITY_REVERT`,
  `COMPATIBLE_CHANGE`, `MONEY_UNIT_DRIFT`; counterfactual without memory;
  verdicts derived from the gate; exact-byte restore; one receipt per probe.
- `/api/guard {decision_id, probe}` (enum only); UI: three future agent
  changes, verdict colours, counterfactual line, shared-assumption strip.
- Ship: CSP/security headers (pages + API), Worker Version id on every API
  response, per-container action cap, favicon, rollback doc.
- Integrity: canonical suite pinned in `pytest.ini`; tests never write
  `evidence/`.

## 4. Deliberately rejected

| Idea | Why not |
|---|---|
| Judge-supplied arbitrary diffs | Breaks the bounded-input rule (no paths/values from HTTP) and invites unverifiable demos. Fixed probes are real mutations with real verdicts. |
| Scripted "fresh agent" replay | Rejected. The real replay evidence is session-bound Bob execution: Attempt 01 is preserved as REPLAY_FAIL; Attempt 02 is a targeted-repair REPLAY_PASS after a withheld 7/7 contract. |
| RATIFY action for the money unit in this build | Requires generalising the decision compiler to a concept with no repair and adds a fourth decision to the judge path. Preserved as the next North Star step (below). |
| Counting the money-unit divergence as an "integration conflict" | The conflict probe is the canonical baseline definition (identity + money field). Changing it would silently redefine historical evidence. The divergence is reported as a SPEC_GAP finding instead. |
| LLM confidence / semantic-similarity classification | Consensus and confidence are not authority; the classifier stays deterministic. |
| Durable-Object rate limiter | Out of proportion for a judged demo; bounded by `max_instances`, body cap, route allowlist and per-container run cap. |
| Gate orchestrator as a product feature | Strengthens our process, not COLLIDER. Kept as a lean repository consistency test (`tests/test_gate_registry.py`). |

## 5. North Star (preserved, not claimed)

1. **RATIFY** — a human promotes a disclosed assumption to canon; the same
   money-unit change then flips from `DECISION_REQUIRED` to `MERGE_BLOCKED`.
2. **Decision interaction** — decisions that constrain each other (money unit
   ↔ currency ↔ rounding) form a dependency graph; conflicting canon is itself
   a finding.
3. **COLLIDER as a required PR check** — the three verdicts on every agent PR,
   decision memory as a portable semantic lockfile across repos and sessions.
4. **Pre-implementation fuzzing** and **fresh-agent replay** with genuinely
   independent live agents (`PENDING_LIVE_BOB`).
5. **Concept extraction** beyond declared constants.

## 6. Truth boundary of this pass

- Concepts are observed from declared constants (`CUSTOMER_IDENTITY_FIELD`,
  `CREDIT_FIELD_NAME`, `MONEY_UNIT`) and function signatures, not inferred
  semantics.
- Probes are controlled, fixed changes — not agents, not replay.
- The counterfactual removes decision memory and the spec marker only; the
  code judged is the same changed tree.
- Interpretations remain `PRESEEDED`. Nothing is `LIVE_BOB`.
- Verified locally and in the real container image; the public runtime has not
  yet been observed on this commit (this environment's egress policy blocks
  the workers.dev host).

## 7. Competitive re-check (2026-09-27, search snippets only — INFERRED)

Adjacent: decision-memory merge gates and "memory-as-governance" for coding
agents (e.g. Hivelore, PROJECTMEM), specification-gap research on code
agents, interactive clarification agents (AMBIG-SWE), requirement-elicitation
tools. These enforce or preserve decisions that exist, or ask questions before
work. None observed shows the kill-condition loop (independent
interpretations → source-grounded AGENT_DRIFT vs SPEC_GAP → minimal
clarification → dependency-aware repair), nor a `DECISION_REQUIRED` verdict on
a change that breaks no recorded rule. Kill gate: **PROVISIONAL_PASS**,
monitoring continues; the merge-gate-over-memory space is now crowded, so the
third verdict is the distinction to lead with.
