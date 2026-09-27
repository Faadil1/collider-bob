# Submission Snapshot — 2026-09-27

This file records the repository/runtime state that existed at the hackathon
submission deadline.

## Submitted repository snapshot

- Archive branch: `archive/submission-deadline-2026-09-27`
- Commit: `a909a682f1b033e41b1e1ef312dffbe24005af67`
- UI/UX merge parent: `91795b67dc8dfeec51e485ec7cea8ada0bace60c`
- Test verification before deployment: `271 passed, 123 subtests passed`
- TypeScript: clean

## Public runtime observed after deployment

- URL: https://collider-semantic-ci.faadil-casecraft.workers.dev/
- Worker version: `453a881f-3b9a-4065-b65b-25b3b2ffa369`
- execution_environment: `CLOUDFLARE_CONTAINER`
- interpretation_source: `PRESEEDED`
- human_decision_source: `INTERACTIVE_WEB`
- polished UI markers observed publicly:
  - `Source authority ends here.`
  - `Bob replay evidence`
  - `field_name`

## Bob truth boundary at submission

- comparative public fixture interpretations: PRESEEDED
- separate live Bob run: OBSERVED with three isolated Bob subagents
- replay Attempt 01: REPLAY_FAIL, 5/7, preserved
- replay Attempt 02: TARGETED_REPAIR_REPLAY, REPLAY_PASS, 7/7
- guard probes: controlled future changes, not autonomous agents

## Post-submission change policy

Changes after this snapshot should be limited to:

- README/documentation clarity;
- evidence indexing/archival;
- screenshots, slides and walkthrough media;
- explicit corrections of stale documentation.

Do not add or materially alter product functionality and then present it as part
of the submitted build.

Any replacement walkthrough should be labelled as **post-submission presentation
material demonstrating the same submitted build**.
