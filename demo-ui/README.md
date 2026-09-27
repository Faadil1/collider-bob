# COLLIDER Demo UI

Evidence-first static demo surface.

## Generate canonical demo data

    python3 demo-ui/build_demo_data.py

## ACTIVE MODE (default)

    python3 demo-ui/server.py

Serves the UI at 127.0.0.1:4173 with bounded local actions:

    GET  /api/state    gate on the committed tree
    POST /api/decide   {"choice": "USE_ACCOUNT_ID" | "KEEP_UNKNOWN"}
    POST /api/guard    {"decision_id": "<session id from USE_ACCOUNT_ID>",
                        "probe": "IDENTITY_REVERT" | "COMPATIBLE_CHANGE" | "MONEY_UNIT_DRIFT"}
    GET  /api/gate?decision=<session id>

No HTTP input carries values or paths. Every action writes only to the
git-ignored `.collider/workspaces/` and `.collider/runs/`.

### Layout

ACTIVE MODE is a fixed-height application shell (no document scrolling):
top bar with provenance · left loop rail (DETECT → GUARD, replay pending) ·
one current step in the center · proof drawer (collapsed by default: code diff,
spec patch, regression contract, decision memory, receipts, hashes, provenance) ·
bottom action bar holding the primary action. The GUARD step lists three
future agent changes; each is judged with and without decision memory and
shows MERGE BLOCKED, MERGE ALLOWED or DECISION REQUIRED. The rail follows what
is on screen: GUARD reads ✓ only once the revealed receipt reached that
change's expected verdict and the exact prior bytes were restored. On phones the rail becomes a compact progress line, the
action bar is sticky, and proof opens as a bottom sheet. All API calls are
relative (`./api/...`), so the UI works behind any single origin.

## EVIDENCE MODE

Switch with the mode control in the masthead. It shows the committed receipts
(baseline-001, local-resolved-004, decision-001) and labels them
`COMMITTED EVIDENCE · LOCAL / PRESEEDED`. Nothing is executed by the browser.
The guard probe is not part of committed evidence.

When the page is served statically (`python3 -m http.server 4173 --directory demo-ui`),
ACTIVE MODE reports `ACTIVE MODE UNAVAILABLE` and EVIDENCE MODE still works.

## Canonical evidence

The UI is generated from:

- evidence/runs/baseline-001/
- evidence/runs/local-resolved-004/
- evidence/comparisons/baseline-001-vs-local-resolved-004.json

## Truth boundary

The canonical demo is LOCAL / PRESEEDED.

Do not narrate it as LIVE_BOB execution.
