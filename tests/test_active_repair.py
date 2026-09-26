"""
Active Semantic Repair — final interaction delta.

  KEEP UNKNOWN          real abstention: no canon, no repair, DECISION_REQUIRED
  USE account_id        still compiles to SEMANTICALLY_READY
  GUARD                 real future-agent probe (account_id → email) in the
                        compiled workspace: MERGE_BLOCKED, contract fails,
                        exact restoration, SEMANTICALLY_READY again
  loop state            GUARD is never complete before the probe runs
  provenance            ACTIVE and EVIDENCE labels cannot be confused
  isolation             source tree and canonical evidence never change
"""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from collider import gate as gate_mod
from collider.decision_compiler import compile_decision, record_abstention
from collider.guard_probe import PROBE, run_guard_probe

ROOT = Path(__file__).resolve().parents[1]

# Content hashes of committed canonical evidence (sorted path + file sha256).
CANONICAL_EVIDENCE = {
    "evidence/runs/baseline-001":
        "257b1ad3d180552d93d3036860997fef1981321287a4c4c6a0682c58f2345b8d",
    "evidence/runs/local-resolved-004":
        "10f87f63f77c2c5a7baefc48e38411fdfc7f79793a5afe83d6300697cb47457b",
    "evidence/comparisons":
        "5fb3e72bf26b31dd1cad372514235617d4eb2ab181dd7ec52420c39d75081cad",
    "evidence/decisions/decision-001":
        "6ef6c9e91c7d4252defe22148ddd5addfe4db61c8620044d4bfbbab110b132c7",
}


def dir_hash(rel: str) -> str:
    h = hashlib.sha256()
    for p in sorted((ROOT / rel).rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(ROOT)).encode() + b"\0"
                     + hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def source_snapshot() -> dict:
    rels = list(gate_mod.WORKSTREAM_FILES.values()) + [gate_mod.BRIEF_RELPATH]
    return {rel: (ROOT / rel).read_bytes() for rel in rels}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# KEEP UNKNOWN
# ---------------------------------------------------------------------------

class TestKeepUnknown(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="collider-abstain-"))
        cls.before = source_snapshot()
        cls.receipt = record_abstention(
            "customer_identity",
            human_decision_source="CLI_OPERATOR",
            action_id="abstain-test",
            out_dir=cls.tmp / "out",
        )
        cls.after = source_snapshot()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_writes_no_canon(self):
        r = self.receipt
        self.assertIsNone(r["canonical_value"])
        self.assertFalse(r["canon_written"])
        self.assertFalse(r["decision_memory_written"])
        self.assertFalse(r["spec_patch_written"])
        written = sorted(p.name for p in (self.tmp / "out").iterdir())
        self.assertEqual(written, ["abstention.json"])
        self.assertFalse((ROOT / gate_mod.MEMORY_RELPATH).exists())
        self.assertNotIn("collider:canon", (ROOT / gate_mod.BRIEF_RELPATH).read_text())

    def test_performs_no_repair(self):
        self.assertEqual(self.receipt["repairs_applied"], [])
        self.assertEqual(self.before, self.after)
        self.assertTrue(self.receipt["source_tree_untouched"])
        self.assertEqual(
            gate_mod.observe_facts(ROOT)["api_customer_identity_field"], "email"
        )

    def test_remains_decision_required_and_unknown(self):
        r = self.receipt
        self.assertEqual(r["gate_verdict"], "DECISION_REQUIRED")
        self.assertEqual(r["epistemic_state"], "UNKNOWN")
        self.assertIn("SPEC_GAP", {f["kind"] for f in r["gate_findings"]})
        self.assertEqual(r["integration"]["conflict_count"], 2)
        self.assertEqual(gate_mod.evaluate_gate(ROOT)["verdict"], "DECISION_REQUIRED")

    def test_says_so_and_is_not_a_canonical_receipt(self):
        self.assertEqual(self.receipt["message"], "No canon written. No dependent work repaired.")
        self.assertIn("not a canonical decision receipt", self.receipt["receipt_kind"])
        self.assertEqual(self.receipt["human_choice"], "KEEP_UNKNOWN")

    def test_abstention_on_resolved_tree_refused(self):
        tmp = Path(tempfile.mkdtemp(prefix="collider-abstain2-"))
        try:
            res = compile_decision(
                "customer_identity", "account_id",
                human_decision_source="CLI_OPERATOR", decision_id="x",
                workspace=tmp / "ws", out_dir=tmp / "out",
            )
            with self.assertRaises(RuntimeError):
                record_abstention(
                    "customer_identity", human_decision_source="CLI_OPERATOR",
                    action_id="y", source_root=Path(res["workspace"]),
                    out_dir=tmp / "out2",
                )
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# GUARD probe
# ---------------------------------------------------------------------------

