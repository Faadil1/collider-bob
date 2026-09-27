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

## Screenshot archive slots

The original screenshots currently live in the working conversation evidence pool.
When their image files are exported, place them here without alteration:

```text
evidence/bob-sessions/screenshots/
  J1-quarantine-original.<ext>
  J2-three-subagents-original.<ext>
  J3-live-bob-spec-gap-original.<ext>
  J4-interactive-decision-original.<ext>
  J5-replay-attempt-01-fail-original.<ext>
  J6-replay-attempt-02-pass-original.<ext>
```

Then append, for each file:

```text
filename:
sha256:
captured_from: original Bob/Codespaces screen
content_summary:
```

Do not fabricate these filenames or hashes before the original image files are
actually archived.
