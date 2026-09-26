# COLLIDER — Failure Modes

This document catalogs failure modes that could invalidate the demo, corrupt the evidence
record, or produce misleading classification results. Each entry describes the failure,
its severity, and the mitigation.

---

## FM-01 — Model non-determinism

**Failure:** The subagents do not consistently produce the planned disagreements. On some runs,
Ledger uses `refund_amount` instead of `credit_amount`. On others, all three workstreams
happen to agree on `account_id`. The demo fixture requires specific disagreements to be present;
if they are absent, there is nothing to classify.

**Severity:** Critical. Invalidates the demo entirely if the planned disagreements do not
materialize. Also undermines reproducibility claims.

**Mitigation:**
- Use a **deterministic fixture**: workstream agent prompts are authored to produce specific
  interpretations, not inferred freely. The disagreements are engineered, not hoped for.
- The interpretation objects (what each agent declares about shared concepts) are committed
  artifacts in the fixture. If a live agent run is needed for the demo, the interpretation
  objects are verified against the fixture before classification proceeds.
- If live generation is unreliable, fall back to replaying committed interpretation objects
  through the classifier. The classifier behavior is what is being demonstrated; the agent
  generation step is scaffolding.
- Label clearly: "these interpretations were produced by independent agents running the brief"
  and show the evidence. Do not simulate interpretations without disclosure.

---

## FM-02 — Source evidence retrieval failure

**Failure:** When the classifier runs Step 3, it cannot locate the relevant passage in the
product brief or spec document. For example: the brief text is not indexed, the retrieval
returns no results, or it returns the wrong passage. The classifier cannot confirm `AGENT_DRIFT`
for `field_name` because it cannot find the word "refund_amount" in the source.

**Severity:** High. A failed retrieval silently downgrades `AGENT_DRIFT` to `SPEC_GAP / UNKNOWN`,
misclassifying a known agent error as a specification gap. This is the most dangerous failure
mode because it produces a wrong but plausible-looking result.

**Mitigation:**
- For the demo fixture, the source evidence is a committed, line-numbered document. The
  classifier can use a direct text lookup for "refund_amount" rather than semantic retrieval.
- Log the evidence reference (document, line, excerpt) for every Step 3 decision.
- Mark the evidence state as `INFERRED` rather than `OBSERVED` when the retrieval was
  approximate. Never narrate approximate retrieval as a confirmed source match.
- If retrieval fails entirely, the classifier must return `UNKNOWN`, not `SPEC_GAP` or
  `AGENT_DRIFT`. Failure to retrieve is not the same as source silence.

---

## FM-03 — False SPEC_GAP (scope filter misses an internal field or includes it incorrectly)

**Failure:** The Step 0 scope filter incorrectly classifies an internal response body field as
a stub-defined cross-boundary field, or incorrectly excludes a genuine stub field. Either way,
the negative control case breaks: the classifier raises a SPEC_GAP for `{"status":"credited"}`
vs `{"ok":true}`, even though these are not cross-boundary contract fields.

**Severity:** Medium. Does not corrupt the primary classification path (SPEC_GAP and AGENT_DRIFT
for the real disagreements are unaffected), but produces a visible false alarm that undermines
classifier credibility at demo time.

**Mitigation:**
- The stub field list is a committed static enumeration in the fixture:
  `["charge_id", "refund_amount", "notification_contact"]` + HTTP status code.
  Internal response body keys (`status`, `ok`) are not in this list.
- The scope filter is a lookup, not a model judgment. The field list is version-pinned
  to the same commit as BRIEF.md.
- The negative control case (`OUT_OF_SCOPE`) is an explicit fixture pass criterion in
  EXPECTED-TRUTH.md. If the scope filter raises a SPEC_GAP for this, it is a fixture failure.
- Before the demo, run the scope filter against the internal body fields and confirm
  `OUT_OF_SCOPE` is returned.

---

## FM-04 — AGENT_DRIFT / SPEC_GAP confusion

**Failure:** The classifier conflates the two categories. Common failure patterns:
- Classifying `customer_identity` as `AGENT_DRIFT` (choosing a "winner" between email
  and account_id) when the source is silent — this invents a canon.
- Classifying `field_name` as `SPEC_GAP` when the brief explicitly says "refund_amount" —
  this ignores evidence of agent error.

Both errors corrupt the downstream routing: `AGENT_DRIFT` triggers an evidence-grounded repair
(correct for `field_name`), while `SPEC_GAP` triggers a human clarification request (correct for
`customer_identity`). Swapping them produces the wrong action on the wrong workstream.

**Severity:** High. Produces wrong outputs in both directions. The `SPEC_GAP → AGENT_DRIFT`
confusion is especially dangerous because it causes COLLIDER to "fix" something that was
actually a product decision, potentially overwriting valid agent work.

