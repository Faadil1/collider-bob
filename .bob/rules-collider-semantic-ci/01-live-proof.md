# COLLIDER Semantic CI mode execution rules

When this mode is active:

1. Load the `collider-semantic-review` skill before running a COLLIDER workflow.
2. Prefer the project MCP tools for semantic checks and provenance validation
   when the `collider-semantic-ci` MCP server is available.
3. A request for a **live Bob interpretation run** must spawn three independent
   subagents for API, Ledger, and Notifications. Do not silently replace the
   requested parallel run with parent-agent analysis.
4. Use `general` subagents when an interpretation requires reading workstream
   files and producing an artifact. Keep `fork_context` false unless explicitly
   necessary; sibling conclusions must never be passed across subagents.
5. Give all three agents the same authoritative brief, but only the files needed
   for their workstream.
6. Before spawning a live ambiguity probe for a concept already present in Bob
   decision memory, quarantine `.bob/rules/collider-decision-memory.md` from the
   workspace rule path into the run's transient `.collider/` directory. Record its
   SHA-256 before moving it. Because Bob workspace rules apply across modes, leaving
   this rule active would leak the canonical answer into the probe.
7. Spawn the three subagents only after the rule is absent from `.bob/rules/`.
   Keep `fork_context: false`, and never pass the parent agent's remembered canon
   into a subagent prompt. If any subagent cites the quarantined decision rule, the
   live probe is contaminated and must be rejected/rerun.
8. After all three independent interpretations have returned, restore the exact
   decision-memory rule byte-for-byte and verify its SHA-256 matches the pre-probe
   hash before DETECT, decision compilation, GUARD, or REPLAY continues.
9. Validate the resulting bundle with `collider_validate_live_bob` (MCP) or
   `python3 -m collider.bob_live validate` before COLLIDER consumes it.
10. Ask the human for a SPEC_GAP decision. Do not let Bob choose the canonical
    value on the human's behalf.
11. After an approved decision, export decision memory into Bob workspace rules.
12. Treat fresh-agent replay as a separate execution with a new independent Bob
    agent. Never infer replay success from the original run.
13. Preserve exact provenance in every judge-facing statement.
