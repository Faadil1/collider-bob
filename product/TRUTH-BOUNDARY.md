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

## Negative path
SPEC_GAP → UNKNOWN → HUMAN DECISION REQUIRED

Correct abstention is product success.