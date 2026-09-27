# IBM Bob Usage Statement

IBM Bob 2.0 was used as a load-bearing development agent during the implementation and refinement of COLLIDER.

Bob worked directly inside the project repository in GitHub Codespaces. Preserved Bob task evidence shows it reading the existing project state, creating and modifying project files, and contributing executable runtime and test work. The recorded session includes work on files such as `collider/__init__.py` and `tests/test_fixture.py`, and continued into a second preserved task after the first task reached its configured turn limit.

Bob's contribution was not limited to code generation. The build process used Bob to help shape and harden the system around specification-gap detection, agent-drift classification, correct abstention on unresolved ambiguity, dependency-aware repair, executable verification, and evidence/provenance discipline. Weak proof paths were deliberately rejected during development—for example, schema validity alone was not treated as evidence that workstreams behaved correctly.

The finished product now demonstrates an active Semantic CI loop: source-aware classification, one bounded human decision, decision compilation into specification/code/tests/memory, and a three-verdict future-change guard (`MERGE_BLOCKED`, `MERGE_ALLOWED`, `DECISION_REQUIRED`).

COLLIDER also ships as a native Bob project capability. The repository contains a project custom mode (`.bob/custom_modes.yaml`), a reusable `collider-semantic-review` skill, workspace truth-boundary and decision-memory rules, a project-level MCP server (`.bob/mcp.json`) exposing COLLIDER as native Bob tools, a LIVE_BOB provenance validator, and an exporter that turns approved COLLIDER decision memory into Bob workspace rules. The live protocol is designed to spawn isolated Bob subagents for API, Ledger, and Notifications, validate their session-bound interpretation artifacts, then feed those exact artifacts into the normal COLLIDER pipeline. Bob can also call COLLIDER's gate, PR gate, decision memory, live-input validator, rule exporter, and replay evaluator through MCP. These mechanisms are implemented and covered by the repository test suite.

The remaining proof boundary is empirical: until a real Bob task/session executes that protocol and its Task Session Summary/subagent evidence is captured, no new interpretation run is called LIVE_BOB.

The provenance boundary is explicit. The canonical interpretation objects used in the comparative evidence are **PRESEEDED**, not live Bob-generated. The three future guard probes are controlled edits, not autonomous agents. Fresh-agent replay is **NOT_EXECUTED / PENDING_LIVE_BOB**.

That separation is intentional: COLLIDER treats provenance and uncertainty as product requirements, so the submission applies the same standard to its own IBM Bob claims.
