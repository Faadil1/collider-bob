// COLLIDER Semantic CI — Cloudflare Worker entry point.
//
// Worker + Workers Static Assets (demo-ui/) + one Cloudflare Container per
// browser session. Routing rules live in ./router.ts.

import { Container, getContainer } from "@cloudflare/containers";
import { handleRequest } from "./router";

/**
 * The COLLIDER Python action runtime (cloudflare/container_server.py).
 *
 * Lifecycle: the container starts on the first API request of a session and
 * sleeps after `sleepAfter` of inactivity. Its filesystem is EPHEMERAL:
 * `.collider/` workspaces, decision memory and guard receipts exist only for
 * the life of that container instance and are lost when it sleeps or is
 * recreated. The packaged repository files are the immutable baseline, so a
 * fresh container starts again at DECISION_REQUIRED. Nothing here claims
 * persistence beyond the container lifecycle.
 */
export class ColliderContainer extends Container {
  defaultPort = 8080;
  // Protects an active judge session from being reset by a pause in activity.
  sleepAfter = "2h";
  // The runtime needs no outbound network access.
  enableInternet = false;
  // Readiness probe served by the container itself (never exposed by the Worker).
  pingEndpoint = "container/healthz";
}

interface Env {
  ASSETS: Fetcher;
  COLLIDER: DurableObjectNamespace<ColliderContainer>;
  CF_VERSION_METADATA?: WorkerVersionMetadata;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return handleRequest(request, {
      assets: env.ASSETS,
      // Stable, per-session named instance. Never getRandom(): Active Mode
      // mutates a workspace, so a session must always reach the same container.
      containerFor: (name) => getContainer(env.COLLIDER, name),
      workerVersion: env.CF_VERSION_METADATA?.id,
    });
  },
} satisfies ExportedHandler<Env>;
