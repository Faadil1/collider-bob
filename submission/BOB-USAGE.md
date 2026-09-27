# IBM Bob Usage Statement

IBM Bob 2.0 was used as a load-bearing development agent during the implementation and refinement of COLLIDER.

Bob worked directly inside the project repository in GitHub Codespaces. Preserved Bob task evidence shows it reading the existing project state, creating and modifying project files, and contributing executable runtime and test work. The recorded session includes work on files such as `collider/__init__.py` and `tests/test_fixture.py`, and continued into a second preserved task after the first task reached its configured turn limit.

Bob's contribution was not limited to code generation. The build process used Bob to help shape and harden the system around specification-gap detection, agent-drift classification, correct abstention on unresolved ambiguity, dependency-aware repair, executable verification, and evidence/provenance discipline. Weak proof paths were deliberately rejected during development—for example, schema validity alone was not treated as evidence that workstreams behaved correctly.

The finished product now demonstrates an active Semantic CI loop: source-aware classification, one bounded human decision, decision compilation into specification/code/tests/memory, and a three-verdict future-change guard (`MERGE_BLOCKED`, `MERGE_ALLOWED`, `DECISION_REQUIRED`).

The provenance boundary is explicit. The canonical interpretation objects used in the comparative evidence are **PRESEEDED**, not live Bob-generated. The three future guard probes are controlled edits, not autonomous agents. Fresh-agent replay is **NOT_EXECUTED / PENDING_LIVE_BOB**.

That separation is intentional: COLLIDER treats provenance and uncertainty as product requirements, so the submission applies the same standard to its own IBM Bob claims.
