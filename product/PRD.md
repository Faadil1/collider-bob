# PRD — COLLIDER v0.1

## Problem
Parallel coding agents can independently make locally plausible decisions about identity, units, interfaces, ownership, idempotency, and other cross-boundary semantics. If the original specification never decided one of these questions, the disagreement can surface late as rework or system-level inconsistency.

## User
Tech lead / product engineer supervising parallel AI coding workstreams.

## Job to be done
When several coding agents interpret one task differently, identify whether the issue is an agent mistake or a missing decision in the specification, then resolve only what is necessary without redoing unrelated work.

## v0.1 workflow
1. ingest brief + repository fixture
2. Bob Plan decomposes task
3. independent workstreams emit structured interpretations
4. reconciler groups shared concepts and detects disagreement
5. evidence resolver compares each interpretation with source material
6. classifier returns AGENT_DRIFT, SPEC_GAP, or UNKNOWN
7. AGENT_DRIFT gets evidence-grounded repair
8. SPEC_GAP asks one minimal clarification
9. clarification becomes canon patch
10. impact router identifies dependent workstreams
11. only affected workstreams replan/repair
12. evidence run records baseline and COLLIDER outcomes

## Non-goals
- general semantic understanding of arbitrary repositories
- fully autonomous resolution of product ambiguity
- replacing Git merge
- replacing CI
- claiming correctness from model consensus
- production-grade distributed orchestration

## Success proof
A deterministic fixture demonstrates:
- at least one explicit AGENT_DRIFT
- at least one true SPEC_GAP
- at least one shared-but-INFERRED assumption
- at least one unaffected workstream preserved
- one negative path where COLLIDER returns UNKNOWN rather than inventing a canon.