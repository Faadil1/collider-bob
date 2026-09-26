"""
COLLIDER action API inside a Cloudflare Container.

    python3 cloudflare/container_server.py        # binds 0.0.0.0:8080

This is a thin adapter over demo-ui/server.py. All semantic behavior (decide,
KEEP UNKNOWN, compile, guard probe, gate) is the existing Python runtime; this
file only:

  - selects the CLOUDFLARE_CONTAINER provenance profile
      execution_environment = CLOUDFLARE_CONTAINER
      human_decision_source = INTERACTIVE_WEB
      interpretation_source = PRESEEDED (unchanged)
  - serves the API only (static assets are served by the Worker's Static
    Assets binding, never by the container)
  - binds 0.0.0.0:8080, the ColliderContainer class's defaultPort

Each browser session is routed by the Worker to its own named container, so
the ephemeral .collider/ runtime directory is per session. It lives on the
container's ephemeral disk and is lost when the container sleeps or is
recreated; the packaged repository files are the immutable baseline.
"""

import importlib.util
import sys
from http.server import HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HOST = "0.0.0.0"
PORT = 8080
API_PATHS = {"/api/state", "/api/gate", "/api/decide", "/api/guard"}
HEALTH_PATH = "/healthz"


def load_action_server():
    spec = importlib.util.spec_from_file_location(
        "collider_action_server", ROOT / "demo-ui" / "server.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.configure("CLOUDFLARE_CONTAINER")
    return module


server_mod = load_action_server()


class ApiOnlyHandler(server_mod.Handler):
    """The existing bounded API handler, minus static file serving."""

    server_version = "collider-container"
    sys_version = ""

    def _not_found(self):
        return self._json(404, {"error": "not found"})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == HEALTH_PATH:
            # Readiness probe for the Container class (pingEndpoint). The
            # Worker never forwards this path from the browser.
            return self._json(200, {"ok": True})
        if path not in API_PATHS:
            return self._not_found()
        return super().do_GET()

    def do_HEAD(self):
        return self._not_found()

    def do_POST(self):
        if urlparse(self.path).path not in API_PATHS:
            return self._not_found()
        return super().do_POST()

    def log_message(self, fmt, *args):
        # One line per request to stdout (Workers Logs); no request bodies.
        sys.stdout.write("%s %s\n" % (self.command, urlparse(self.path).path))


def make_server(host: str = HOST, port: int = PORT) -> HTTPServer:
    # Single-threaded on purpose (see demo-ui/server.py): the compiler changes
    # directory while repairing and the guard probe mutates then restores a
    # workspace file. One container serves one browser session.
    return HTTPServer((host, port), ApiOnlyHandler)


def main():
    httpd = make_server()
    print(
        f"COLLIDER container action API on {HOST}:{PORT} "
        f"({server_mod.RUNTIME['execution_environment']})",
        flush=True,
    )
    httpd.serve_forever()


if __name__ == "__main__":
    main()
