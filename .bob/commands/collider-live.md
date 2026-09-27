---
description: Run a provenance-bound live COLLIDER Semantic CI pass with isolated IBM Bob subagents
argument-hint: <run-id>
---
Switch to the `collider-semantic-ci` custom mode and activate the
`collider-semantic-review` skill.

Run the skill's **Live Bob protocol** using `$1` as the run id.

Requirements:
- before spawning probes for `customer_identity`, quarantine
  `.bob/rules/collider-decision-memory.md` into
  `.collider/bob-live/$1/quarantine/`, record its SHA-256, and confirm the rule is
  absent from `.bob/rules/`; this prevents the pre-existing PRESEEDED canon from
  contaminating the ambiguity probe;
- spawn API, Ledger, and Notifications as independent Bob subagents only after that
  quarantine is active;
- keep `fork_context: false` and do not disclose sibling interpretations or the
  parent agent's remembered canonical value before each subagent returns;
- reject/rerun the probe if any subagent cites the quarantined decision-memory rule;
- after all three subagents return, restore the rule byte-for-byte and verify its
  SHA-256 before running DETECT;
- record the real parent Bob session reference and each real task-summary reference;
- save only genuine LIVE_BOB interpretation objects under
  `.collider/bob-live/$1/interpretations/`;
- run `python3 -m collider.bob_live validate` before COLLIDER consumes them;
- run DETECT first with no human decision;
- if a SPEC_GAP appears, ask me the minimum clarification instead of choosing;
- after my answer, run the resolved path in a new immutable transient directory;
- export resulting decision memory into Bob workspace rules with
  `python3 -m collider.bob_rules`;
- finish by showing the receipt paths and exact truth boundary.

Do not create or reconstruct screenshots. I will capture the real Bob task/session
summary and parallel-subagent panel from the UI.
