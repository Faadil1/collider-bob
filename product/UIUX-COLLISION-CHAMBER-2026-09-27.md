# COLLIDER UI — The Collision Chamber (2026-09-27)

Pre-final judge-facing redesign of `demo-ui/`, executed against
`product/CLAUDE-UIUX-HANDOFF-2026-09-27.md`. Visual / interaction / comprehension
only: no API, runtime, evidence or semantic change.

## Concept

The interface is a **collision chamber** feeding a **decision instrument** feeding a
**semantic court**. The mechanism is drawn as information, not decoration:

| Step | What the judge sees before reading |
|---|---|
| 01 DETECT | `30` / `3/3` in green, a rule reading **BUT**, `2` in crimson. Beside it, API (ultramarine) and Ledger (orange) trajectories braid and hit twice — `customer_identity` and the money field — before the integration wall. Notifications runs alone, dashed, "not a party". Two conflicts = two visible collision points. |
| 02 DECIDE | The collision becomes a reading: API `email`, LEDGER `account_id`, SOURCE `SILENT` (dashed empty slot, quoted brief). Both trajectories converge into a chartreuse **UNKNOWN** plate with a ruled measurement field — "the boundary of current authority". Two equal outcome slabs: **USE account_id** (ink, commit) and **KEEP UNKNOWN** (chartreuse, hold). AGENT_DRIFT and SHARED ASSUMPTION sit below as secondary strips. |
| 03–06 COMPILE | A vertical canonical trace grows from the human answer through seven diamond stations. `2` shrinks and is struck; `0` lands in green. Lanes show the canon reaching only API and Ledger (trajectory colour feeding into ink); Notifications stays untouched. Decision memory is a sealed ink artifact. |
| 07 GUARD | A three-case docket (A/B/C) above a bench split in two: **CONVENTIONAL CI** (test count) and **SEMANTIC CI** (verdict), joined by **YET** or **AND**. The signature frame: `37/37 ALL TESTS PASS` — YET — `DECISION REQUIRED`. The change card shows the diff "judged against" the decision-memory slab; a restore band winds back to verified bytes. |

## Colour roles (each colour means one thing)

- ultramarine — API trajectory · orange — Ledger trajectory · graphite — Notifications
- crimson — collision, AGENT_DRIFT, MERGE_BLOCKED, failed tests
- chartreuse — UNKNOWN, SPEC_GAP, DECISION_REQUIRED, KEEP UNKNOWN (the "nobody decided" colour)
- green — OBSERVED, verified, MERGE_ALLOWED, passing tests
- ink — canon, decision memory, chrome

## Type

Self-hosted (CSP `font-src 'self'`), OFL-licensed, licences in `demo-ui/fonts/`:
Archivo variable (width 62–125 %) for display and verdicts; IBM Plex Mono for data.

## Motion grammar

Each movement explains a cause, runs once, and never loops:
trajectories draw in independently → collision nodes impact → readings stagger →
convergence lines draw → UNKNOWN plate mask-wipes in → decision panel rises;
canonical trace fills per compiled step → 2 collapses, 0 lands → memory seals;
guard: change card highlighted → conventional CI answers → semantic verdict
mask-reveals → restore band rewinds → restored.
`prefers-reduced-motion: reduce` disables every animation and transition and shows
each end state immediately (guard jumps to the restored frame).

## Truth boundary in the UI

- Truth badge unchanged (LOCAL/CLOUDFLARE ACTIVE DEMO · PRESEEDED · INTERACTIVE).
- Rail replay block: *this session: NOT EXECUTED* separated from *separate LIVE_BOB
  evidence run: attempt 01 REPLAY_FAIL 5/7 · attempt 02 targeted-repair REPLAY_PASS 7/7*.
- Proof → Provenance and Evidence → Truth Boundary cite `live-bob-2026-09-27-01`
  as a separate run and state that this demo's interpretations are PRESEEDED.
- Guard copy calls the probes "controlled future changes, not autonomous agents".

## Validation (local runtime, Chromium)

- Desktop 1440×900 and 1366×768: every state of DETECT → DECIDE → COMPILE → GUARD
  (all three verdicts), KEEP UNKNOWN, EVIDENCE MODE and the proof drawer fit with no
  document scroll; zero console / CSP errors.
- Mobile 390×844: no horizontal overflow in any state; vertical trajectories; sticky
  action bar; proof as bottom sheet.
- Reduced motion: full flow completes with all end states visible.
- `python3 -m pytest -q -p no:cacheprovider`: 271 passed, 123 subtests passed.
- `npx tsc --noEmit`: clean.

Not yet observed on the public Cloudflare runtime; that requires deploying this branch.
