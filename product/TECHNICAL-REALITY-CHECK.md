# Technical Reality Check — COLLIDER

**Stage:** TECHNICAL_REALITY_CHECK  
**Project:** collider-bob  
**Date:** 2026-09-26  
**Epistemic labels used throughout:** OBSERVED · INFERRED · UNKNOWN

---

## Q1 — Which parts genuinely work during a hackathon (days, not months)?

**OBSERVED** — The following parts exist and are buildable within a hackathon window:

- **Deterministic fixture** — A hand-authored failing-payment brief with three workstreams (API, Ledger, Notifications) can be written and version-controlled in hours. The fixture makes the canonical scenario (identity: `email` vs `account_id`; money: decimal dollars vs integer cents) explicit and repeatable. This is the single most critical deliverable; it determines whether every other part of the demo is honest.

- **Structured interpretation artifacts** — The `interpretation.schema.json` already exists. Agents can emit JSON conforming to it in a single Bob session. Three interpretation files can be produced in one afternoon.

- **Reconciler (disagreement detection)** — Comparing two interpretation files for claims on the same `concept` with different `value`s is a deterministic set-difference operation. A minimal Python script or Bob agent executing that comparison works in a hackathon window.

- **Evidence resolver (source lookup)** — For a fixture with two or three controlled ambiguities, the "source evidence" is the fixture brief itself. Resolving whether `customer_id` is defined in the brief is a string search. This is unconditionally buildable.

- **Classifier (AGENT_DRIFT / SPEC_GAP / UNKNOWN)** — For the demo fixture, classification can be rule-based: if the disputed concept is explicitly defined in the brief and an agent contradicts it → AGENT_DRIFT; if the brief is silent and both values are plausible → SPEC_GAP; if evidence is missing or conflicting → UNKNOWN. Rule-based classification over a controlled fixture is deterministic and buildable in hours.

- **Canon patch emission** — `canon-patch.schema.json` already exists. A Bob agent or script can write a conforming JSON artifact after the human answers the minimal clarification question.

- **Impact router (dependency-aware targeted repair selection)** — For three workstreams and one or two concepts, the affected-workstream set can be hand-encoded in the fixture or produced by a trivial lookup. Full dynamic graph analysis is not required at hackathon scale.

- **Targeted repair prompt** — A single Bob Agent invocation with the canon patch as context can re-emit a repaired interpretation. This is a single prompt round-trip.

- **Negative path** — When evidence is absent, returning `SPEC_GAP → UNKNOWN → HUMAN DECISION REQUIRED` is a two-line branch in the classifier. Demonstrating deliberate abstention is no harder than demonstrating resolution.

- **Evidence artifacts** — Git-committed JSON files for each run, with commit SHAs, constitute sufficient receipts for a hackathon submission.

**INFERRED** — Bob's Plan mode can decompose the brief into workstream tasks and hand them to parallel subagents. This is the expected use of Plan/Agent mode; it has not yet been confirmed in a live session against this specific fixture.

**UNKNOWN** — Whether Bob's parallel subagent scheduling reliably produces meaningfully divergent interpretations without prompting them toward divergence. If agents share too much context they may converge; if they share too little they may produce incomparable outputs. Prompt engineering is required to control this, and the correct approach is not yet tested.

---

## Q2 — Which parts must be deterministic for a reliable live demo?

**OBSERVED** (from DEMO-CONTRACT.md and NEGATIVE-PATH.md) — A deterministic demo is a mandatory gate.

The following must be fully deterministic (no model variability at demo time):

| Component | Required determinism mechanism |
|---|---|
| Fixture brief | Static file, version-controlled |
| Interpretation artifacts | Pre-produced and committed; replayed, not regenerated |
| Reconciler output | Script over static inputs; no model call |
| Classifier output | Rule-based over the pre-produced interpretations |
| Canon patch | Committed artifact; replayed |
| Impact routing output | Static lookup in fixture or committed artifact |
| Negative path branch | Hardcoded trigger condition in classifier |

**INFERRED** — The targeted repair step (post-canon-patch agent execution) is the only step that must invoke a live model call during the demo. This step is the only acceptable source of non-determinism if the demo is live; all preceding artifacts should already exist as committed files.

