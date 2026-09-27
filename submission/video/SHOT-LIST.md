# COLLIDER: shot list

1920x1080, 30 fps, 1:51. The product window is 1600x900, placed at (160, 70) on a paper canvas. A chapter band sits above it and the caption band below.

Every shot is one of two things:

- **REC**: a segment of the real screen recording of the running product (`record.js`: CDP screencast plus a mouse/click/rect event log).
- **STILL**: a 3200x1800 screenshot captured during that same run once a state had settled. Stills are used only where the camera punches in beyond 1.3x.

Nothing on screen is mocked. The overlays are:

- stroke boxes and mono labels anchored to element rects logged by the recording;
- the cursor, replayed from the logged mouse path;
- the chapter band, the captions, the opening title and the end card.

Source was the `design/claude-uiux-pass` build (230e24a) running locally. The truth badge reads **LOCAL ACTIVE DEMO · PRESEEDED INTERPRETATIONS · INTERACTIVE HUMAN DECISION**. The public workers.dev URL could not be recorded from the build container because network egress to it is blocked. The end card shows that URL.

| # | Out (s) | Chapter | Source | Camera | Overlays | VO |
|---|---|---|---|---|---|---|
| 0 | 0.0–2.1 | — | Remotion title | — | COLLIDER · Semantic CI for AI agents | — |
| 1 | 1.8–4.4 | Detect | REC 0.2–2.8 | full frame; window wipes in | cursor | "Three workstreams…" |
| 2 | 4.4–10.5 | Detect | STILL detect-settled | push to the counters, then across to the chamber | `30 tests pass` (green), `3/3 green` (green), `2 integration conflicts` (crimson) | "Thirty tests pass… two conflicts." |
| 3 | 10.5–20.0 | Detect | STILL detect-settled | 1.75x on the customer_identity collision, then onto Notifications | `customer_identity: email vs account_id` (crimson), `Notifications: no customer_identity claim` (ink) | "Each workstream was locally right…" |
| 4 | 20.0–22.5 | Decide | REC 6.45–8.95 | full frame; the real Run click into DECIDE | cursor, click ripple | "COLLIDER checks each collision against the source." |
| 5 | 22.5–28.9 | Decide | STILL decide-settled | 1.45x on the AGENT_DRIFT strip, then onto the UNKNOWN plate | `AGENT_DRIFT: the brief decided` (crimson), `SPEC_GAP: the brief is silent` (chartreuse) | "Where the brief already decided…" |
| 6 | 28.9–38.9 | Decide | STILL decide-settled | 1.9x on the refund_amount repair; 1.8x on SOURCE SILENT; pull back to "Source authority ends here." | `refund_amount: repaired from source`, box on the source reading | "The brief names refund_amount… asks one question." |
| 7 | 38.9–47.0 | Decide → Compile | REC 12.3–20.4 | 1.3x on the decision panel, then full frame | `KEEP UNKNOWN: a valid abstention` (chartreuse), `Use account_id` (ink); real cursor moves to Keep, then commits Use account_id | "Keeping UNKNOWN is a valid answer…" / "That answer compiles." |
| 8 | 47.0–55.6 | Compile | STILL compile-settled | 1.55x walk down the canonical trace (spec patch → API/Ledger repair → regression contract → decision memory), then onto the result | `2 → 0` (green) | "The spec is patched… Two conflicts become zero." |
| 9 | 55.6–62.7 | Guard | REC 22.8–29.9 | full frame, then 1.15x on the bench | cursor clicks case A | "…email back. Tests fail…" |
| 10 | 62.7–63.9 | Guard | STILL guardA-p4 | 1.35x onto the counterfactual | box on "Without decision memory…" | "…decision memory blocks the merge." |
| 11 | 63.9–71.5 | Guard | REC 31.8–39.4 | full frame, then 1.15x on the bench | cursor clicks case B | "A wording change… Merge allowed." |
| 12 | 71.5–78.7 | Guard | REC 41.2–48.4 | full frame, then 1.2x on `37/37 · YET · DECISION REQUIRED` | cursor clicks case C | "Then Ledger switches to dollars…" |
| 13 | 78.7–84.0 | Guard | STILL guardC-p4 | 1.42x push on the bench, then onto the docket | none (the product already labels both sides) | "COLLIDER still returns decision required…" |
| 14 | 84.0–87.4 | Proof | STILL guardC-p4 | 2.0x on the truth badge | `PRESEEDED, and labelled` | "The demo data is preseeded…" |
| 15 | 87.4–91.1 | Proof | REC 51.6–55.3 | full frame; the real Proof drawer opens | cursor | "Separately, IBM Bob ran the protocol live…" |
| 16 | 91.1–96.2 | Proof | STILL proof-provenance | 1.55x on the LIVE_BOB section | `Separate LIVE_BOB run` | (same line), then "The first replay…" |
| 17 | 96.2–99.8 | Proof | STILL replay-rail | 2.4x on the rail: `01 FAIL 5/7`, `02 TARGETED PASS 7/7` | box on the replay block | "…five of seven… seven of seven." |
| 18 | 99.8–104.0 | Close | REC 67.3–71.5 | full frame; back to Active | cursor | "COLLIDER is semantic CI for AI agents." |
| 19 | 104.0–111.0 | Close | STILL guardC-p4 + Remotion end card | window scales to 0.56 and moves right | COLLIDER · Semantic CI for AI agents · MERGE_BLOCKED / MERGE_ALLOWED / DECISION_REQUIRED · live URL · repo | "When agents disagree…" |

## Truth boundary, as shown

- The demo interpretations are **PRESEEDED**. The film says so (shot 14) and the product badge shows it.
- LIVE_BOB is presented only as a **separate** evidence run (`live-bob-2026-09-27-01`, shots 15–17).
- Attempt 01 is shown as a failure (`FAIL 5/7`). Attempt 02 is shown as **targeted** (`TARGETED PASS 7/7`), never as a first-try success.
- Guard cases A/B/C are the product's controlled future changes. The VO calls them "a future change" and "a wording change", not agents.
- Every number on screen is read from the running product: 30, 3/3, 2, 2 → 0, 37/37, 5/7, 7/7.
