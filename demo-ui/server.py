"""
COLLIDER local action server — makes the demo ACTION-CAPABLE.

    python3 demo-ui/server.py            # http://127.0.0.1:4173

Serves demo-ui/ statically and exposes three local actions:

    GET  /api/state    live gate verdict on the committed (pre-decision) tree
    POST /api/decide   {"concept": "customer_identity", "value": "account_id"}
                       → runs collider.decision_compiler for real; the human
                         decision source is recorded as INTERACTIVE_LOCAL_UI
    GET  /api/gate?decision=<id>   re-runs the gate on a compiled workspace

Each POST compiles into its own workspace (.collider/workspaces/<id>) and
receipt directory (.collider/runs/<id>), both git-ignored. Committed evidence
is never written by the server.

Single-threaded on purpose: the compiler changes directory while repairing.
Binds to 127.0.0.1 only.
"""

import datetime
import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collider import gate as gate_mod  # noqa: E402
from collider.decision_compiler import compile_decision, display_path  # noqa: E402

UI_DIR = Path(__file__).resolve().parent
RUNS_DIR = ROOT / ".collider/runs"
WORKSPACES_DIR = ROOT / ".collider/workspaces"


def strip(g: dict) -> dict:
    return {k: v for k, v in g.items() if k != "verification_output"}


def new_decision_id() -> str:
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return f"ui-{stamp}"


class Handler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def _json(self, status: int, obj) -> None:
        body = json.dumps(obj, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/state":
            return self._json(200, {
                "server": "collider-local-action",
                "execution": "LOCAL",
                "gate": strip(gate_mod.evaluate_gate(ROOT)),
            })
        if url.path == "/api/gate":
            decision = parse_qs(url.query).get("decision", [""])[0]
            workspace = (WORKSPACES_DIR / decision).resolve()
            if not decision or WORKSPACES_DIR.resolve() not in workspace.parents \
                    or not workspace.exists():
                return self._json(404, {"error": "unknown decision workspace"})
            return self._json(200, strip(gate_mod.evaluate_gate(workspace)))
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/decide":
            return self._json(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            decision_id = new_decision_id()
            result = compile_decision(
                payload.get("concept", "customer_identity"),
                payload["value"],
                human_decision_source="INTERACTIVE_LOCAL_UI",
                decision_id=decision_id,
                workspace=WORKSPACES_DIR / decision_id,
                out_dir=RUNS_DIR / decision_id,
            )
        except (KeyError, ValueError, RuntimeError, FileExistsError) as e:
            return self._json(400, {"error": str(e)})
        result["receipt_dir"] = display_path(Path(result["out_dir"]), ROOT)
        result.pop("out_dir")
        result.pop("workspace")
        return self._json(200, result)


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"COLLIDER local action server — http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
