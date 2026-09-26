# COLLIDER Demo UI

Evidence-first static demo surface.

## Generate canonical demo data

    python3 demo-ui/build_demo_data.py

## Preview

    python3 -m http.server 4173 --directory demo-ui

Then open port 4173 from the Codespaces Ports panel.

## Canonical evidence

The UI is generated from:

- evidence/runs/baseline-001/
- evidence/runs/local-resolved-004/
- evidence/comparisons/baseline-001-vs-local-resolved-004.json

## Truth boundary

The canonical demo is LOCAL / PRESEEDED.

Do not narrate it as LIVE_BOB execution.
