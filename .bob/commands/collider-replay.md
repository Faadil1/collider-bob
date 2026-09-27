---
description: Run the fresh-agent replay proof for a resolved COLLIDER decision
argument-hint: <compiled-workspace> <session-ref>
---
Use the COLLIDER Semantic CI mode and skill.

Run a **fresh independent Bob agent** against the patched specification and
decision rule from `$1`.

Withhold:
- the repaired implementation files;
- repair.patch;
- the canonical value as an explicit prompt answer.

The fresh agent must derive the value from the patched specification / workspace
decision rule, produce a new implementation and interpretation, and run the
regression contract.

Record the real Bob session/task references and construct a replay result only
from actual execution. Evaluate it with `collider.replay`.

Do not mark REPLAY_PASS unless:
- execution_source is LIVE_BOB_SESSION;
- the required provenance fields are present;
- emitted_value matches canon;
- tests_passed is true.

If any condition is missing, preserve NOT_EXECUTED or REJECTED.
