# Problem Evidence

## Five-part canonical pattern

### Positive signal / opportunity
Parallel coding agents can execute multiple workstreams concurrently, creating major throughput potential.

### Concrete negative event
Mars Climate Orbiter was lost after English-unit data crossed an interface where metric units were required. NASA/JPL described a failure to recognize and correct an information-transfer error between teams. NASA engineering material identifies inadequate systems engineering, communications, and verification among contributing factors.

Sources:
- https://www.jpl.nasa.gov/news/mars-climate-orbiter-team-finds-likely-cause-of-loss/
- https://swehb.nasa.gov/spaces/7150/pages/16449723/SWE-017%2B-%2BProject%2Band%2BSoftware%2BTraining
- https://ntrs.nasa.gov/api/citations/20010005242/downloads/20010005242.pdf

### Observable impact
The spacecraft was lost. NASA technical material describes the mission as a $125M spacecraft.

### Design implication
Locally produced assumptions at a system boundary must not silently become shared reality merely because each component appears internally coherent.

### Product response
COLLIDER externalizes independent interpretations, compares them against source evidence, distinguishes AGENT_DRIFT from SPEC_GAP, preserves UNKNOWN, asks the minimum clarification required, commits a canon patch, and reroutes only affected work.

## Modern agent-specific evidence
CodeScout (Findings of ACL 2026) reports that AI software agents struggle with ambiguous problem statements lacking sufficient task context and requirements specification, and associates such ambiguity with longer trajectories, over-exploration, and repeated attempts.
Source: https://aclanthology.org/2026.findings-acl.2032/

## Claim boundary
Do not claim MCO was an AI-agent failure, that its interface specification was absent, that COLLIDER would have prevented it, or any unmeasured performance percentage.