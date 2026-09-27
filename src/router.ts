// COLLIDER Worker routing — pure logic, no Cloudflare runtime imports, so it
// can be unit-tested under Node (see tests/test_cloudflare_adapter.py).
//
//   non-API request       → Static Assets binding (demo-ui/)
//   /api/{state,gate}     → GET  → this browser session's own Container
//   /api/{decide,guard}   → POST → this browser session's own Container
//   any other /api/*      → 404 at the Worker (no Container is touched)
//
// Session model: the Worker mints a 256-bit random opaque id and stores it in
// an HttpOnly/Secure/SameSite=Lax cookie. The Container name is derived from
// that id by SHA-256 at the Worker boundary; the browser never supplies a
// Container name, and a malformed cookie is replaced, not trusted.

export const SESSION_COOKIE = "collider_session";
export const SESSION_ID_RE = /^[0-9a-f]{64}$/;
export const CONTAINER_NAME_PREFIX = "collider-session-";
export const MAX_BODY_BYTES = 4096;

export const API_ROUTES: Readonly<Record<string, readonly string[]>> = Object.freeze({
  "/api/state": Object.freeze(["GET"]),
  "/api/gate": Object.freeze(["GET"]),
  "/api/decide": Object.freeze(["POST"]),
  "/api/guard": Object.freeze(["POST"]),
});

// Only these request headers are forwarded to the Container.
const FORWARDED_HEADERS = ["content-type", "accept"];

export interface FetchTarget {
  fetch(request: Request): Promise<Response>;
}

export interface RouterDeps {
  assets: FetchTarget;
  containerFor(name: string): FetchTarget;
  randomBytes?(length: number): Uint8Array;
  // Cloudflare Worker Version id (version_metadata binding), when deployed.
  workerVersion?: string;
}

// Every API response names the deployed Worker Version that produced it, so a
// live observation can be bound to a specific deployment (and, through the
// Workers Builds record for that version, to a Git commit).
export const VERSION_HEADER = "x-collider-worker-version";
const VERSION_RE = /^[0-9a-f-]{8,64}$/;

function toHex(bytes: Uint8Array): string {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

function defaultRandomBytes(length: number): Uint8Array {
  const bytes = new Uint8Array(length);
  crypto.getRandomValues(bytes);
  return bytes;
}

export function newSessionId(randomBytes: (n: number) => Uint8Array = defaultRandomBytes): string {
  const id = toHex(randomBytes(32));
  if (!SESSION_ID_RE.test(id)) throw new Error("random source produced an invalid session id");
  return id;
}

export function readSessionId(cookieHeader: string | null): string | null {
  if (!cookieHeader) return null;
  const values: string[] = [];
  for (const part of cookieHeader.split(";")) {
    const eq = part.indexOf("=");
    if (eq < 0) continue;
    if (part.slice(0, eq).trim() === SESSION_COOKIE) values.push(part.slice(eq + 1).trim());
  }
  // Exactly one well-formed value, otherwise a fresh session is minted.
  if (values.length !== 1 || !SESSION_ID_RE.test(values[0])) return null;
  return values[0];
}

export function sessionCookie(sessionId: string): string {
  if (!SESSION_ID_RE.test(sessionId)) throw new Error("refusing to set a malformed session id");
  return `${SESSION_COOKIE}=${sessionId}; Path=/; HttpOnly; Secure; SameSite=Lax`;
}

export async function containerName(sessionId: string): Promise<string> {
  if (!SESSION_ID_RE.test(sessionId)) throw new Error("refusing to route a malformed session id");
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(sessionId));
  return CONTAINER_NAME_PREFIX + toHex(new Uint8Array(digest));
}

export function isApiPath(pathname: string): boolean {
  return pathname === "/api" || pathname.startsWith("/api/");
}

// Every API response is data, never a document: nothing in it may render,
// frame or load anything. (Pages and assets get demo-ui/_headers.)
export const API_SECURITY_HEADERS: Readonly<Record<string, string>> = Object.freeze({
  "x-content-type-options": "nosniff",
  "content-security-policy": "default-src 'none'; frame-ancestors 'none'",
  "referrer-policy": "no-referrer",
});

function json(status: number, body: unknown, extra: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json", "cache-control": "no-store",
      ...API_SECURITY_HEADERS, ...extra,
    },
  });
}

export async function handleRequest(request: Request, deps: RouterDeps): Promise<Response> {
  const url = new URL(request.url);

  if (!isApiPath(url.pathname)) {
    return deps.assets.fetch(request);
  }

  const response = await handleApi(request, url, deps);
  if (deps.workerVersion && VERSION_RE.test(deps.workerVersion)) {
    response.headers.set(VERSION_HEADER, deps.workerVersion);
  }
  return response;
}

async function handleApi(request: Request, url: URL, deps: RouterDeps): Promise<Response> {
  const methods = API_ROUTES[url.pathname];
  if (!methods) return json(404, { error: "not found" });
  if (!methods.includes(request.method)) {
    return json(405, { error: "method not allowed" }, { allow: methods.join(", ") });
  }

  let body: string | undefined;
  if (request.method === "POST") {
    const declared = Number(request.headers.get("content-length") ?? "0");
    if (!Number.isFinite(declared) || declared > MAX_BODY_BYTES) {
      return json(413, { error: "request body too large" });
    }
    body = await request.text();
    if (new TextEncoder().encode(body).length > MAX_BODY_BYTES) {
      return json(413, { error: "request body too large" });
    }
  }

  let sessionId = readSessionId(request.headers.get("cookie"));
  const minted = sessionId === null;
  if (sessionId === null) sessionId = newSessionId(deps.randomBytes ?? defaultRandomBytes);

  const headers = new Headers();
  for (const name of FORWARDED_HEADERS) {
    const value = request.headers.get(name);
    if (value !== null) headers.set(name, value);
  }

  // Path and query are forwarded as-is; the Container validates them with the
  // same bounded rules as the local server (choice enum, strict session ids).
  const forward = new Request(`http://container${url.pathname}${url.search}`, {
    method: request.method,
    headers,
    body,
  });

  let upstream: Response;
  try {
    upstream = await deps.containerFor(await containerName(sessionId)).fetch(forward);
  } catch {
    const out = json(503, { error: "active runtime unavailable; the session container could not be reached" });
    if (minted) out.headers.append("set-cookie", sessionCookie(sessionId));
    return out;
  }

  const out = new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "content-type": upstream.headers.get("content-type") ?? "application/json",
      "cache-control": "no-store",
      ...API_SECURITY_HEADERS,
    },
  });
  if (minted) out.headers.append("set-cookie", sessionCookie(sessionId));
  return out;
}
