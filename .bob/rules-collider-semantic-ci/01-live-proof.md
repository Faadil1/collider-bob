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
6. Validate the resulting bundle with `collider_validate_live_bob` (MCP) or
   `python3 -m collider.bob_live validate` before COLLIDER consumes it.
7. Ask the human for a SPEC_GAP decision. Do not let Bob choose the canonical
   value on the human's behalf.
8. After an approved decision, export decision memory into Bob workspace rules.
9. Treat fresh-agent replay as a separate execution with a new independent Bob
   agent. Never infer replay success from the original run.
10. Preserve exact provenance in every judge-facing statement.
