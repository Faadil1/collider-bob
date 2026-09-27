# Bob Judge Evidence Manifest — 2026-09-27

Purpose: select a small, judge-readable proof set from the larger authentic Bob
evidence pool while preserving every raw artifact.

## Evidence policy

- Keep **all** original screenshots, transcripts, receipts, hashes, and failed attempts.
- Never reconstruct or redraw a Bob screenshot and present it as execution evidence.
- Judge-facing media should use only original captures from the real sessions.
- Do not hide Attempt 01. Its failure is part of the integrity story.
- The public demo's built-in comparative interpretations are PRESEEDED.
- `live-bob-2026-09-27-01` is the separately observed LIVE_BOB run.
- Attempt 02 is a **targeted-repair replay** under a general minimal-change /
  preserve-public-interface instruction; never call it an unconstrained first try.

## Judge-facing shortlist

Target: **4–6 screenshots maximum** in the submission/video. Use the original
captures already preserved in the working evidence pool.

| ID | What the original screenshot must show | Why it matters | Use |
|---|---|---|---|
| J1 | decision-memory quarantine SHA-256 + rule absent from `.bob/rules/` before probe spawn | proves the known canon was prevented from leaking into live probes | backup / deep proof |
| J2 | three independent Bob subagents completed + contamination check CLEAN | proves the ambiguity inputs came from real isolated Bob execution | primary |
| J3 | LIVE_BOB validation + `customer_identity = SPEC_GAP / UNKNOWN` + minimal human question | strongest Bob-native signature moment: real agents disagree and COLLIDER refuses to invent authority | **primary hero proof** |
| J4 | interactive human decision recorded as `human_decision_source=INTERACTIVE` + resolved path / zero conflicts / MERGE_ALLOWED | closes ambiguity → decision → compiled canon | primary |
| J5 | Attempt 01 `REPLAY_FAIL`, 5 passed / 2 failed, with compatibility regression visible | demonstrates that the replay gate is real and failures are preserved | optional integrity proof |
| J6 | Attempt 02: fresh Bob task derives `account_id`, preserved signature, then holdout `7 passed` + `REPLAY_PASS` | proves targeted future-agent convergence from decision memory | **primary replay proof** |

Recommended video sequence: **J3 → J4 → J6**.  
Recommended README/submission gallery if space permits: **J2 → J3 → J4 → J5 → J6**.

## Raw evidence that should remain archived but normally not shown to judges

- duplicate terminal captures of the same JSON object;
- long unscrolled interpretation dumps;
- intermediate TODO-list screens;
- Bobcoin dashboard (useful audit evidence, not central product proof);
- CLI/help debugging;
- failed slash-command discovery;
- raw receipt sections containing stale historical scaffold wording;
- the root `collider_gate` mismatch observed before its canon-path issue was understood;
- screenshots whose only value is setup rather than mechanism proof.

## Canonical machine evidence

LIVE_BOB:
- `evidence/bob-sessions/LIVE-BOB-2026-09-27-01.md`
- session ref: `e6b660eb207144f0953d24bbc49f2a87`
- bundle SHA-256: `56921cc86b212bf8c2c52677cdf43fd99961ca39c9b7890169e760b33fa3a438`

Replay Attempt 01:
- `evidence/bob-sessions/FRESH-REPLAY-ATTEMPT-01-2026-09-27.md`
- task id: `4100558a9ec3bb56296149a8388af980`
- verdict: `REPLAY_FAIL`
- holdout: 5 passed / 2 failed

Replay Attempt 02:
- `evidence/bob-sessions/FRESH-REPLAY-ATTEMPT-02-2026-09-27.md`
- task id: `9a6ec967e19713910d16b99184b15307`
- verdict: `REPLAY_PASS`
- holdout: 7 passed / 0 failed
- receipt SHA-256: `ed623331edefb259ffc7047a98f3091fd0a0ac0d94566c927c4d4f9da71a12c0`

## Archived screenshot pool

The following authentic originals are committed under `evidence/bob-sessions/screenshots/`.
They were copied byte-for-byte from the captured run evidence and SHA-256 verified before archive commit
`8e336c8e344d712749b4a886fae349630afc7c4c`.

| ID | File | SHA-256 | Status |
|---|---|---|---|
| J1 | [J1-quarantine-original.png](screenshots/J1-quarantine-original.png) | `d5fb5f64182aced3b1d6870a0834b4a5bf2023e81dbd1e9687b922a262b8e631` | AUTHENTIC_ORIGINAL |
| J2 | [J2-three-subagents-original.png](screenshots/J2-three-subagents-original.png) | `d522c3f2b38650912a42ee0c028fe40c90ddbde96fea44b2f943305c9fcdc06a` | AUTHENTIC_ORIGINAL |
| J3 | [J3-live-bob-spec-gap-original.png](screenshots/J3-live-bob-spec-gap-original.png) | `9cdd0922c1da3394b62d89116c5f344a8a71fb475f18028f50458e0753955d20` | AUTHENTIC_ORIGINAL |
| J4 | [J4-interactive-decision-original.png](screenshots/J4-interactive-decision-original.png) | `9c1736f1961f8a2e9ea0da32b22e48cacc65b88f051325948acae52b4306b848` | AUTHENTIC_ORIGINAL |

### Replay screenshot limitation

No authentic J5/J6 image files were found in the accessible captured-image pool during the final seal.
They are therefore **not reconstructed, redrawn, or fabricated**.

Replay proof remains machine-verifiable in:

- [Attempt 01 — REPLAY_FAIL, 5 passed / 2 failed](FRESH-REPLAY-ATTEMPT-01-2026-09-27.md)
- [Attempt 02 — TARGETED_REPAIR_REPLAY, REPLAY_PASS, 7/7](FRESH-REPLAY-ATTEMPT-02-2026-09-27.md)

This is a visual-packaging limitation, not a missing replay execution claim.
