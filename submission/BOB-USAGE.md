# IBM Bob Usage Statement

IBM Bob 2.0 was used as a load-bearing development agent during the implementation and refinement of COLLIDER.

Bob worked directly inside the project repository in GitHub Codespaces. The recorded Bob session shows it reading the existing project state, modifying the COLLIDER runtime, and writing project files including `collider/__init__.py` and `tests/test_fixture.py`. The session also produced and refined executable logic around specification-gap detection, agent-drift classification, abstention on unresolved ambiguity, impact routing, evidence generation, and fixture verification.

A major part of Bob's contribution was evidence hardening. During the build, the project deliberately rejected weaker proofs. For example, schema validation alone was not accepted as evidence that individual workstreams behaved correctly. The implementation was subsequently hardened around executable API, Ledger, and Notifications behavior, explicit dependency routing, negative controls, targeted repair, and provenance fields.

Bob was also used iteratively across two preserved tasks in the same `collider-bob` workspace. The second task continued from the first after the configured session turn limit was reached rather than restarting the project.

The canonical comparative runtime evidence is intentionally not described as LIVE_BOB. Its interpretation objects and human decision are PRESEEDED and the execution is LOCAL. Bob assisted with the development and verification of the system, but the canonical runtime evidence does not claim that live Bob subagents generated those canonical interpretations.

This separation is deliberate: COLLIDER treats provenance and uncertainty as product requirements, so the submission applies the same standard to its own IBM Bob usage claims.
