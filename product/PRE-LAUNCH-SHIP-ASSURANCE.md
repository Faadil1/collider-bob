# Pre-Launch / Ship Assurance Gate

## Promotion chain

`PRE_LAUNCH_CODE_OK → DEPLOY → LIVE_RUNTIME_CHECK → CRITICAL_PATH_PASS → PROOF_CAPTURED → SHIP`

This gate applies to the real production runtime. Repository correctness alone is insufficient.

## Current deployment

- URL: https://collider-semantic-ci.faadil-casecraft.workers.dev/
- Runtime: Cloudflare Worker + Static Assets + per-browser-session Container
- Runtime code commit used for deployment: `bdfd9d35054ddefe8e48c7e67f525f5d3d55f5e7`
- Cloudflare version observed in deployment history: `f946793b`
- Active provenance: `CLOUDFLARE_CONTAINER / PRESEEDED / INTERACTIVE_WEB`
- Fresh LIVE_BOB generation: **NOT CLAIMED**

## Audit

| Area | Status | Current evidence / remaining work |
|---|---|---|
| Legal & Privacy | N/A / REVIEWED | Demo has no account system or intended PII collection. Session uses an opaque random identifier. Do not upgrade this to a legal-compliance claim. |
| HTTPS | PROVEN | Public runtime is served over HTTPS by Cloudflare. |
| Secrets | PROVEN FOR REPO | Wrangler config requires no application secret; no frontend secret is part of the adapter design. Account credentials remain deployment-side only. |
| Session safety | PROVEN IN CODE / RUNTIME PARTIAL | 256-bit opaque session id; HttpOnly, Secure, SameSite=Lax cookie; malformed/duplicate cookie replaced; container name derived by Worker hash. Separate-session live proof still pending. |
| Request boundary | PROVEN IN CODE | API routes/methods are allow-listed, request body bounded to 4096 bytes, only content-type/accept forwarded. |
| Container network | PROVEN IN CONFIG | Container has outbound Internet disabled. |
| Security headers / CSP | PENDING | Must inspect final production headers before SHIP. |
| Abuse / rate limiting | REVIEW NEEDED | Low-volume hackathon demo; no dedicated rate limiter proven. Decide explicit N/A or bounded mitigation before SHIP. |
| Metadata | PARTIAL_PASS | Public title and description are present. |
| Canonical / OG / favicon | PENDING / NON-CORE | Verify link-preview metadata and favicon; add only if it improves submission sharing. |
| sitemap.xml | N/A | Single-purpose hackathon demo; current endpoint is 404 and search indexing is not a product requirement. |
| robots.txt | REVIEWED | Cloudflare serves robots/content-signal text. No staging-indexing claim is made. |
| Accessibility | ACTIVE | Reduced-motion path exists. Keyboard/focus, contrast, semantics, and final mobile usability still need live smoke. |
| Performance | ACTIVE | Public page responds; no Core Web Vitals or formal performance budget has been recorded. |
| Responsive / mobile | PENDING | Final mobile smoke required. |
| Error / loading / empty states | PARTIAL_PASS | Active-mode unavailable, action failure, compile, guard-running, abstention, and restoration states exist. |
| Input/action safety | PROVEN FOR CURRENT ACTIONS | Human choice is bounded; mutations occur in isolated workspace; guard mutation is restored exactly. |
| Retry / idempotency | REVIEW NEEDED | Current judge path is bounded and session-scoped; no general idempotency claim. |
| Observability | PARTIAL_PASS | Cloudflare observability enabled; container emits one-line request logs without request bodies. Operational alerting is not proven. |
| Analytics events | N/A | No product-analytics requirement for the hackathon demo. Do not claim analytics instrumentation. |
| Narrative / primary CTA | PARTIAL_PASS | Core narrative and decision flow are strong; Outsider Break Test still pending. |
| Critical resolved path | PROVEN | DECISION_REQUIRED → USE account_id → compile/repair → 2→0 → SEMANTICALLY_READY. |
| Negative path | PROVEN | KEEP UNKNOWN preserves DECISION_REQUIRED and writes no canon/repair. |
| Second act | PROVEN | Future incompatible change → MERGE_BLOCKED → exact restore → SEMANTICALLY_READY. |
| Session isolation | PENDING | Must prove a separate browser session starts from its own DECISION_REQUIRED state. |
| Runtime / commit binding | ACTIVE | Deployment was issued from the verified branch workspace; record a dedicated Cloudflare-version↔Git-SHA receipt before PROVEN. |
| Rollback / deployment recovery | PENDING | Cloudflare version history exists; rehearse or document exact rollback path before SHIP. |
| Proof capture | PARTIAL_PASS | Core and abstention paths captured in live user recordings. Session isolation/mobile/header/rollback receipts remain. |

## Discoverability observation

A production fetch confirmed:

- title: `COLLIDER — Semantic CI`
- description: `Semantic CI for agentic software development: detect, decide, compile, patch, verify, remember, guard.`
- viewport is mobile-aware.
- `sitemap.xml` currently returns 404; classified N/A for this single-purpose demo.

## Ship blockers

The build must not be marked `SHIP` until:

1. separate-session isolation is observed;
2. mobile smoke passes;
3. security headers/CSP are inspected and either fixed or explicitly accepted;
4. runtime-version↔Git-SHA binding is recorded;
5. rollback/recovery path is documented;
6. final critical-path receipt is captured.

## Gate verdict

**ACTIVE — PRODUCTION CORE PATH PROVEN; SHIP NOT YET EARNED**
