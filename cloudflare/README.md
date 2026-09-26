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
| Fresh-agent replay | `NOT_EXECUTED / PENDING_LIVE_BOB` everywhere |

Nothing is labelled LIVE_BOB. The container image has no git, so
`provenance.input_commit` reads `UNKNOWN` there rather than guessing a commit.
