# Problem & Solution

## Problem

Parallel AI coding agents can each produce locally valid implementations while silently making different choices about requirements the shared specification never decided.

Those disagreements may not appear as Git conflicts, syntax errors, or failing unit tests. In COLLIDER's canonical fixture, all 30 local tests pass and all three workstreams are green, yet integration reveals two incompatible assumptions.

The important part is that the two mismatches have different causes.

One is **AGENT_DRIFT**: the source explicitly says `refund_amount`, but Ledger implemented `credit_amount`.

The other is a **SPEC_GAP**: API uses `email`, Ledger uses `account_id`, and the source never chose a canonical customer identity.

Treating both as generic failures loses the most useful information.

## Solution

COLLIDER is **Semantic CI for Agentic Software Development**.

It uses independent implementation interpretations as ambiguity probes. For every disagreement, it checks source authority and separates:

- **AGENT_DRIFT** — the specification already decided the question, so the implementation is repaired from evidence.
- **SPEC_GAP / UNKNOWN** — multiple implementations remain plausible because the specification never decided, so COLLIDER refuses to invent the answer and asks one bounded human question.

When the human selects `account_id`, COLLIDER compiles that decision into a specification patch, targeted code repair, regression contract, and decision memory. The executable integration moves from **2 conflicts to 0** and becomes `SEMANTICALLY_READY`.

Then the second act begins.

COLLIDER judges future changes against decision memory with three verdicts:

- **MERGE_BLOCKED** when a change violates resolved canon.
- **MERGE_ALLOWED** when the semantic change is harmless.
- **DECISION_REQUIRED** when all tests may still pass but the change exposes a new source-silent decision.

The signature example changes Ledger from cents to dollars: **37/37 tests pass**, yet COLLIDER returns `DECISION_REQUIRED`.

That is the core idea: tests can say pass or fail; COLLIDER adds a third answer — **nobody decided this yet**.

The comparative fixture interpretation evidence remains PRESEEDED. Separately, a real
LIVE_BOB run with three isolated Bob subagents reproduced the source-silent
`customer_identity` ambiguity and stopped for an interactive human decision. A
fresh-agent replay then preserved an authentic first failure before a second,
targeted minimal-change replay passed the withheld regression contract 7/7. No
unmeasured time-saving or percentage-productivity claim is made.
