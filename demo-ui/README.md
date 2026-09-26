# COLLIDER Demo UI

Evidence-first static demo surface.

## Generate canonical demo data

    python3 demo-ui/build_demo_data.py

## Preview (action-capable)

    python3 demo-ui/server.py

Serves the UI at 127.0.0.1:4173 and adds a local action endpoint. Choosing a value
on the SPEC_GAP panel runs `collider.decision_compiler` for real, and the UI shows
the diff, verification, decision memory and gate verdict. Receipts go to the
git-ignored `.collider/runs/`.

## Preview (static)

    python3 -m http.server 4173 --directory demo-ui

With no action server, the decision control shows the committed receipt
`evidence/decisions/decision-001` and labels it as a committed receipt, not
something executed in the browser.

Then open port 4173 from the Codespaces Ports panel.

## Canonical evidence

The UI is generated from:

- evidence/runs/baseline-001/
- evidence/runs/local-resolved-004/
- evidence/comparisons/baseline-001-vs-local-resolved-004.json

## Truth boundary

The canonical demo is LOCAL / PRESEEDED.

Do not narrate it as LIVE_BOB execution.