class TestGuardProbe(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="collider-guard-"))
        cls.source_before = source_snapshot()
        cls.compiled = compile_decision(
            "customer_identity", "account_id",
            human_decision_source="CLI_OPERATOR",
            decision_id="guard-test",
            workspace=cls.tmp / "ws",
            out_dir=cls.tmp / "out",
        )
        cls.ws = Path(cls.compiled["workspace"])
        cls.out = Path(cls.compiled["out_dir"])
        cls.api = cls.ws / PROBE["affected_file"]
        cls.api_bytes_before = cls.api.read_bytes()
        cls.receipt = run_guard_probe(cls.ws, cls.out)
        cls.source_after = source_snapshot()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_account_id_still_compiles_ready(self):
        self.assertEqual(self.compiled["manifest"]["gate_after"], "SEMANTICALLY_READY")
        self.assertEqual(self.compiled["manifest"]["integration_conflicts_after"], 0)

    def test_reads_actual_decision_memory(self):
        memory = json.loads((self.ws / gate_mod.MEMORY_RELPATH).read_text())
        record = memory["decisions"][0]
        self.assertEqual(self.receipt["decision_id"], record["decision_id"])
        self.assertEqual(self.receipt["decision_id"], "guard-test")
        self.assertEqual(self.receipt["decision_memory_value"], record["canonical_value"])
        self.assertEqual(self.receipt["regression_contract"], record["regression_artifact_ref"])

    def test_actually_mutates_api_account_id_to_email(self):
        r = self.receipt
        self.assertEqual((r["canonical_value"], r["attempted_value"]), ("account_id", "email"))
        self.assertEqual(r["affected_file"], "api/handlers/recover.py")
        self.assertNotEqual(r["sha_during_probe"], r["sha_before_probe"])
        self.assertIn('-CUSTOMER_IDENTITY_FIELD = "account_id"', r["probe_diff"])
        self.assertIn('+CUSTOMER_IDENTITY_FIELD = "email"', r["probe_diff"])
        mutated = self.api_bytes_before.decode().replace(
            'CUSTOMER_IDENTITY_FIELD = "account_id"', 'CUSTOMER_IDENTITY_FIELD = "email"', 1
        ).encode()
        self.assertEqual(r["sha_during_probe"], hashlib.sha256(mutated).hexdigest())

    def test_gate_during_probe_is_agent_drift_against_resolved_canon(self):
        r = self.receipt
        self.assertEqual(r["gate_during_probe"], "AGENT_DRIFT")
        v = r["violation"]
        self.assertEqual(v["kind"], "AGENT_DRIFT")
        self.assertEqual(v["concept"], "customer_identity")
        self.assertEqual(v["authority"], "RESOLVED_CANON")
        self.assertEqual(v["expected"], "account_id")
        self.assertEqual(v["violations"], {"api": "email"})
        self.assertEqual(r["integration_during_probe"]["conflict_count"], 1)

    def test_guard_verdict_is_merge_blocked(self):
        self.assertEqual(self.receipt["guard_verdict"], "MERGE_BLOCKED")

    def test_regression_contract_fails_during_violation(self):
        c = self.receipt["verification_during_probe"]["regression_contract"]
        self.assertFalse(c["passed"])
        self.assertGreater(c["failed_count"], 0)
        self.assertIn("contracts/test_canon_customer_identity.py", c["command"])
        self.assertFalse(self.receipt["verification_during_probe"]["full_suite"]["passed"])

    def test_restores_exact_prior_repaired_source(self):
        r = self.receipt
        self.assertTrue(r["restoration_applied"])
        self.assertTrue(r["restored_exact_bytes"])
        self.assertEqual(self.api.read_bytes(), self.api_bytes_before)
        self.assertEqual(r["sha_before_probe"], sha(self.api))
        self.assertEqual(r["sha_after_restore"], r["sha_before_probe"])

    def test_gate_after_restore_is_ready_with_zero_conflicts(self):
        r = self.receipt
        self.assertEqual(r["gate_after_restore"], "SEMANTICALLY_READY")
        self.assertEqual(r["integration_after_restore"]["conflict_count"], 0)
        self.assertTrue(r["verification_after_restore"]["regression_contract"]["passed"])
        self.assertEqual(r["verification_after_restore"]["regression_contract"]["failed_count"], 0)
        self.assertTrue(r["restoration_verified"])
        self.assertEqual(gate_mod.evaluate_gate(self.ws)["verdict"], "SEMANTICALLY_READY")

    def test_receipt_file_contains_real_hashes_and_verdicts(self):
        on_disk = json.loads((self.out / "guard-probe.json").read_text())
        for key in (
            "decision_id", "concept", "canonical_value", "attempted_value",
            "affected_file", "sha_before_probe", "sha_during_probe",
            "gate_during_probe", "verification_during_probe", "guard_verdict",
            "restoration_applied", "sha_after_restore", "gate_after_restore",
            "restoration_verified",
        ):
            self.assertIn(key, on_disk)
            self.assertEqual(on_disk[key], self.receipt[key])
        for key in ("sha_before_probe", "sha_during_probe", "sha_after_restore"):
            self.assertRegex(on_disk[key], r"^[0-9a-f]{64}$")

    def test_guard_is_not_the_replay(self):
        self.assertFalse(self.receipt["is_fresh_agent_replay"])
        self.assertEqual(
            self.receipt["truth_boundary"]["fresh_agent_replay"],
            "NOT_EXECUTED / PENDING_LIVE_BOB",
        )
        memory = json.loads((self.ws / gate_mod.MEMORY_RELPATH).read_text())
        self.assertEqual(memory["decisions"][0]["replay"],
                         {"status": "NOT_EXECUTED", "runtime_state": "PENDING_LIVE_BOB"})

    def test_source_tree_untouched(self):
        self.assertEqual(self.source_before, self.source_after)
        self.assertTrue(self.receipt["source_tree_untouched"])

    def test_second_probe_refused(self):
        with self.assertRaises(FileExistsError):
            run_guard_probe(self.ws, self.out)

    def test_probe_refuses_source_tree(self):
        with self.assertRaises((ValueError, RuntimeError)):
            run_guard_probe(ROOT, self.tmp / "src-probe")

    def test_probe_refuses_unready_workspace(self):
        ws = self.tmp / "unready"
        shutil.copytree(self.ws, ws)
        (ws / "contracts/test_zz_fail.py").write_text("def test_x():\n    assert False\n")
        before = (ws / PROBE["affected_file"]).read_bytes()
        with self.assertRaises(RuntimeError):
            run_guard_probe(ws, self.tmp / "unready-out")
        self.assertEqual((ws / PROBE["affected_file"]).read_bytes(), before)


