"""
COLLIDER local action server — ACTIVE MODE for the demo.

    python3 demo-ui/server.py            # http://127.0.0.1:4173

Serves demo-ui/ statically and exposes bounded local actions:

    GET  /api/state     live gate verdict on the committed (pre-decision) tree
    POST /api/decide    {"choice": "USE_ACCOUNT_ID" | "KEEP_UNKNOWN"}
                        USE_ACCOUNT_ID → collider.decision_compiler, for real
                        KEEP_UNKNOWN   → abstention receipt only; no canon,
                                         no spec patch, no repair
    POST /api/guard     {"decision_id": "<id from a USE_ACCOUNT_ID session>"}
                        → collider.guard_probe in that session's workspace
                          (fixed probe: customer_identity account_id → email)
    GET  /api/gate?decision=<id>   re-runs the gate on a compiled workspace

HTTP input never carries values or paths: choices are an enum and sessions are
matched by a strict id pattern against directories this server created.

Every action writes only to .collider/workspaces/<id> and .collider/runs/<id>
(git-ignored). Committed evidence and the source tree are never written.

Single-threaded on purpose: the compiler changes directory while repairing and
the guard probe mutates then restores a workspace file.
Binds to 127.0.0.1 only.
"""

import datetime
import json
import re
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collider import gate as gate_mod  # noqa: E402
from collider.decision_compiler import (  # noqa: E402
    compile_decision,
    display_path,
    record_abstention,
)
from collider.guard_probe import run_guard_probe  # noqa: E402

UI_DIR = Path(__file__).resolve().parent
RUNS_DIR = ROOT / ".collider/runs"
WORKSPACES_DIR = ROOT / ".collider/workspaces"

PROVENANCE_MODE = "ACTIVE"
SESSION_ID_RE = re.compile(r"^ui-\d{8}T\d{12}Z$")

# The only decisions the judge-facing UI can make.
CHOICES = {
    "USE_ACCOUNT_ID": ("customer_identity", "account_id"),
    "KEEP_UNKNOWN": ("customer_identity", None),
}


def strip(g: dict) -> dict:
    return {k: v for k, v in g.items() if k != "verification_output"}


def new_session_id() -> str:
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return f"ui-{stamp}"


def compiled_session(decision_id) -> tuple[Path, Path] | None:
    """Resolve a session id to (workspace, runs dir) only if this server made it."""
    if not isinstance(decision_id, str) or not SESSION_ID_RE.fullmatch(decision_id):
        return None
    workspace = WORKSPACES_DIR / decision_id
    runs = RUNS_DIR / decision_id
    if not (workspace / gate_mod.MEMORY_RELPATH).is_file() or not runs.is_dir():
        return None
    return workspace, runs


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

    def _payload(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")
        return payload

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/state":
            return self._json(200, {
                "server": "collider-local-action",
                "provenance_mode": PROVENANCE_MODE,
                "execution": "LOCAL",
                "gate": strip(gate_mod.evaluate_gate(ROOT)),
            })
        if url.path == "/api/gate":
            session = compiled_session(parse_qs(url.query).get("decision", [""])[0])
            if session is None:
                return self._json(404, {"error": "unknown decision session"})
            return self._json(200, strip(gate_mod.evaluate_gate(session[0])))
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/decide":
            return self._decide()
        if path == "/api/guard":
            return self._guard()
        return self._json(404, {"error": "not found"})

    def _decide(self):
        try:
            choice = self._payload().get("choice")
            if choice not in CHOICES:
                raise ValueError(f"REFUSE: choice must be one of {sorted(CHOICES)}")
            concept, value = CHOICES[choice]
            session_id = new_session_id()
            if value is None:
                result = record_abstention(
                    concept,
                    human_decision_source="INTERACTIVE_LOCAL_UI",
                    action_id=session_id,
                    out_dir=RUNS_DIR / session_id,
                )
                result["kind"] = "abstention"
            else:
                result = compile_decision(
                    concept, value,
                    human_decision_source="INTERACTIVE_LOCAL_UI",
                    decision_id=session_id,
                    workspace=WORKSPACES_DIR / session_id,
                    out_dir=RUNS_DIR / session_id,
                )
                result["kind"] = "decision"
                result.pop("workspace")
        except (ValueError, RuntimeError, FileExistsError) as e:
            return self._json(400, {"error": str(e)})
        result["choice"] = choice
        result["provenance_mode"] = PROVENANCE_MODE
        result["receipt_dir"] = display_path(Path(result.pop("out_dir")), ROOT)
        return self._json(200, result)

    def _guard(self):
        try:
            session = compiled_session(self._payload().get("decision_id"))
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        if session is None:
            return self._json(404, {"error": "unknown decision session"})
        try:
            receipt = run_guard_probe(session[0], session[1])
        except FileExistsError as e:
            return self._json(409, {"error": str(e)})
        except (ValueError, RuntimeError) as e:
            return self._json(400, {"error": str(e)})
        receipt["provenance_mode"] = PROVENANCE_MODE
        receipt["receipt_path"] = display_path(session[1] / "guard-probe.json", ROOT)
        return self._json(200, receipt)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="COLLIDER local action server")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"COLLIDER local action server — http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
