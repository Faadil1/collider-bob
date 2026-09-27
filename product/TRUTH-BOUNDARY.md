# Truth Boundary

## States
### OBSERVED
Directly stated in trusted source material or proven by executable evidence.

### INFERRED
Plausible interpretation supported indirectly but not explicitly specified.

### UNKNOWN
Available evidence cannot support a unique conclusion.

### AGENT_DRIFT
An agent interpretation contradicts explicit source evidence.

### SPEC_GAP
The source material does not decide a cross-boundary question and multiple plausible interpretations remain.

## Required behavior
- AGENT_DRIFT may be repaired from evidence without inventing a new product decision.
- SPEC_GAP must not be auto-resolved as fact.
- UNKNOWN must remain visible.
- Agreement among agents is not proof; shared inference remains INFERRED unless source evidence upgrades it.
- Conflicting or stale evidence cannot be narrated as PASS.

## Agreement without authority (Semantic CI gate)
Registered in collider/concepts.py, applied identically to every concept:
- `BLOCK` — the question has already been raised (it diverged before). Later agreement does not close it; only canon does. Gate stays DECISION_REQUIRED.
- `DISCLOSE` — never yet diverged. Reported as a shared assumption: INFERRED, `upgrades_to_fact: false`, non-blocking, visible. The first disagreement makes it a SPEC_GAP.

## Guard verdicts
- `MERGE_BLOCKED` — contradicts explicit source or resolved canon.
- `MERGE_ALLOWED` — no semantic concept changed.
- `DECISION_REQUIRED` — the change exposes a decision nobody made. It is never called AGENT_DRIFT, because nothing was decided to drift from.

## Negative path
SPEC_GAP → UNKNOWN → HUMAN DECISION REQUIRED

Correct abstention is product success.