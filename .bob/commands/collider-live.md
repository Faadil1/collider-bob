---
description: Run a provenance-bound live COLLIDER Semantic CI pass with isolated IBM Bob subagents
argument-hint: <run-id>
---
Switch to the `collider-semantic-ci` custom mode and activate the
`collider-semantic-review` skill.

Run the skill's **Live Bob protocol** using `$1` as the run id.

Requirements:
- use Bob Plan mode first to create a scope-only decomposition; do not let Plan
  choose source-silent semantic values;
- return to COLLIDER mode and spawn API, Ledger, and Notifications as independent
  `general` Bob subagents with `fork_context: false`;
- do not disclose sibling interpretations before each subagent returns;
- record the real parent Bob session reference and each real task-summary reference;
- save only genuine LIVE_BOB interpretation objects under
  `.collider/bob-live/$1/interpretations/`;
- run `python3 -m collider.bob_live validate` before COLLIDER consumes them;
- run DETECT first with no human decision;
- if a SPEC_GAP appears, ask me the minimum clarification instead of choosing;
- after my answer, compile the decision from the same validated LIVE_BOB bundle
  using `collider.decision_compiler` with `INTERACTIVE_BOB`,
  `LIVE_BOB`, the real session ref, and a new immutable workspace/receipt dir;
- export that resulting decision memory into Bob workspace rules with
  `python3 -m collider.bob_rules`;
- finish by showing the receipt paths and exact truth boundary.

Do not create or reconstruct screenshots. I will capture the real Bob task/session
summary and parallel-subagent panel from the UI.
