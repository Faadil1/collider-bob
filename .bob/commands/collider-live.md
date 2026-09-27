---
description: Run a provenance-bound live COLLIDER Semantic CI pass with isolated IBM Bob subagents
argument-hint: <run-id>
---
Switch to the `collider-semantic-ci` custom mode and activate the
`collider-semantic-review` skill.

Run the skill's **Live Bob protocol** using `$1` as the run id.

Requirements:
- spawn API, Ledger, and Notifications as independent Bob subagents;
- do not disclose sibling interpretations before each subagent returns;
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