# ---------------------------------------------------------------------------
# Isolation
# ---------------------------------------------------------------------------

class TestIsolation(unittest.TestCase):

    def test_canonical_evidence_untouched(self):
        for rel, expected in CANONICAL_EVIDENCE.items():
            self.assertEqual(dir_hash(rel), expected, rel)

    def test_committed_tree_is_pre_decision(self):
        self.assertFalse((ROOT / "canon").exists())
        self.assertFalse((ROOT / "contracts").exists())
        facts = gate_mod.observe_facts(ROOT)
        self.assertEqual(facts["api_customer_identity_field"], "email")
        self.assertEqual(facts["ledger_money_field"], "credit_amount")


# ---------------------------------------------------------------------------
# UI loop state + provenance (demo-ui/loop-state.js, executed in node)
# ---------------------------------------------------------------------------

NODE = shutil.which("node")


def run_node(expr: str):
    script = (
        f"const L = require({json.dumps(str(ROOT / 'demo-ui/loop-state.js'))});"
        f"process.stdout.write(JSON.stringify({expr}));"
    )
    out = subprocess.run([NODE, "-e", script], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


@unittest.skipIf(NODE is None, "node is required to execute demo-ui/loop-state.js")
class TestLoopState(unittest.TestCase):

    READY = '{gate_after: {verdict: "SEMANTICALLY_READY"}}'
    GUARD_OK = ('{guard_verdict: "MERGE_BLOCKED", restoration_verified: true, '
                'gate_after_restore: "SEMANTICALLY_READY"}')

    def test_guard_waiting_after_compile(self):
        s = run_node(f'L.loopState({{mode: "ACTIVE", decision: {self.READY}}})')
        for n in ("DECIDE", "COMPILE", "PATCH", "VERIFY", "REMEMBER"):
            self.assertEqual(s[n], "done", n)
        self.assertEqual(s["GUARD"], "waiting")

    def test_guard_done_only_after_probe(self):
        s = run_node(
            f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, guard: {self.GUARD_OK}}})'
        )
        self.assertEqual(s["GUARD"], "done")

    def test_guard_failed_probe_is_not_done(self):
        s = run_node(
            f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, '
            f'guard: {{guard_verdict: "GUARD_DID_NOT_BLOCK", restoration_verified: true, '
            f'gate_after_restore: "SEMANTICALLY_READY"}}}})'
        )
        self.assertEqual(s["GUARD"], "failed")

    def test_guard_never_done_in_evidence_mode_without_probe(self):
        s = run_node(f'L.loopState({{mode: "EVIDENCE", decision: {self.READY}}})')
        self.assertEqual(s["GUARD"], "not-in-evidence")

    def test_keep_unknown_skips_everything(self):
        s = run_node('L.loopState({mode: "ACTIVE", abstention: {gate_verdict: "DECISION_REQUIRED"}})')
        self.assertEqual(s["DECIDE"], "abstained")
        for n in ("COMPILE", "PATCH", "VERIFY", "REMEMBER"):
            self.assertEqual(s[n], "skipped")
        self.assertNotEqual(s["GUARD"], "done")

    def test_no_decision_is_waiting_on_human(self):
        s = run_node('L.loopState({mode: "ACTIVE"})')
        self.assertEqual(s["DECIDE"], "waiting")
        self.assertEqual(s["GUARD"], "idle")

    def test_replay_always_pending(self):
        for state in ('{mode: "ACTIVE"}',
                      f'{{mode: "ACTIVE", decision: {self.READY}, guard: {self.GUARD_OK}}}'):
            self.assertEqual(run_node(f"L.loopState({state})")["REPLAY"], "pending")

    def test_provenance_labels_cannot_be_confused(self):
        p = run_node("L.PROVENANCE")
        active = " ".join([p["ACTIVE"]["label"], *p["ACTIVE"]["detail"]])
        evidence = " ".join([p["EVIDENCE"]["label"], *p["EVIDENCE"]["detail"]])
        self.assertEqual(active, "LOCAL ACTIVE DEMO PRESEEDED INTERPRETATIONS INTERACTIVE HUMAN DECISION")
        self.assertEqual(evidence, "COMMITTED EVIDENCE LOCAL / PRESEEDED")
        self.assertNotIn("INTERACTIVE", evidence)
        self.assertNotIn("ACTIVE DEMO", evidence)
        self.assertNotIn("COMMITTED", active)

    def test_results_only_render_in_their_own_mode(self):
        self.assertEqual(
            run_node('[L.acceptsResult("ACTIVE", {provenance_mode: "ACTIVE"}),'
                     ' L.acceptsResult("EVIDENCE", {provenance_mode: "ACTIVE"}),'
                     ' L.acceptsResult("ACTIVE", {provenance_mode: "EVIDENCE"}),'
                     ' L.acceptsResult("ACTIVE", {})]'),
            [True, False, False, False],
        )

    # --- display synchronization (guard timing fix) -----------------------

    def guard_at(self, phase):
        return run_node(
            f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, '
            f'guard: {self.GUARD_OK}, guardPhase: {phase}}}).GUARD'
        )

    def test_guard_rail_follows_displayed_phase(self):
        # The receipt is complete in every case; only the displayed phase moves.
        self.assertEqual(self.guard_at(0), "running")
        self.assertEqual(self.guard_at(1), "violation")
        self.assertEqual(self.guard_at(2), "violation")
        self.assertEqual(self.guard_at(3), "restoring")
        self.assertEqual(self.guard_at(4), "done")

    def test_guard_not_done_while_merge_blocked_is_displayed(self):
        self.assertNotEqual(self.guard_at(2), "done")

    def test_guard_running_before_receipt(self):
        s = run_node(f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, guardRunning: true}})')
        self.assertEqual(s["GUARD"], "running")

    def test_failed_guard_never_done_even_when_fully_displayed(self):
        s = run_node(
            f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, guardPhase: 4, '
            f'guard: {{guard_verdict: "GUARD_DID_NOT_BLOCK", restoration_verified: true, '
            f'gate_after_restore: "SEMANTICALLY_READY"}}}})'
        )
        self.assertEqual(s["GUARD"], "failed")

    def test_compile_rail_follows_revealed_checklist(self):
        partial = run_node(f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, compileRevealed: 2}})')
        self.assertEqual(partial["DECIDE"], "done")
        self.assertEqual(partial["COMPILE"], "done")
        self.assertEqual(partial["PATCH"], "running")
        self.assertEqual(partial["VERIFY"], "idle")
        self.assertEqual(partial["GUARD"], "idle")
        full = run_node(
            f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, compileRevealed: L.COMPILE_ITEMS}})'
        )
        for n in ("DECIDE", "COMPILE", "PATCH", "VERIFY", "REMEMBER"):
            self.assertEqual(full[n], "done", n)
        self.assertEqual(full["GUARD"], "waiting")

    def test_display_params_default_to_fully_revealed(self):
        with_defaults = run_node(
            f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, guard: {self.GUARD_OK}}})'
        )
        explicit = run_node(
            f'L.loopState({{mode: "ACTIVE", decision: {self.READY}, guard: {self.GUARD_OK}, '
            f'compileRevealed: L.COMPILE_ITEMS, guardPhase: 4}})'
        )
        self.assertEqual(with_defaults, explicit)

    def test_committed_receipt_is_evidence_provenance(self):
        data = json.loads((ROOT / "demo-ui/evidence.json").read_text())
        self.assertEqual(data["decisionReceipt"]["provenance_mode"], "EVIDENCE")