**Mitigation:**
- The classifier algorithm is explicit: Step 3 requires source evidence before `AGENT_DRIFT`
  can be returned. If source evidence is absent or ambiguous, `SPEC_GAP / UNKNOWN` is the
  required output.
- The AGENT_DRIFT classification must log the exact source passage that was contradicted.
  A logged evidence reference is a prerequisite for the classification, not a post-hoc note.
- Review `customer_identity` classification explicitly: confirm that no source passage names
  any of the two values (email / account_id) as canonical before classifying as `SPEC_GAP`.

---

## FM-05 — Canon patch not binding

**Failure:** After the human decides `account_id` and the canon patch is written, the repair
agent for the API workstream does not incorporate the patch. It re-runs with the original brief
as its only context and re-produces `email` as the identity field. The repair appears to succeed
but does not.

**Severity:** High. The most critical property of the system is that a human decision, once
made, durably changes what is built. If the patch is not binding, the entire canon/repair loop
is cosmetic.

**Mitigation:**
- The canon patch is passed explicitly as context to the repair agent, not as background
  information. The repair prompt must reference the patch directly and the agent must
  acknowledge it.
- Post-repair, the interpretation object for the repaired workstream is re-extracted and
  verified against the canon value before the run is marked complete.
- The test suite for the API workstream must include a test that exercises the `account_id`
  path. If the test passes after repair, it is evidence (not proof) that the patch was applied.

---

## FM-06 — Integration test not catching the semantic mismatch

**Failure:** The baseline local tests pass even though API uses `email` and Ledger uses
`account_id` for credit identity. Tests pass because each workstream is internally consistent —
no test checks cross-boundary identity agreement. This means the "everything looked green
locally" moment in the demo is literally true, and the tests provide no signal that anything
is wrong.

**Severity:** Medium (expected). This is actually the **correct** failure mode to demonstrate:
tests pass because each workstream is internally consistent, even though the system as a whole
has incompatible assumptions. The risk is that this looks like a test quality problem rather
than a specification gap.

**Mitigation:**
- Frame this explicitly in the demo: "Tests pass because each workstream is internally
  self-consistent. No test checks whether all three agree on what 'the customer' means."
- Do not fix the tests to catch the disagreement before the demo. The disagreement is the
  point. If the tests caught it, COLLIDER would not be needed.
- After repair, show that the cross-boundary inconsistency is resolved — not by adding a
  test that checks for it, but by showing that all three workstreams now reference the same
  canonical value.

---

## FM-07 — Human clarification ambiguity

**Failure:** The minimal clarification question is itself underspecified. The question
"Which field should identify the customer in the refund workflow?" could be answered in ways
that do not resolve the disagreement:
- "Use whatever is in the request" (not a decision)
- "It depends on context" (not a decision)
- "account_id for internal systems, email for external" (a decision that requires further
  decomposition — which system is API? which is Notifications?)

If the human answer is ambiguous, the canon patch cannot be written, and the run must remain
in `UNKNOWN` state.

**Severity:** Low for the demo fixture (the answer is scripted). Medium in production use,
where real human answers may be ambiguous.

**Mitigation:**
- For the demo, the clarification question and its answer are part of the fixture. The answer
  is unambiguous by design: `account_id`.
- The clarification question template should enumerate the candidate values observed and ask
  the human to select or specify. This constrains the answer space.
- If the answer is ambiguous, COLLIDER must not write a canon patch. It must return `UNKNOWN`
  and log the ambiguous answer as part of the evidence record. An ambiguous human answer is
  still a recorded artifact; it is just not a canon decision.
- The evidence record must distinguish between `SPEC_GAP (human decision pending)`,
  `SPEC_GAP (human answered, answer ambiguous)`, and `SPEC_GAP (resolved → canon patch written)`.

---

## Summary table

| ID | Failure | Severity | Primary mitigation |
|----|---------|----------|--------------------|
| FM-01 | Agent non-determinism produces wrong disagreements | Critical | Deterministic fixture; committed interpretation objects |
| FM-02 | Source retrieval failure misclassifies AGENT_DRIFT as UNKNOWN | High | Committed source documents; log evidence references |
| FM-03 | Scope filter error causes false SPEC_GAP (negative control) | Medium | Static committed stub field list; negative control is explicit fixture pass criterion |
| FM-04 | AGENT_DRIFT / SPEC_GAP confusion | High | Step 3 requires logged source passage before AGENT_DRIFT is returned |
| FM-05 | Canon patch not binding on repair agent | High | Explicit patch injection; post-repair interpretation re-extraction |
| FM-06 | Tests pass despite semantic mismatch (expected) | Medium (expected) | Frame as the demonstration, not a bug; do not fix pre-demo |
| FM-07 | Human clarification answer is ambiguous | Low (demo) / Medium (prod) | Fixture answer is scripted; production: enumerated choices, UNKNOWN if ambiguous |
