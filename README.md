# COLLIDER — Disagreement-Driven Specification Repair for Parallel AI Agents

COLLIDER is a hackathon project for the IBM Bob 2.0 Hackathon.

## Thesis

Parallel coding agents can each make locally valid choices while silently interpreting an underspecified requirement in incompatible ways.

COLLIDER turns those disagreements into evidence of missing product or architectural decisions.

**Core loop**

`Bob Plan → independent subagents → interpretations → disagreement classification → spec gap / agent drift → minimal clarification → canon patch → targeted repair`

## Truth boundary

COLLIDER never upgrades uncertainty into truth.

- **OBSERVED** — explicitly supported by source material or executable evidence.
- **INFERRED** — a plausible interpretation not explicitly specified.
- **UNKNOWN** — evidence is missing, stale, or conflicting.
- **AGENT_DRIFT** — an agent contradicts explicit source evidence.
- **SPEC_GAP** — multiple plausible interpretations exist because the source never decided the question.

If evidence is insufficient, COLLIDER must abstain or request clarification rather than invent a canon.

## Real-failure anchor

The project is grounded in a concrete class of systems failure: the Mars Climate Orbiter was lost after English-unit data crossed an interface that expected metric units. NASA/JPL emphasized that the critical failure was not merely the initial error but the failure of systems engineering and verification processes to detect it before mission loss.

This project does **not** claim COLLIDER would have prevented that historical incident. The incident is used only as evidence that locally produced, cross-boundary assumptions can become globally destructive when they are not reconciled.

Primary sources:
- https://www.jpl.nasa.gov/news/mars-climate-orbiter-team-finds-likely-cause-of-loss/
- https://ntrs.nasa.gov/api/citations/20010005242/downloads/20010005242.pdf

Modern agent evidence:
- CodeScout (ACL 2026) reports that ambiguous software-engineering requests lacking sufficient context/specification are associated with longer, less effective agent trajectories:
  https://aclanthology.org/2026.findings-acl.2032/

## Canonical build rules

- Real failure > fake success.
- Every major claim must map to demonstration + receipt.
- Preserve failures in the evidence record.
- Include a negative path: REFUSE / ABSTAIN / REVIEW / UNKNOWN.
- No read-only default for creative ideation or normal agent execution.
- Deadline pressure constrains sequencing, not concept ambition.
- Requirements ↔ evidence ↔ artifacts ↔ runtime ↔ project state must agree before completion is claimed.

## Status

**Concept:** locked for technical reality check  
**Competitive novelty:** passed provisionally; continue monitoring  
**Runtime:** not implemented  
**Evidence run:** not yet executed  
**Submission claims:** not yet earned

See `state/CURRENT.yaml` after the foundation pack lands.
