# COLLIDER on Cloudflare

```
browser ──► Worker  collider-semantic-ci  (src/index.ts, src/router.ts)
             │
             ├─ non-API paths ──► Workers Static Assets   demo-ui/   (ACTIVE + EVIDENCE UI)
             │
             └─ /api/state  GET  ┐
                /api/gate   GET  │  session cookie ─► SHA-256 ─► getContainer(COLLIDER, name)
                /api/decide POST │                               one Container per browser session
                /api/guard  POST ┘                               cloudflare/container_server.py :8080
                  {decision_id, probe: IDENTITY_REVERT | COMPATIBLE_CHANGE | MONEY_UNIT_DRIFT}
```

## Deploy

Workers Builds (GitHub integration), repository root, deploy command:

    npx wrangler deploy

No API token, account id or secret is stored in this repository. The build
runs `wrangler deploy`, which bundles the Worker, uploads `demo-ui/` as static
assets (minus `demo-ui/.assetsignore`), builds `./Dockerfile` and registers the
`ColliderContainer` class.

Local checks without Cloudflare credentials:

    npm install
    npx tsc --noEmit
    npx wrangler deploy --dry-run --outdir .wrangler/dry-run

## Routing and session isolation

- Only `/api/*` runs the Worker first (`assets.run_worker_first`); every other
  request is served by Static Assets. The frontend calls relative URLs only
  (`./api/...`), so it works on any single origin (workers.dev or a custom
  domain) without code changes.
- The Worker allowlists four routes and their methods. Any other `/api/*` path
  gets a 404 from the Worker and no Container is touched. Bodies are capped at
  4 KiB. Only `content-type` and `accept` are forwarded; browser cookies are not.
- On the first API call the Worker mints a 256-bit random session id and sets
  `collider_session` with `HttpOnly; Secure; SameSite=Lax; Path=/`.
- The Container name is `collider-session-` + SHA-256(session id), derived in
  the Worker. The browser never names a Container. A missing, malformed or
  duplicated cookie is replaced with a fresh id, never trusted.
- `getContainer(env.COLLIDER, name)` gives every request of a session the same
  named instance. `getRandom()` is never used: ACTIVE MODE mutates a workspace,
  so a session must always come back to its own runtime. Two sessions never
  share `.collider/` workspaces, decision memory, guard receipts or files.

## Security headers and limits

- Pages and assets: `demo-ui/_headers` (Workers Static Assets) sets a strict
  CSP (`default-src 'none'`; scripts, styles and `fetch` from the same origin
  only; no inline script or style; `frame-ancestors 'none'`), `nosniff`,
  `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, COOP and a closed
  `Permissions-Policy`. `demo-ui/server.py` applies the same block locally, so
  browser checks run against the shipped policy.
- API responses: the Worker adds `nosniff`, `Content-Security-Policy:
  default-src 'none'; frame-ancestors 'none'` and `Referrer-Policy:
  no-referrer` to every `/api/*` response, including its own 404/405/413/503.
- Abuse bounds (no dedicated rate limiter): at most 20 container instances
  (`max_instances`), 4 KiB request bodies, four allow-listed routes, and at most
  24 decision/abstention runs per container (HTTP 429 after that). Each guard
  probe runs once per decision. No outbound network from the container.

## Runtime / commit binding

Every `/api/*` response carries `x-collider-worker-version: <Worker Version
id>` from the `version_metadata` binding, and the UI shows it in
PROOF → PROVENANCE. To bind a live observation to Git: take that id, open the
Worker's Deployments / Workers Builds history in the Cloudflare dashboard and
read the commit recorded for that version. The container image has no git, so
receipts written inside it report `input_commit: UNKNOWN` rather than guessing.

## Rollback / recovery

- Nothing durable lives in the runtime: container disks are ephemeral and
  every session restarts from the packaged baseline, so a rollback cannot lose
  user data and needs no migration.
- Roll back the Worker to a previous version from the Cloudflare dashboard
  (Workers → `collider-semantic-ci` → Deployments) or with
  `npx wrangler rollback <version-id>` from an authenticated machine. Confirm
  the result by reading `x-collider-worker-version` on `/api/state`.
- Or revert the offending commit on the deployed branch; Workers Builds
  redeploys it. Check afterwards that the container image rebuilt from the
  reverted `Dockerfile` (dashboard → Containers) before re-running the
  critical path.
- A session stuck in a bad state is recovered by opening COLLIDER in a new
  browser session (new cookie → new container).

## Container lifecycle

- `ColliderContainer`: `defaultPort = 8080`, `sleepAfter = "2h"`,
  `enableInternet = false`, readiness probe on `/healthz` (never forwarded by
  the Worker).
- The image (`Dockerfile`, allowlisted by `.dockerignore`) contains only the
  ACTIVE MODE runtime: `collider/`, `api/`, `ledger/`, `notifications/` with
  their behavioral tests, `fixtures/failed-payment/`, `demo-ui/server.py`,
  `cloudflare/container_server.py` and pytest. It runs as a non-root user;
  the baseline files are read-only and only `/app/.collider/` is writable.
- **The container filesystem is ephemeral.** `.collider/` output exists only
  for the life of that instance. After `sleepAfter` of inactivity, or when the
  instance is recreated (for example on a new deploy), the session starts again
  from the packaged baseline at `DECISION_REQUIRED`. Nothing is persisted beyond
  the container lifecycle, and nothing claims otherwise.
- The runtime is single-threaded per container, matching the local server. One
  container serves one browser session.

## Provenance

| Surface | Label |
|---|---|
| ACTIVE MODE via Cloudflare | `execution_environment = CLOUDFLARE_CONTAINER`, `interpretation_source = PRESEEDED`, `human_decision_source = INTERACTIVE_WEB` · UI: `CLOUDFLARE CONTAINER ACTIVE DEMO` |
| ACTIVE MODE via `python3 demo-ui/server.py` | `LOCAL`, `PRESEEDED`, `INTERACTIVE_LOCAL_UI` · UI: `LOCAL ACTIVE DEMO` |
| EVIDENCE MODE | `COMMITTED EVIDENCE · LOCAL / PRESEEDED` (committed receipts, never executed by the browser) |
| Replay inside the current browser session | `NOT_EXECUTED / PENDING_LIVE_BOB` |
| Separate Bob evidence | Attempt 01: `REPLAY_FAIL` (5/7); Attempt 02: targeted-repair `REPLAY_PASS` (7/7) |

The public demo's comparative interpretations are never labelled LIVE_BOB. A
separate preserved Bob run is genuinely labelled LIVE_BOB in
`evidence/bob-sessions/`, with its own session/task provenance. The container
image has no git, so `provenance.input_commit` reads `UNKNOWN` there rather
than guessing a commit.

Latest verified post-UI deployment:
- Git snapshot: `a909a682f1b033e41b1e1ef312dffbe24005af67`
- Worker version: `453a881f-3b9a-4065-b65b-25b3b2ffa369`
- Runtime: `CLOUDFLARE_CONTAINER / PRESEEDED / INTERACTIVE_WEB`