**OBSERVED** — If any model call can fail due to network, rate limit, or output format divergence, it must be pre-run and the output committed. A "live" demo that fails due to an API call has no fallback. The DEMO-CONTRACT.md requires capturing the canonical run to an exact Git commit SHA before presentation.

---

## Q3 — Which IBM Bob capabilities are genuinely load-bearing?

**INFERRED** (stated as planned in `submission/BOB-USAGE.md`; not yet confirmed by session evidence):

| Capability | Load-bearing role | Confidence |
|---|---|---|
| **Plan mode** | Decomposes the brief into three independent workstream tasks | INFERRED — logical fit, not yet session-proved |
| **Parallel subagents** | Each workstream runs independently, producing divergent interpretations | INFERRED — this is the core architectural claim |
| **Repository context** | Evidence resolver uses the fixture repo as source truth for `evidence_refs` | INFERRED — requires Bob to read committed files as evidence |
| **Document understanding** | Brief and spec documents serve as the evidence corpus for the resolver | INFERRED — depends on Bob reading non-code documents |
| **Agent mode** | Targeted repair executes only for affected workstreams after canon patch | INFERRED — single-agent repair prompt |

**UNKNOWN** — Whether Bob's Plan mode decomposition will naturally produce interpretations that are semantically comparable enough for the reconciler to match on `concept` names. If agents name concepts differently (e.g., `customer_id` vs `user_identity`), the reconciler must be resilient to lexical variation or the fixture must constrain the concept vocabulary.

**OBSERVED** — `submission/BOB-USAGE.md` explicitly states: "Do not claim a Bob capability was used until task-session evidence proves it." No session evidence exists yet. All Bob capability claims are currently INFERRED, not OBSERVED.

---

## Q4 — Which parts must be simulated or locally stubbed?

**OBSERVED** — Runtime status is `NOT_IMPLEMENTED` (`state/CURRENT.yaml`). The following must be stubbed or pre-produced for any demo:

| Component | Stub strategy |
|---|---|
| Parallel subagent interpretations | Pre-authored and committed JSON files conforming to `interpretation.schema.json` |
| Evidence resolver (if no real repo corpus) | Fixture brief is the full corpus; resolver is a string-match over a static file |
| Classifier model judgment | Rule-based script for the two or three controlled concepts |
| Impact router | Hardcoded affected-workstream mapping in the fixture |
| Human clarification step | Simulated by a single human input or a pre-recorded answer injected at demo time |

**INFERRED** — Anything not yet session-proved with Bob must be treated as a stub at submission time unless a real session is run before the deadline. The submission does not earn its claims until the canonical run is executed and committed.

**OBSERVED** — The DEMO-CONTRACT.md and CANONICAL-RUN.md are explicit that no polished success narrative replaces a real run. Stubs are acceptable for building but must be labeled as stubs in the evidence record.

---

## Q5 — Which claims must NOT be made?

**OBSERVED** (derived directly from `product/PROBLEM-EVIDENCE.md`, `product/TRUTH-BOUNDARY.md`, `product/DIFFERENTIATOR.md`, `demo/DEMO-CONTRACT.md`):

1. **DO NOT claim** COLLIDER would have prevented the Mars Climate Orbiter loss. The MCO interface requirement existed; the incident was not an AI-agent failure.
2. **DO NOT claim** any unmeasured performance percentages (rework reduction, time savings, etc.) before a real baseline and COLLIDER run are compared.
3. **DO NOT claim** agreement among agents is proof — shared inference remains INFERRED regardless of how many agents agree.
4. **DO NOT claim** COLLIDER performs semantic merge, replaces Git, or replaces CI.
5. **DO NOT claim** correctness from model consensus.
6. **DO NOT claim** any Bob capability as load-bearing until Bob session evidence exists.
7. **DO NOT claim** SPEC_GAP resolution is automatic or autonomous — it requires human clarification.
8. **DO NOT narrate** a LOCAL_STUB or simulation as a LIVE_GATEWAY or real execution.
9. **DO NOT claim** competitive novelty is secure — the kill condition requires monitoring for prior art.
10. **DO NOT claim** submission readiness until the canonical run is committed and all required artifacts exist.

