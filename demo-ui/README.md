# COLLIDER Demo UI

Evidence-first static demo surface.

## Generate canonical demo data

    python3 demo-ui/build_demo_data.py

## ACTIVE MODE (default)

    python3 demo-ui/server.py

Serves the UI at 127.0.0.1:4173 with bounded local actions:

    GET  /api/state    gate on the committed tree
    POST /api/decide   {"choice": "USE_ACCOUNT_ID" | "KEEP_UNKNOWN"}
    POST /api/guard    {"decision_id": "<session id from USE_ACCOUNT_ID>"}
    GET  /api/gate?decision=<session id>

No HTTP input carries values or paths. Every action writes only to the
git-ignored `.collider/workspaces/` and `.collider/runs/`.

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
