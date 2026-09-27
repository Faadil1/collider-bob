# Public Repository Hygiene & Privacy Audit — 2026-09-27

## Scope

Audit target:
`Faadil1/collider-bob`
branch:
`claude/sharp-planck-vfqz40`

Goal:
keep the submission repository limited to COLLIDER product, implementation,
evidence, deployment, demo, and hackathon-submission material.

## Current-tree review

The branch tree was reviewed for unrelated project folders/files and obvious
private-research leakage.

No current-tree material was identified for unrelated personal work such as:

- STO work / dashboards / internal transport research
- job applications, CVs, salary or interview material
- Wealth Decoded
- TRACE / Valid Until / Callsheet / Carry One or other unrelated builds
- personal phone/address material
- unrelated private research notes

Targeted repository searches also returned no matches for representative private
terms such as:

- `8192826953`
- `Gatineau`
- `Canada Revenue Agency`
- `Spellbook`
- `Zensurance`
- `Avida`
- `salary`
- `resume`
- `STO marketing`
- `Wealth Decoded`

Searches for short substrings such as `STO` or `TRACE` produced only false
positives inside ordinary words such as "stored", "story", or "traceable".

No repository-content match was found for the user's Yahoo address/name string in
the targeted search.

## Cleanup performed

Removed obsolete generated test evidence under:

`evidence/runs/test-run/`

The current test suite already writes its test pipeline output to a temporary
directory and explicitly excludes `evidence/` from collection, so the committed
`test-run` directory was redundant submission noise.

Canonical evidence was not removed.

## Content intentionally retained

These areas are submission-relevant and remain:

- `product/` — product decisions, truth boundary, technical/judge gates
- `evidence/` — canonical proof, runtime receipts, incident transparency
- `demo/` and `demo-ui/` — demo narrative and product surface
- `state/` — canonical current/handover state
- `submission/` — submission copy
- implementation/tests/deployment files

Historical invalid/failed COLLIDER evidence is retained when it documents an
actual project failure or correction; it is relevant to evidence integrity, not
private research.

## Important limitation

This audit covers the **current branch tree and targeted searchable repository
content**. It is not a cryptographic proof that no unrelated text ever existed in
any historical Git commit.

Git commit author metadata is also separate from repository file contents. If
history-level removal or author-email rewriting is ever required, that is a
separate destructive history-rewrite operation and should not be done casually
before submission.

## Verdict

**CURRENT SUBMISSION TREE: CLEAN FOR PUBLICATION**

No unrelated private research was detected in the current submission tree, and
obsolete generated test artifacts were removed.