---

## Q6 — Which failure modes could invalidate the demo?

**INFERRED / UNKNOWN** — ranked by severity:

| Failure mode | Severity | Epistemic label | Mitigation |
|---|---|---|---|
| Parallel subagents produce identical interpretations (no divergence to classify) | **INVALIDATING** | UNKNOWN | Pre-author divergent interpretations; make this deterministic via committed artifacts |
| Classifier misclassifies the canonical SPEC_GAP as AGENT_DRIFT (or vice versa) in a model-driven path | **INVALIDATING** | UNKNOWN | Use rule-based classifier over controlled fixture; avoid live model classification for the canonical cases |
| Evidence resolver fails to find the brief's silence (false AGENT_DRIFT on a genuine SPEC_GAP) | HIGH | INFERRED | Fixture brief must explicitly omit the SPEC_GAP concept; verify by inspection before the demo |
| Bob Plan mode decomposes into non-comparable workstream tasks | HIGH | UNKNOWN | Pre-run Plan decomposition; commit the task list before the demo |
| Network / API failure during live targeted-repair call | HIGH | INFERRED | Pre-commit the repair output; replay instead of re-running live |
| Canon patch schema validation failure | MEDIUM | OBSERVED risk | Pre-validate all committed artifacts against JSON schemas |
| Impact router includes an unaffected workstream (unnecessary rerun) | MEDIUM | INFERRED | Acceptable for a demo; does not invalidate the mechanism |
| Impact router misses an affected workstream | HIGH | INFERRED | Fixture workstream dependencies must be explicitly modeled |
| Negative path fails to abstain (invents a canon on UNKNOWN evidence) | **INVALIDATING** | INFERRED | Negative path must be a hard branch, not a model judgment |
| Submission claims exceed what the canonical run proved | **DISQUALIFYING** | OBSERVED risk | Never write to `submission/` before the canonical run exists |

---

## Q7 — What is the smallest architecture that proves the mechanism without reducing the full product vision?

**INFERRED** — The minimum viable proof is:

```
1. Static fixture brief (brief.md, committed)
2. Three pre-authored interpretation JSON files (api.json, ledger.json, notifications.json)
3. Reconciler: Python script — finds claims on the same concept with different values
4. Evidence resolver: Python script — checks whether the concept appears in brief.md
5. Classifier: rule-based — OBSERVED in brief + contradiction → AGENT_DRIFT;
                             silent in brief + disagreement → SPEC_GAP;
                             evidence ambiguous → UNKNOWN
6. Human clarification: one question printed to stdout; answer read from stdin or pre-committed
7. Canon patch: script writes canon-patch.json (conforming to schema)
8. Impact router: reads affected_workstreams from spec-gap.json
9. Targeted repair: one Bob Agent call with canon patch in context, producing repaired JSON
10. Negative path: classifier returns UNKNOWN; system prints HUMAN DECISION REQUIRED; halts
```

This architecture:
- Uses Bob for task decomposition (Plan), interpretation emission (parallel Agent), and targeted repair (Agent) — all load-bearing
- Keeps reconciler, evidence resolver, and classifier as deterministic scripts — no model variability on the critical decision path
- Requires one real human clarification — demonstrating the minimal-question principle
- Demonstrates AGENT_DRIFT, SPEC_GAP, UNKNOWN, and a preserved unaffected workstream

**OBSERVED** — The full product vision (production-grade distributed orchestration, dynamic dependency graphs, arbitrary repo analysis) is explicitly listed as a Non-Goal in `product/PRD.md`. The small architecture above proves the mechanism without those features.

---

## Q8 — How to build a fair baseline without COLLIDER?

**INFERRED** — A fair baseline is:

1. Present the same fixture brief to a human developer or Bob agent **without** the COLLIDER reconciliation loop.
2. Run the same three workstream agents independently, producing the same workstream outputs.
3. **Do not** expose the parallel outputs to any reconciler or cross-comparison step.
4. The human (simulating a tech lead in a non-COLLIDER world) must integrate the three workstreams manually.
5. Measure: number of integration-time contradictions discovered, number of human clarification rounds needed, number of workstreams that required rework after integration, time from task start to integration-ready.

