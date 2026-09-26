// Executes src/router.ts against fake Static Assets / Container bindings and
// prints one JSON object with every observation. Run by
// tests/test_cloudflare_adapter.py via `node --experimental-strip-types`.

import {
  API_ROUTES,
  CONTAINER_NAME_PREFIX,
  MAX_BODY_BYTES,
  SESSION_COOKIE,
  containerName,
  handleRequest,
  readSessionId,
} from "../../src/router.ts";

type Call = { name: string; method: string; url: string; headers: Record<string, string>; body: string };

const assetCalls: string[] = [];
const containerCalls: Call[] = [];
let failContainers = false;

const deps = {
  assets: {
    async fetch(req: Request) {
      assetCalls.push(new URL(req.url).pathname);
      return new Response("asset", { status: 200, headers: { "content-type": "text/html" } });
    },
  },
  containerFor(name: string) {
    return {
      async fetch(req: Request) {
        if (failContainers) throw new Error("container down");
        const headers: Record<string, string> = {};
        req.headers.forEach((v, k) => { headers[k] = v; });
        containerCalls.push({ name, method: req.method, url: req.url, headers, body: await req.text() });
        return new Response(JSON.stringify({ ok: true, container: name }), {
          status: 200,
          headers: { "content-type": "application/json", "set-cookie": "evil=1" },
        });
      },
    };
  },
};

const ORIGIN = "https://collider-semantic-ci.example";

async function call(path: string, init: RequestInit & { cookie?: string } = {}) {
  const headers = new Headers(init.headers);
  if (init.cookie !== undefined) headers.set("cookie", init.cookie);
  const before = containerCalls.length;
  const res = await handleRequest(new Request(ORIGIN + path, { ...init, headers }), deps);
  const setCookie = res.headers.get("set-cookie");
  const cookieId = setCookie ? /collider_session=([^;]*)/.exec(setCookie)?.[1] ?? null : null;
  return {
    status: res.status,
    setCookie,
    cookieId,
    allow: res.headers.get("allow"),
    cacheControl: res.headers.get("cache-control"),
    container: containerCalls.length > before ? containerCalls[containerCalls.length - 1] : null,
    body: await res.text(),
  };
}

const out: Record<string, unknown> = {};

// Static assets
out.staticRoot = await call("/");
out.staticApp = await call("/app.js");
out.staticNearApi = await call("/apix");
out.assetCalls = [...assetCalls];

// New session → cookie + container
const first = await call("/api/state");
out.first = first;
const sid = first.cookieId as string;
out.expectedName = await containerName(sid);

// Same session → same container, no new cookie
out.sameGet = await call("/api/state", { cookie: `${SESSION_COOKIE}=${sid}` });
out.samePost = await call("/api/decide", {
  method: "POST",
  cookie: `other=1; ${SESSION_COOKIE}=${sid}`,
  headers: { "content-type": "application/json", "x-forwarded-for": "1.2.3.4", authorization: "Bearer x" },
  body: JSON.stringify({ choice: "USE_ACCOUNT_ID" }),
});
out.sameGate = await call("/api/gate?decision=ui-20260926T000000000000Z", { cookie: `${SESSION_COOKIE}=${sid}` });

// Different session → different container
const second = await call("/api/state");
out.second = second;

// Injection attempts: never trusted, a fresh id is minted every time
const injections = [
  "../../etc/passwd",
  CONTAINER_NAME_PREFIX + "0".repeat(64),
  "A".repeat(64),
  "0".repeat(63),
  "0".repeat(65),
  `${"0".repeat(64)}; ${SESSION_COOKIE}=${"1".repeat(64)}`,
  "",
];
out.injections = [];
for (const value of injections) {
  const cookie = value.includes(SESSION_COOKIE) ? `${SESSION_COOKIE}=${value}` : `${SESSION_COOKIE}=${value}`;
  const r = await call("/api/state", { cookie });
  (out.injections as unknown[]).push({ value, status: r.status, minted: r.cookieId, name: r.container?.name ?? null });
}
out.readSessionId = {
  none: readSessionId(null),
  valid: readSessionId(`${SESSION_COOKIE}=${"a".repeat(64)}`),
  duplicate: readSessionId(`${SESSION_COOKIE}=${"a".repeat(64)}; ${SESSION_COOKIE}=${"b".repeat(64)}`),
  upper: readSessionId(`${SESSION_COOKIE}=${"A".repeat(64)}`),
};

// API-only routing
const callsBefore = containerCalls.length;
out.unknownApi = await call("/api/containers/start", { cookie: `${SESSION_COOKIE}=${sid}` });
out.apiRoot = await call("/api", { cookie: `${SESSION_COOKIE}=${sid}` });
out.wrongMethod = await call("/api/state", { method: "POST", cookie: `${SESSION_COOKIE}=${sid}`, body: "{}" });
out.wrongMethodGuard = await call("/api/guard", { cookie: `${SESSION_COOKIE}=${sid}` });
out.tooLarge = await call("/api/decide", {
  method: "POST",
  cookie: `${SESSION_COOKIE}=${sid}`,
  headers: { "content-type": "application/json" },
  body: "x".repeat(MAX_BODY_BYTES + 1),
});
out.containerCallsDuringRejected = containerCalls.length - callsBefore;
out.routes = API_ROUTES;

// Container unavailable
failContainers = true;
out.down = await call("/api/state");
failContainers = false;

out.containerNames = [...new Set(containerCalls.map((c) => c.name))];
process.stdout.write(JSON.stringify(out));
