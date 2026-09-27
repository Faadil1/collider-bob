"""
Cloudflare deployment adapter tests.

  Worker routing   src/router.ts executed under Node (strip-types) with fake
                   Static Assets / Container bindings: session cookie
                   creation, same-session routing, different-session
                   isolation, API-only container routing, static routing,
                   no session-id injection.
  Container API    cloudflare/container_server.py over HTTP: API-only, health,
                   CLOUDFLARE_CONTAINER / INTERACTIVE_WEB provenance on real
                   decide + guard actions, replay still NOT_EXECUTED.
  Config           wrangler.jsonc, Dockerfile, .dockerignore, .assetsignore.
"""

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from collider.decision_compiler import compile_decision, record_abstention
from collider.guard_probe import run_guard_probe

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
SESSION_RE = re.compile(r"^[0-9a-f]{64}$")
NAME_RE = re.compile(r"^collider-session-[0-9a-f]{64}$")


def node_supports_strip_types() -> bool:
    if NODE is None:
        return False
    r = subprocess.run([NODE, "--experimental-strip-types", "-e", "const x: number = 1"],
                       capture_output=True, text=True)
    return r.returncode == 0


def load_jsonc(path: Path) -> dict:
    text = re.sub(r"^\s*//.*$", "", path.read_text(), flags=re.M)
    return json.loads(text)


# ---------------------------------------------------------------------------
# Worker routing (real src/router.ts)
# ---------------------------------------------------------------------------

@unittest.skipUnless(node_supports_strip_types(), "node with --experimental-strip-types required")
class TestWorkerRouting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        r = subprocess.run(
            [NODE, "--experimental-strip-types", "--no-warnings",
             str(ROOT / "tests/cloudflare/router_cases.ts")],
            capture_output=True, text=True, cwd=ROOT, check=True,
        )
        cls.o = json.loads(r.stdout)

    def test_static_assets_route_to_assets_binding(self):
        for key in ("staticRoot", "staticApp", "staticNearApi"):
            self.assertEqual(self.o[key]["status"], 200, key)
            self.assertIsNone(self.o[key]["container"], key)
            self.assertIsNone(self.o[key]["setCookie"], key)
        self.assertEqual(self.o["assetCalls"], ["/", "/app.js", "/apix"])

    def test_session_cookie_created_with_required_attributes(self):
        first = self.o["first"]
        self.assertEqual(first["status"], 200)
        self.assertRegex(first["cookieId"], SESSION_RE)
        cookie = first["setCookie"]
        for attr in ("HttpOnly", "Secure", "SameSite=Lax", "Path=/"):
            self.assertIn(attr, cookie)
        self.assertNotIn("Domain=", cookie)

    def test_container_name_derived_at_worker_boundary(self):
        sid = self.o["first"]["cookieId"]
        expected = "collider-session-" + hashlib.sha256(sid.encode()).hexdigest()
        self.assertEqual(self.o["expectedName"], expected)
        self.assertEqual(self.o["first"]["container"]["name"], expected)
        self.assertNotIn(sid, expected)

    def test_same_session_routes_to_same_container(self):
        name = self.o["first"]["container"]["name"]
        for key in ("sameGet", "samePost", "sameGate"):
            self.assertEqual(self.o[key]["container"]["name"], name, key)
            self.assertIsNone(self.o[key]["setCookie"], key)

    def test_different_sessions_are_isolated(self):
        a, b = self.o["first"], self.o["second"]
        self.assertNotEqual(a["cookieId"], b["cookieId"])
        self.assertNotEqual(a["container"]["name"], b["container"]["name"])

    def test_session_id_injection_is_never_trusted(self):
        seen = set()
        for inj in self.o["injections"]:
            self.assertEqual(inj["status"], 200, inj["value"])
            self.assertRegex(inj["minted"], SESSION_RE, inj["value"])
            self.assertRegex(inj["name"], NAME_RE, inj["value"])
            self.assertNotIn(inj["value"] or "∅", inj["name"])
            seen.add(inj["name"])
        self.assertEqual(len(seen), len(self.o["injections"]))
        r = self.o["readSessionId"]
        self.assertIsNone(r["none"])
        self.assertEqual(r["valid"], "a" * 64)
        self.assertIsNone(r["duplicate"])
        self.assertIsNone(r["upper"])

    def test_only_bounded_api_routes_reach_containers(self):
        self.assertEqual(self.o["unknownApi"]["status"], 404)
        self.assertEqual(self.o["apiRoot"]["status"], 404)
        self.assertEqual(self.o["wrongMethod"]["status"], 405)
        self.assertEqual(self.o["wrongMethod"]["allow"], "GET")
        self.assertEqual(self.o["wrongMethodGuard"]["status"], 405)
        self.assertEqual(self.o["tooLarge"]["status"], 413)
        self.assertEqual(self.o["containerCallsDuringRejected"], 0)
        self.assertEqual(self.o["routes"], {
            "/api/state": ["GET"], "/api/gate": ["GET"],
            "/api/decide": ["POST"], "/api/guard": ["POST"],
        })

    def test_forwarded_request_is_minimal(self):
        post = self.o["samePost"]["container"]
        self.assertEqual(post["method"], "POST")
        self.assertEqual(post["url"], "http://container/api/decide")
        self.assertEqual(json.loads(post["body"]), {"choice": "USE_ACCOUNT_ID"})
        self.assertEqual(set(post["headers"]), {"content-type"})
        gate = self.o["sameGate"]["container"]
        self.assertEqual(gate["url"], "http://container/api/gate?decision=ui-20260926T000000000000Z")

    def test_container_headers_do_not_leak_to_browser(self):
        self.assertIsNone(self.o["sameGet"]["setCookie"])  # upstream set-cookie dropped
        self.assertEqual(self.o["sameGet"]["cacheControl"], "no-store")

    def test_api_responses_carry_security_headers(self):
        for key in ("sameGet", "samePost", "unknownApi", "wrongMethod", "tooLarge", "down"):
            with self.subTest(response=key):
                self.assertEqual(self.o[key]["nosniff"], "nosniff")
                self.assertEqual(self.o[key]["csp"], "default-src 'none'; frame-ancestors 'none'")

    def test_api_responses_name_the_worker_version(self):
        v = self.o["version"]
        self.assertEqual(v["api"], "f946793b-0000-4000-8000-000000000000")
        self.assertEqual(v["unknownRoute"], "f946793b-0000-4000-8000-000000000000")
        self.assertIsNone(v["asset"])
        self.assertIsNone(v["rejected"])
        cfg = (ROOT / "wrangler.jsonc").read_text()
        self.assertIn('"version_metadata": { "binding": "CF_VERSION_METADATA" }', cfg)

    def test_container_unavailable_is_reported_not_faked(self):
        down = self.o["down"]
        self.assertEqual(down["status"], 503)
        self.assertIn("unavailable", json.loads(down["body"])["error"])