**OBSERVED** (from `demo/DEMO-CONTRACT.md`) — The baseline must use the **same** fixture; measurements must be **observed**, not estimated. Do not preset improvement percentages.

**INFERRED** — The baseline will naturally surface the SPEC_GAP at integration time rather than at interpretation time. That is the correct behavior to demonstrate: COLLIDER surfaces it earlier in the cycle.

---

## Q9 — How to build a comparable run with COLLIDER?

**INFERRED** — The COLLIDER run uses the same fixture and produces:

1. Same three workstreams, same agents, same brief.
2. Interpretation artifacts committed before any integration step.
3. Reconciler runs before integration — disagreement detected at interpretation time.
4. Evidence resolver checks the brief — SPEC_GAP classified.
5. One minimal clarification asked and answered.
6. Canon patch committed.
7. Impact router identifies affected workstreams.
8. Only affected workstreams replanned/repaired.
9. Unaffected workstream preserved unchanged.
10. Negative path demonstrated for the UNKNOWN case.

Measurements (same metrics as baseline): human clarifications, rework cycles, workstreams rerun, time to integration-ready, contradictions caught before integration.

**OBSERVED** — `demo/DEMO-CONTRACT.md` explicitly lists these five measurement dimensions. Do not add unmeasured dimensions.

---

## Q10 — Which evidence artifacts must both runs generate?

**OBSERVED** (from `demo/CANONICAL-RUN.md`) — Both runs must produce and commit:

| Artifact | Baseline | COLLIDER run |
|---|---|---|
| Git commit SHA | ✓ | ✓ |
| Fixture version (brief.md hash or commit) | ✓ | ✓ |
| Three workstream output artifacts | ✓ | ✓ |
| Integration-time disagreements discovered | ✓ (manual, documented) | ✓ (reconciler output JSON) |
| Number of human clarifications required | ✓ | ✓ |
| Rework cycles | ✓ | ✓ |
| Workstreams rerun | ✓ | ✓ |
| Time to integration-ready | ✓ | ✓ |
| Timestamps | ✓ | ✓ |

**COLLIDER-only artifacts** (not present in baseline):
- `interpretation.schema.json`-conforming JSON for each workstream
- `spec-gap.schema.json`-conforming disagreement classification
- `canon-patch.schema.json`-conforming canon patch
- Impact router output (affected workstream list)
- Targeted repair output artifact
- Negative path abstention event (UNKNOWN state log)

**OBSERVED** — `demo/CANONICAL-RUN.md` explicitly requires known failures and limitations to be preserved in the run record. Both runs must include a failures section.

---

## Q11 — Which parts of the mechanism depend on model judgment and which can be deterministic?

| Step | Model-dependent? | Rationale |
|---|---|---|
| Task decomposition (Plan) | INFERRED-model | Bob Plan uses the model to decompose the brief |
| Interpretation emission (per workstream) | **Model-dependent** | Each subagent produces interpretation JSON via the model |
| Reconciler (disagreement detection) | **Deterministic** | Set-difference over concept/value pairs; no model needed |
| Evidence resolver (source lookup) | **Deterministic** | String/semantic search over the fixture brief |
| Classifier (AGENT_DRIFT / SPEC_GAP / UNKNOWN) | **Should be deterministic** for demo | Rule-based over resolver output; model call introduces variability |
| Canon patch emission | **Deterministic** | Schema-conforming write after human answer |
| Impact router | **Deterministic** | Lookup against affected_workstreams in spec-gap artifact |
| Targeted repair | **Model-dependent** | Bob Agent re-executes with canon patch context |
| Negative path abstention | **Deterministic** | Hard branch: if evidence_state = INSUFFICIENT/CONFLICTING/UNAVAILABLE → UNKNOWN |

**INFERRED** — The critical insight: the classifier is the trust boundary. If the classifier uses a model call, misclassification (false AGENT_DRIFT, false SPEC_GAP) is a persistent risk. For the demo, the classifier **must** be deterministic over the controlled fixture. For the full product, a model-assisted classifier is reasonable but must be disclosed and tested.

---