# ---------------------------------------------------------------------------
# Frontend portability: same-origin, relative API calls only
# ---------------------------------------------------------------------------

class TestFrontendPortability(unittest.TestCase):

    FILES = ["demo-ui/app.js", "demo-ui/loop-state.js", "demo-ui/index.html"]

    def test_no_hard_coded_hosts(self):
        for rel in self.FILES:
            text = (ROOT / rel).read_text()
            for host in ("127.0.0.1", "localhost", "github.dev", "app.github.dev", "codespaces"):
                self.assertNotIn(host, text, f"{host} in {rel}")

    def test_api_calls_are_relative(self):
        app = (ROOT / "demo-ui/app.js").read_text()
        for endpoint in ("api/state", "api/decide", "api/guard"):
            self.assertIn(f'"./{endpoint}"', app)
        self.assertNotRegex(app, r'fetch\(\s*["\']https?://')
        self.assertNotRegex(app, r'["\']https?://[^"\']*/api/')


# ---------------------------------------------------------------------------
# Server: /api/decide choices + /api/guard
# ---------------------------------------------------------------------------

class TestActiveServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "collider_demo_server_active", ROOT / "demo-ui/server.py"
        )
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)
        cls.tmp = Path(tempfile.mkdtemp(prefix="collider-active-srv-"))
        cls.mod.RUNS_DIR = cls.tmp / "runs"
        cls.mod.WORKSPACES_DIR = cls.tmp / "workspaces"
        cls.httpd = cls.mod.HTTPServer(("127.0.0.1", 0), cls.mod.Handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.source_before = source_snapshot()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def call(self, path, body=None):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as res:
                return res.status, json.loads(res.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_state_is_active_provenance(self):
        status, body = self.call("/api/state")
        self.assertEqual((status, body["provenance_mode"]), (200, "ACTIVE"))

    def test_keep_unknown_over_http(self):
        status, body = self.call("/api/decide", {"choice": "KEEP_UNKNOWN"})
        self.assertEqual(status, 200)
        self.assertEqual(body["kind"], "abstention")
        self.assertEqual(body["provenance_mode"], "ACTIVE")
        self.assertEqual(body["gate_verdict"], "DECISION_REQUIRED")
        self.assertFalse(body["canon_written"])
        self.assertEqual(body["message"], "No canon written. No dependent work repaired.")
        # No workspace is created for an abstention, so it cannot be guarded.
        session = body["action_id"]
        self.assertFalse((self.mod.WORKSPACES_DIR / session).exists())
        status, _ = self.call("/api/guard", {"decision_id": session})
        self.assertEqual(status, 404)
        self.assertEqual(source_snapshot(), self.source_before)

    def test_use_account_id_then_guard_over_http(self):
        status, body = self.call("/api/decide", {"choice": "USE_ACCOUNT_ID"})
        self.assertEqual(status, 200)
        self.assertEqual(body["gate_after"]["verdict"], "SEMANTICALLY_READY")
        session = body["decision"]["decision_id"]

        status, g = self.call("/api/guard", {"decision_id": session})
        self.assertEqual(status, 200)
        self.assertEqual(g["provenance_mode"], "ACTIVE")
        self.assertEqual(g["guard_verdict"], "MERGE_BLOCKED")
        self.assertEqual(g["gate_during_probe"], "AGENT_DRIFT")
        self.assertEqual(g["gate_after_restore"], "SEMANTICALLY_READY")
        self.assertTrue(g["restoration_verified"])
        self.assertTrue((self.mod.RUNS_DIR / session / "guard-probe.json").is_file())

        status, _ = self.call("/api/guard", {"decision_id": session})
        self.assertEqual(status, 409)
        self.assertEqual(source_snapshot(), self.source_before)

    def test_guard_rejects_arbitrary_input(self):
        for payload in (
            {}, {"decision_id": "../../etc"}, {"decision_id": "decision-001"},
            {"decision_id": "ui-20260926T000000000000Z"},
            {"decision_id": ["x"]},
            {"decision_id": "ui-20260926T000000000000Z", "value": "email",
             "path": "api/handlers/recover.py"},
        ):
            status, _ = self.call("/api/guard", payload)
            self.assertEqual(status, 404, payload)


if __name__ == "__main__":
    unittest.main()