class TestWorkerEntry(unittest.TestCase):

    def test_uses_stable_named_containers_never_random(self):
        src = (ROOT / "src/index.ts").read_text()
        self.assertIn("getContainer(env.COLLIDER, name)", src)
        self.assertNotRegex(src, r"import[^;]*getRandom")
        self.assertNotRegex(src, r"getRandom\s*\(\s*env")

    def test_container_class(self):
        src = (ROOT / "src/index.ts").read_text()
        self.assertIn("export class ColliderContainer extends Container", src)
        self.assertIn("defaultPort = 8080", src)
        self.assertIn('sleepAfter = "2h"', src)
        self.assertIn("enableInternet = false", src)
        self.assertIn("EPHEMERAL", src)

    def test_no_container_management_primitives_exposed(self):
        router = (ROOT / "src/router.ts").read_text()
        for primitive in ("startAndWaitForPorts", "destroy(", "stop(", "getState", "setAlarm"):
            self.assertNotIn(primitive, router)


# ---------------------------------------------------------------------------
# Container API adapter (real Python runtime)
# ---------------------------------------------------------------------------

class TestContainerServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "collider_container_server_test", ROOT / "cloudflare/container_server.py"
        )
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)
        cls.tmp = Path(tempfile.mkdtemp(prefix="collider-cf-"))
        cls.mod.server_mod.RUNS_DIR = cls.tmp / "runs"
        cls.mod.server_mod.WORKSPACES_DIR = cls.tmp / "workspaces"
        cls.httpd = cls.mod.make_server("127.0.0.1", 0)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def call(self, path, body=None, method=None):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as res:
                return res.status, json.loads(res.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_binds_expected_port_by_default(self):
        self.assertEqual((self.mod.HOST, self.mod.PORT), ("0.0.0.0", 8080))

    def test_serves_api_only(self):
        for path in ("/", "/index.html", "/app.js", "/server.py", "/api/nope", "/../collider/gate.py"):
            status, _ = self.call(path)
            self.assertEqual(status, 404, path)
        self.assertEqual(self.call("/healthz"), (200, {"ok": True}))

    def test_state_reports_cloudflare_provenance(self):
        status, body = self.call("/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(body["provenance_mode"], "ACTIVE")
        self.assertEqual(body["execution_environment"], "CLOUDFLARE_CONTAINER")
        self.assertEqual(body["human_decision_source"], "INTERACTIVE_WEB")
        self.assertEqual(body["interpretation_source"], "PRESEEDED")
        self.assertEqual(body["gate"]["verdict"], "DECISION_REQUIRED")

    def test_decide_and_guard_carry_cloudflare_provenance(self):
        status, d = self.call("/api/decide", {"choice": "USE_ACCOUNT_ID"})
        self.assertEqual(status, 200)
        self.assertEqual(d["gate_after"]["verdict"], "SEMANTICALLY_READY")
        prov = d["memory"]["provenance"]
        self.assertEqual(prov["execution_environment"], "CLOUDFLARE_CONTAINER")
        self.assertEqual(prov["interpretation_source"], "PRESEEDED")
        self.assertEqual(prov["human_decision_source"], "INTERACTIVE_WEB")
        self.assertEqual(d["decision"]["human_decision_source"], "INTERACTIVE_WEB")
        tb = d["manifest"]["truth_boundary"]
        self.assertEqual(tb["execution"], "CLOUDFLARE_CONTAINER")
        self.assertEqual(tb["fresh_agent_replay"], "NOT_EXECUTED / PENDING_LIVE_BOB")
        self.assertEqual(d["memory"]["replay"],
                         {"status": "NOT_EXECUTED", "runtime_state": "PENDING_LIVE_BOB"})
        self.assertEqual((d["replay"]["status"], d["replay"]["runtime_state"]),
                         ("NOT_EXECUTED", "PENDING_LIVE_BOB"))

        status, g = self.call("/api/guard", {"decision_id": d["decision"]["decision_id"]})
        self.assertEqual(status, 200)
        self.assertEqual(g["guard_verdict"], "MERGE_BLOCKED")
        self.assertTrue(g["restoration_verified"])
        self.assertEqual(g["execution_environment"], "CLOUDFLARE_CONTAINER")
        self.assertEqual(g["truth_boundary"]["execution"], "CLOUDFLARE_CONTAINER")
        self.assertEqual(g["truth_boundary"]["fresh_agent_replay"], "NOT_EXECUTED / PENDING_LIVE_BOB")
        self.assertFalse(g["is_fresh_agent_replay"])

    def test_keep_unknown_carries_cloudflare_provenance(self):
        status, a = self.call("/api/decide", {"choice": "KEEP_UNKNOWN"})
        self.assertEqual(status, 200)
        self.assertFalse(a["canon_written"])
        self.assertEqual(a["gate_verdict"], "DECISION_REQUIRED")
        self.assertEqual(a["human_decision_source"], "INTERACTIVE_WEB")
        self.assertEqual(a["truth_boundary"]["execution"], "CLOUDFLARE_CONTAINER")

    def test_bounded_inputs_still_enforced(self):
        for payload in ({"choice": "email"}, {"value": "email"}, {"choice": "USE_EMAIL"}):
            self.assertEqual(self.call("/api/decide", payload)[0], 400, payload)
        self.assertEqual(self.call("/api/guard", {"decision_id": "../../etc"})[0], 404)

    def test_future_agent_changes_are_selectable_and_bounded(self):
        status, d = self.call("/api/decide", {"choice": "USE_ACCOUNT_ID"})
        self.assertEqual(status, 200)
        sid = d["decision"]["decision_id"]
        status, allowed = self.call("/api/guard", {"decision_id": sid, "probe": "COMPATIBLE_CHANGE"})
        self.assertEqual(status, 200)
        self.assertEqual(allowed["guard_verdict"], "MERGE_ALLOWED")
        self.assertTrue(allowed["receipt_path"].endswith("guard-probe-compatible-change.json"))
        status, held = self.call("/api/guard", {"decision_id": sid, "probe": "MONEY_UNIT_DRIFT"})
        self.assertEqual(status, 200)
        self.assertEqual(held["guard_verdict"], "DECISION_REQUIRED")
        self.assertEqual(held["verification_during_probe"]["full_suite"]["failed_count"], 0)
        self.assertEqual(held["execution_environment"], "CLOUDFLARE_CONTAINER")
        for probe in ("rm -rf /", "ledger/credit_entry.py", 1, None):
            self.assertEqual(self.call("/api/guard", {"decision_id": sid, "probe": probe})[0], 400, probe)
        self.assertEqual(self.call("/api/guard", {"decision_id": sid, "probe": "COMPATIBLE_CHANGE"})[0], 409)

    def test_action_sessions_are_capped_per_container(self):
        runtime = self.mod.server_mod.RUNTIME
        self.assertEqual(runtime["max_action_sessions"], 24)
        before = runtime["max_action_sessions"]
        try:
            runtime["max_action_sessions"] = self.mod.server_mod.action_session_count()
            status, body = self.call("/api/decide", {"choice": "KEEP_UNKNOWN"})
            self.assertEqual(status, 429)
            self.assertIn("action limit", body["error"])
        finally:
            runtime["max_action_sessions"] = before

    def test_oversized_body_refused(self):
        status, body = self.call("/api/decide", {"choice": "KEEP_UNKNOWN", "pad": "x" * 5000})
        self.assertEqual(status, 400)
        self.assertIn("too large", body["error"])

    def test_local_server_default_profile_unchanged(self):
        spec = importlib.util.spec_from_file_location("collider_local_server_default", ROOT / "demo-ui/server.py")
        local = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local)
        self.assertEqual(local.RUNTIME, {
            "execution_environment": "LOCAL", "human_decision_source": "INTERACTIVE_LOCAL_UI",
            "max_action_sessions": None,
        })
        with self.assertRaises(ValueError):
            local.configure("LIVE_BOB")


class TestProvenanceMapping(unittest.TestCase):

    def test_live_bob_is_not_an_execution_environment(self):
        tmp = Path(tempfile.mkdtemp(prefix="collider-prov-"))
        try:
            with self.assertRaises(ValueError):
                compile_decision("customer_identity", "account_id",
                                 human_decision_source="INTERACTIVE_WEB", decision_id="x",
                                 workspace=tmp / "ws", out_dir=tmp / "out",
                                 execution_environment="LIVE_BOB")
            with self.assertRaises(ValueError):
                record_abstention("customer_identity", human_decision_source="INTERACTIVE_WEB",
                                  action_id="y", out_dir=tmp / "o2",
                                  execution_environment="LIVE_BOB_SESSION")
            with self.assertRaises(ValueError):
                run_guard_probe(tmp, tmp / "o3", execution_environment="LIVE_BOB")
            self.assertFalse((tmp / "ws").exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @unittest.skipIf(NODE is None, "node required")
    def test_ui_labels_follow_reported_environment(self):
        script = (
            f"const L = require({json.dumps(str(ROOT / 'demo-ui/loop-state.js'))});"
            "const j = (p) => [p.label, ...p.detail].join(' · ');"
            "let unknown = null; try { L.provenance('ACTIVE', 'LIVE_BOB'); } catch (e) { unknown = 'threw'; }"
            "process.stdout.write(JSON.stringify({"
            " local: j(L.provenance('ACTIVE')),"
            " localExplicit: j(L.provenance('ACTIVE', 'LOCAL')),"
            " cloud: j(L.provenance('ACTIVE', 'CLOUDFLARE_CONTAINER')),"
            " evidence: j(L.provenance('EVIDENCE', 'CLOUDFLARE_CONTAINER')),"
            " unknown }));"
        )
        o = json.loads(subprocess.run([NODE, "-e", script], capture_output=True, text=True, check=True).stdout)
        self.assertEqual(o["local"], "LOCAL ACTIVE DEMO · PRESEEDED INTERPRETATIONS · INTERACTIVE HUMAN DECISION")
        self.assertEqual(o["localExplicit"], o["local"])
        self.assertEqual(o["cloud"], "CLOUDFLARE CONTAINER ACTIVE DEMO · PRESEEDED INTERPRETATIONS · INTERACTIVE WEB DECISION")
        self.assertEqual(o["evidence"], "COMMITTED EVIDENCE · LOCAL / PRESEEDED")
        self.assertEqual(o["unknown"], "threw")
        for label in (o["cloud"], o["local"]):
            self.assertNotIn("LIVE_BOB", label)
            self.assertNotIn("COMMITTED", label)
        self.assertNotIn("LOCAL", o["cloud"])


# ---------------------------------------------------------------------------
# Deployment configuration
# ---------------------------------------------------------------------------

class TestDeploymentConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cfg = load_jsonc(ROOT / "wrangler.jsonc")

    def test_wrangler_core(self):
        c = self.cfg
        self.assertEqual(c["name"], "collider-semantic-ci")
        self.assertEqual(c["main"], "src/index.ts")
        self.assertEqual(c["assets"]["directory"], "./demo-ui")
        self.assertEqual(c["assets"]["binding"], "ASSETS")
        self.assertEqual(c["assets"]["run_worker_first"], ["/api/*"])

    def test_wrangler_container_and_durable_object(self):
        c = self.cfg
        [container] = c["containers"]
        self.assertEqual(container["class_name"], "ColliderContainer")
        self.assertEqual(container["image"], "./Dockerfile")
        self.assertEqual(c["durable_objects"]["bindings"],
                         [{"name": "COLLIDER", "class_name": "ColliderContainer"}])
        self.assertIn("ColliderContainer", c["migrations"][0]["new_sqlite_classes"])

    def test_no_secrets_or_account_binding_in_repo(self):
        for rel in ("wrangler.jsonc", "package.json", "Dockerfile", "src/index.ts", "src/router.ts",
                    "cloudflare/container_server.py"):
            text = (ROOT / rel).read_text()
            for needle in ("CLOUDFLARE_API_TOKEN", "api_token", "account_id", "Bearer "):
                self.assertNotIn(needle, text, f"{needle} in {rel}")
        self.assertNotIn("vars", self.cfg)

    def test_frontend_has_no_deployment_urls(self):
        for rel in ("demo-ui/app.js", "demo-ui/index.html", "demo-ui/loop-state.js"):
            text = (ROOT / rel).read_text()
            self.assertNotIn("workers.dev", text)
            self.assertNotIn("127.0.0.1", text)

    def test_pages_ship_a_strict_security_policy(self):
        text = (ROOT / "demo-ui/_headers").read_text()
        self.assertIn("/*", text)
        for directive in ("default-src 'none'", "script-src 'self'", "style-src 'self'",
                          "connect-src 'self'", "frame-ancestors 'none'", "base-uri 'none'"):
            self.assertIn(directive, text)
        self.assertNotIn("unsafe-inline", text)
        self.assertNotIn("unsafe-eval", text)
        self.assertNotIn("_headers", (ROOT / "demo-ui/.assetsignore").read_text())

    def test_frontend_is_compatible_with_the_policy(self):
        html = (ROOT / "demo-ui/index.html").read_text()
        self.assertNotRegex(html, r"<script(?![^>]*\bsrc=)")  # no inline scripts
        self.assertNotIn(" style=", html)
        self.assertNotIn("style=", (ROOT / "demo-ui/app.js").read_text())
        for rel in ("demo-ui/index.html", "demo-ui/styles.css", "demo-ui/app.js"):
            self.assertNotRegex((ROOT / rel).read_text(), r"https?://(?!www\.w3\.org)")

    def test_local_server_applies_the_same_page_policy(self):
        spec = importlib.util.spec_from_file_location("collider_local_server_headers", ROOT / "demo-ui/server.py")
        local = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local)
        names = [n for n, _ in local.PAGE_HEADERS]
        self.assertIn("Content-Security-Policy", names)
        self.assertIn("X-Frame-Options", names)
        csp = dict(local.PAGE_HEADERS)["Content-Security-Policy"]
        self.assertIn("default-src 'none'", csp)
        # The API-only container image does not ship demo-ui/_headers.
        self.assertEqual(local.load_page_headers(ROOT / "demo-ui/_no_such_headers"), [])
        self.assertNotIn("_headers", (ROOT / ".dockerignore").read_text())

    def test_static_assets_exclude_server_files(self):
        ignored = (ROOT / "demo-ui/.assetsignore").read_text().split()
        for name in ("server.py", "build_demo_data.py", "README.md"):
            self.assertIn(name, ignored)

    def test_image_contains_runtime_only_and_no_runtime_output(self):
        docker = (ROOT / "Dockerfile").read_text()
        self.assertIn("EXPOSE 8080", docker)
        self.assertIn('CMD ["python3", "cloudflare/container_server.py"]', docker)
        self.assertIn("USER collider", docker)
        copies = re.findall(r"^COPY (\S+)", docker, flags=re.M)
        for src in copies:
            self.assertFalse(src.startswith((".collider", "evidence", "tests", ".git")), src)
        ignore = (ROOT / ".dockerignore").read_text().splitlines()
        self.assertEqual(ignore[ignore.index("*")], "*")
        self.assertIn(".collider/", ignore)
        self.assertNotIn("!evidence/", ignore)


if __name__ == "__main__":
    unittest.main()