## Q12 — Where could a false positive / false SPEC_GAP occur?

**INFERRED** — A false SPEC_GAP (classifying an AGENT_DRIFT as a spec gap) can occur:

1. **Evidence resolver fails to find explicit spec text** — If the brief contains the answer but the resolver's pattern match misses it (different casing, synonym, indirect reference), the resolver incorrectly reports silence and the classifier returns SPEC_GAP instead of AGENT_DRIFT.

2. **Concept name mismatch** — Two agents name the same concept differently (`customer_id` vs `user_id`). The reconciler fails to detect the disagreement at all, producing a false negative (missed disagreement), or produces a false SPEC_GAP if it matches incorrectly.

3. **Over-broad concept granularity** — The reconciler groups claims at too coarse a level, merging a concrete contradiction (AGENT_DRIFT) with a genuine ambiguity (SPEC_GAP) into one SPEC_GAP finding.

4. **Stale evidence** — The brief has been updated after the interpretations were produced. The resolver queries the current brief but the agents responded to an older version. The resolver sees silence that is actually an artifact of a version mismatch, classifying an old AGENT_DRIFT as a new SPEC_GAP.

**INFERRED** — The fixture mitigation: control concept vocabulary in interpretation prompts, use exact-match on a version-pinned brief, and require `evidence_refs` to include a content hash or line number.

---

## Q13 — Where could AGENT_DRIFT be incorrectly classified as SPEC_GAP?

**INFERRED** — This is the same failure as Q12 cases 1 and 4, but worth stating explicitly:

1. **Resolver misses explicit text** (wrong parser, synonym, section not indexed) — The correct answer is in the brief but invisible to the resolver. The system reports SPEC_GAP and asks a clarification question for something the spec already decided. The human answers; the canon patch writes back the value that was already in the brief. This is an embarrassing but non-catastrophic failure for the demo. It is a correctness failure for the product.

2. **Implicit requirements treated as absent** — A requirement is conveyed by a type definition, an enum, or an import in the fixture repository rather than in plain text. The evidence resolver only searches the brief document, not the code. Explicit typing evidence is invisible to a document-only resolver.

3. **Model-based resolver over-reports uncertainty** — If the resolver uses a model to assess whether the brief is "silent" on a concept, the model may hedge toward uncertainty, producing false SPEC_GAP on clear requirements. A rule-based resolver over a controlled fixture eliminates this risk.

**INFERRED** — **Strongest mutation:** The evidence resolver must search all source material in scope (brief, existing schema files, type definitions, repo contracts), not only the top-level brief document. For the hackathon fixture, the full evidence corpus should be explicitly enumerated and version-pinned.

---

## Q14 — Where could a SPEC_GAP be incorrectly treated as agent error?

**INFERRED** — A SPEC_GAP is incorrectly treated as AGENT_DRIFT when:

1. **Resolver finds a value in the brief that happens to match one agent's interpretation** — The brief mentions `email` in an unrelated context (e.g., notification template). The resolver reports OBSERVED evidence for `email` as customer identity. The classifier returns AGENT_DRIFT against the agent that chose `account_id`, even though the brief never decided the identity question in a normative sense.

2. **Canon patch source is set to `EXPLICIT_SPEC` when it should be `HUMAN_CLARIFICATION`** — `canon-patch.schema.json` has exactly this field. If the patch source is set incorrectly, downstream audit trails are corrupted. A SPEC_GAP resolution masquerades as spec compliance.

3. **Majority vote used as classifier** — If two of three agents agree on `email`, the classifier might weight that as "correct" and flag the third agent as AGENT_DRIFT. Agent consensus is not evidence. `product/TRUTH-BOUNDARY.md` explicitly forbids this: "Agreement among agents is not proof."

4. **Evidence resolver returns SUFFICIENT on partial evidence** — The brief defines `customer_id` for one workstream context but not for the cross-boundary interface between workstreams. The resolver reports SUFFICIENT, classifier returns AGENT_DRIFT, but the interface was genuinely underdecided.

**INFERRED** — Mitigation: the `evidence_state` field in `spec-gap.schema.json` must require the resolver to confirm the evidence is normative and in scope, not merely a textual match. The `SUFFICIENT` state should require a section reference, not just keyword presence.

