# Public Mobile Smoke + Provenance Proof — 2026-09-27

## Scope

User-recorded production smoke from a real iPhone against:

https://collider-semantic-ci.faadil-casecraft.workers.dev/

This is a real-device mobile proof, not desktop emulation.

## Observed mobile behavior

On the iPhone recording, the public ACTIVE runtime successfully exercised the
full core flow without visible horizontal overflow or broken layout:

- initial DETECT state at mobile width
- decision compilation in progress
- guard flow on the mobile layout
- MERGE_BLOCKED / MERGE_ALLOWED / DECISION_REQUIRED guard states
- exact workspace restoration
- SEMANTICALLY READY AGAIN
- regression contract 7 / 7
- proof drawer opened and navigated on mobile
- Evidence Mode opened and navigated on mobile
- return to ACTIVE MODE

The proof drawer's PROVENANCE tab was visible on the phone and showed:

- execution: CLOUDFLARE_CONTAINER
- interpretations: PRESEEDED
- human decision: INTERACTIVE_WEB
- input commit: UNKNOWN
- Worker version:
  364ad4fd-7eb3-4918-aef8-f9ad049ee20a
- fresh-agent replay: NOT_EXECUTED / PENDING_LIVE_BOB

## What this proves

- Responsive/mobile layout works on a real iPhone for the full public demo path.
- The proof drawer is usable on mobile.
- ACTIVE and EVIDENCE modes remain usable on mobile.
- The live Worker version is observable in-product.

## What remains

The Worker version is now captured live, but Runtime / Commit Binding is not
PROVEN until that Cloudflare Worker version UUID is matched to the commit shown
in Workers Builds / deployment history.

Live CSP/header confirmation is also still pending.

Truth boundary is unchanged:
- PRESEEDED interpretations are not LIVE_BOB.
- Guard probes are controlled edits, not autonomous agents.
- Fresh-agent replay is NOT_EXECUTED.
