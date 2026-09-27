# COLLIDER truth boundary for IBM Bob

These rules apply to every Bob conversation in this workspace.

1. Never call PRESEEDED, SIMULATED, LOCAL, or LOCAL_STUB evidence LIVE_BOB.
2. Never promote consensus into source authority.
3. If the source is silent and plausible implementations disagree, preserve
   SPEC_GAP / UNKNOWN and request the minimum human decision.
4. If the source explicitly decides a concept and an implementation disagrees,
   classify AGENT_DRIFT and cite the exact source evidence.
5. Controlled guard probes are not autonomous agents.
6. A fresh-agent replay is only proven when a new independent Bob agent actually
   executes the replay contract.
7. Do not overwrite committed canonical evidence. New live proof gets a new run
   id and immutable evidence directory.
8. Before changing a concept with an existing COLLIDER decision rule, read
   `.bob/rules/collider-decision-memory.md` if it exists and run the semantic
   guard rather than silently violating canon.