---

## Q15 — What must happen when evidence is missing, stale, conflicting, or unavailable?

**OBSERVED** (from `product/TRUTH-BOUNDARY.md`, `demo/NEGATIVE-PATH.md`, `state/CURRENT.yaml`):

| Evidence state | Required behavior |
|---|---|
| **MISSING** (`evidence_state: UNAVAILABLE`) | Classifier must return `UNKNOWN`. System must not invent a canon. Affected workstreams must halt or enter PENDING state. One minimal clarification question must be surfaced. |
| **STALE** (brief updated after interpretations were produced) | Interpretations must be flagged with a version-mismatch warning. Classification must not proceed until interpretations are re-produced against the current brief or the staleness is explicitly acknowledged. |
| **CONFLICTING** (`evidence_state: CONFLICTING`) | Classifier must return `UNKNOWN`. The conflict must be recorded in the spec-gap artifact with both conflicting evidence references. Do not resolve by majority or recency without explicit human decision. |
| **UNAVAILABLE** (brief document not accessible, repo context unavailable) | Evidence resolver must return `UNAVAILABLE`. Classifier must return `UNKNOWN`. System must not fall through to a default canon. |

**OBSERVED** — `state/CURRENT.yaml` sets `missing_evidence_policy: UNKNOWN`. This is the project's single most important invariant. Any implementation that overrides this policy (by returning a default value, a model-guessed answer, or a majority vote) violates the truth boundary and invalidates the submission.

**INFERRED** — The negative path is not a failure state; it is a first-class product behavior. Demonstrating that COLLIDER **refuses to canonize uncertain evidence** is as important as demonstrating that it resolves clear AGENT_DRIFT. The `demo/NEGATIVE-PATH.md` file makes this explicit: "Correct abstention is treated as product success, not a demo failure."

**INFERRED** — For the demo, the UNKNOWN branch must be demonstrated with a live case, not merely described. A committed example where evidence_state is CONFLICTING and classification is UNKNOWN, with a printed `HUMAN DECISION REQUIRED` message and no automatic canon patch, is required evidence.

---

## Core assumption audit

| Assumption | Verdict | Basis |
|---|---|---|
| Parallel agents will naturally produce divergent interpretations | **UNSOUND if left to chance** — INFERRED risk | Agents with shared context may converge. Mitigation: prompt isolation; pre-authored divergence for demo. |
| The reconciler can match concepts across agents without normalization | **UNSOUND for open-domain** — INFERRED risk | Concept naming will diverge. Mitigation: vocabulary constraint in interpretation prompt, or fuzzy-match with evidence_refs. |
| Document-only evidence resolver is sufficient | **UNSOUND for code-heavy specs** — INFERRED risk | Implicit requirements live in types, schemas, contracts. Mitigation: enumerate full evidence corpus including schemas. |
| Model-based classifier is reliable | **UNSOUND for production** — INFERRED | Model judgment can misclassify. Mitigation: rule-based classifier for controlled fixture; disclose model risk for open-domain. |
| Three workstreams are enough to prove the mechanism | **SOUND** — OBSERVED in PRD | PRD success proof requires exactly: one AGENT_DRIFT, one SPEC_GAP, one preserved unaffected workstream, one UNKNOWN. Three workstreams are sufficient. |
| Correct abstention is a valid demo outcome | **SOUND** — OBSERVED in NEGATIVE-PATH.md | Explicitly stated as product success. |

---

## Strongest mutation if the core assumption is unsound

If parallel agents do not produce genuinely divergent interpretations without prompt engineering, the thesis is not broken — it is sharpened: **COLLIDER's value is precisely in detecting the cases where agents *appear* to agree but have silently made incompatible assumptions.** The mutation is: the fixture must include at least one case where agents produce textually similar-looking outputs that are semantically incompatible (e.g., both say "customer ID" but one means email, one means UUID). The reconciler must detect value-level disagreement, not just surface-label disagreement. This is a harder and more honest demo than one that relies on agents naively choosing different words.

---

*Generated from direct inspection of the COLLIDER project codebase. No claim in this document has been promoted above its evidenced epistemic level.*
