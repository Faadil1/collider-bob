---
description: Run a provenance-bound live COLLIDER Semantic CI pass with isolated IBM Bob subagents
argument-hint: <run-id>
---
Switch to the `collider-semantic-ci` custom mode and activate the
`collider-semantic-review` skill.

Run the skill's **Live Bob protocol** using `$1` as the run id.

Requirements:
- use Bob Plan mode first to create a scope-only decomposition; Plan must not
  choose source-silent semantic values;
- before spawning probes for `customer_identity`, quarantine
  `.bob/rules/collider-decision-memory.md` into
  `.collider/bob-live/$1/quarantine/`, record its SHA-256, and confirm the rule
  is absent from `.bob/rules/`; the pre-existing PRESEEDED canon must not leak
  into the ambiguity probe;
- return to COLLIDER mode and spawn API, Ledger, and Notifications as independent
  `general` Bob subagents with `fork_context: false`;
- do not disclose sibling interpretations or the parent's remembered canonical
  value before each subagent returns;
- reject/rerun the probe if any subagent cites the quarantined decision-memory rule;
- after all three subagents return, restore the rule byte-for-byte and verify its
  SHA-256 before DETECT;
- record the real parent Bob session reference and each real task-summary reference;
- save only genuine LIVE_BOB interpretation objects under
  `.collider/bob-live/$1/interpretations/`;
- validate them with `collider_validate_live_bob` or
  `python3 -m collider.bob_live validate` before COLLIDER consumes them;
- run DETECT first with no human decision;
- if a SPEC_GAP appears, ask me the minimum clarification instead of choosing;
- after my answer, compile the decision from the same validated LIVE_BOB bundle
  using `collider.decision_compiler` with `INTERACTIVE_BOB`,
  `LIVE_BOB`, the real session ref, and a new immutable workspace/receipt dir;
- export that resulting decision memory into Bob workspace rules with
  `collider_export_decision_rule` or `python3 -m collider.bob_rules`;
- finish by showing the receipt paths and exact truth boundary.

Do not create or reconstruct screenshots. I will capture the real Bob task/session
summary and parallel-subagent panel from the UI.
