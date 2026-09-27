# Rubric Map — IBM Bob 2.0 Hackathon

Canonical judge assurance: `product/JUDGE-PERFORMANCE-ASSURANCE.md`

## Application of Technology

What to show:
- Bob worked directly in the repository as a development agent.
- Bob session evidence demonstrates real file/runtime/test work.
- COLLIDER turns parallel-agent disagreement into a semantic-specification signal.
- The finished public product actively compiles decisions and guards future changes.

Truth boundary:
- canonical interpretations are PRESEEDED, not LIVE_BOB;
- guard probes are controlled changes, not agents;
- the public demo session itself does not execute replay;
- separate Bob evidence preserves Attempt 01 as REPLAY_FAIL (5/7) and proves Attempt 02 as a targeted-repair REPLAY_PASS (7/7);
- do not narrate Attempt 02 as an unconstrained first-try replay.

## Presentation

Judge memory sentence:

> **When AI agents disagree, COLLIDER finds the decision the specification forgot to make.**

Core sequence:

`green locally → 2 conflicts → AGENT_DRIFT vs SPEC_GAP → one decision → 2→0 → memory → three future verdicts`

Signature moment:

> **37/37 tests pass. COLLIDER returns DECISION_REQUIRED.**

## Business Value

Demonstrate mechanisms, not invented ROI:

- semantic mismatch caught before silent propagation;
- one bounded clarification instead of broad rework;
- only affected implementation repaired;
- resolved decisions become executable memory;
- compatible changes are allowed rather than blanket-blocked.

Do not claim unmeasured percentages or time savings.

## Originality

Do not claim invention of semantic merge, shared memory, contracts, or multi-agent review.

Differentiator:

`interpretation variation → implementation divergence → source-aware truth test → missing decision → executable decision memory → future semantic CI verdict`

The judge-facing distinction is the third verdict:
**DECISION_REQUIRED even when ordinary tests remain green.**
