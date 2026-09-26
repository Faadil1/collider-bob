"""
Semantic CI loop tests — DECIDE → COMPILE → PATCH → VERIFY → REMEMBER → GUARD,
plus the fresh-agent REPLAY contract and the local action server.

Every compile here writes to a temporary workspace / receipt directory. The
committed tree must be byte-identical before and after.
"""

import importlib.util
import json
import re
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from collider import gate as gate_mod
from collider.decision_compiler import compile_decision
from collider.replay import (
    REQUIRED_RESULT_FIELDS,
    build_replay_request,
    evaluate_replay_result,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "evidence/decisions/decision-001"


def tree_snapshot(root: Path) -> dict:
    rels = list(gate_mod.WORKSTREAM_FILES.values()) + [gate_mod.BRIEF_RELPATH]
    return {rel: (root / rel).read_bytes() for rel in rels}


def set_constant(path: Path, name: str, value: str) -> None:
    text = path.read_text()
    path.write_text(re.sub(rf'^({name}\s*=\s*)"[^"]*"', rf'\1"{value}"', text, flags=re.M))


class CompiledCase(unittest.TestCase):
    """Compile the canonical demo decision once into a temp workspace."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="collider-sci-"))
        cls.source_before = tree_snapshot(ROOT)
        cls.result = compile_decision(
            "customer_identity", "account_id",
            human_decision_source="CLI_OPERATOR",
            decision_id="test-decision",
            workspace=cls.tmp / "ws",
            out_dir=cls.tmp / "out",
        )
        cls.ws = Path(cls.result["workspace"])
        cls.out = Path(cls.result["out_dir"])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def clone(self, name: str) -> Path:
        dst = self.tmp / name
        shutil.copytree(self.ws, dst)
        return dst


# ---------------------------------------------------------------------------
# GUARD
# ---------------------------------------------------------------------------

class TestGateOnCommittedTree(unittest.TestCase):

    def test_committed_tree_requires_decision(self):
        g = gate_mod.evaluate_gate(ROOT)
        self.assertEqual(g["verdict"], "DECISION_REQUIRED")
        self.assertFalse(g["passed"])
        self.assertEqual({f["kind"] for f in g["findings"]}, {"SPEC_GAP", "AGENT_DRIFT"})
        self.assertEqual(g["integration"]["conflict_count"], 2)
        self.assertEqual(g["canon_resolved"], [])
        self.assertIsNone(g["verification"])

    def test_spec_gap_finding_carries_candidates_and_question(self):
        g = gate_mod.evaluate_gate(ROOT)
        gap = next(f for f in g["findings"] if f["kind"] == "SPEC_GAP")
        self.assertEqual(gap["candidates"], {"api": "email", "ledger": "account_id"})
        self.assertEqual(gap["epistemic_state"], "UNKNOWN")
        self.assertIn("account_id", gap["question"])

    def test_explicit_source_drift_is_reported_alongside(self):
        g = gate_mod.evaluate_gate(ROOT)
        drift = next(f for f in g["findings"] if f["kind"] == "AGENT_DRIFT")
        self.assertEqual(drift["concept"], "field_name")
        self.assertEqual(drift["authority"], "EXPLICIT_SOURCE")
        self.assertEqual(drift["violations"], {"ledger": "credit_amount"})

    def test_gate_is_deterministic(self):
        a = gate_mod.evaluate_gate(ROOT)
        b = gate_mod.evaluate_gate(ROOT)
        self.assertEqual(a["verdict"], b["verdict"])
        self.assertEqual(a["findings"], b["findings"])


class TestGateOnCompiledTree(CompiledCase):

    def test_compiled_tree_is_semantically_ready(self):
        g = gate_mod.evaluate_gate(self.ws)
        self.assertEqual(g["verdict"], "SEMANTICALLY_READY")
        self.assertEqual(g["findings"], [])
        self.assertEqual(g["canon_resolved"], ["customer_identity"])
        self.assertEqual(g["integration"]["conflict_count"], 0)
        self.assertEqual(g["verification"]["failed_count"], 0)
        # 30 workstream behavioral tests + 7 regression-contract tests.
        self.assertEqual(g["verification"]["passed_count"], 37)
        self.assertEqual(
            g["verification"]["contract_files"],
            ["contracts/test_canon_customer_identity.py"],
        )

    def test_regressed_dependent_is_agent_drift_against_canon(self):
        ws = self.clone("regress-api")
        set_constant(ws / "api/handlers/recover.py", "CUSTOMER_IDENTITY_FIELD", "email")
        g = gate_mod.evaluate_gate(ws)
        self.assertEqual(g["verdict"], "AGENT_DRIFT")
        drift = g["findings"][0]
        self.assertEqual(drift["concept"], "customer_identity")
        self.assertEqual(drift["authority"], "RESOLVED_CANON")
        self.assertEqual(drift["violations"], {"api": "email"})

    def test_regression_contract_catches_the_regression(self):
        ws = self.clone("regress-contract")
        set_constant(ws / "api/handlers/recover.py", "CUSTOMER_IDENTITY_FIELD", "email")
        v = gate_mod.run_verification(ws)
        self.assertFalse(v["passed"])
        self.assertGreater(v["failed_count"], 0)

    def test_reintroduced_money_drift_is_explicit_source_drift(self):
        ws = self.clone("regress-ledger")
        set_constant(ws / "ledger/credit_entry.py", "CREDIT_FIELD_NAME", "credit_amount")
        g = gate_mod.evaluate_gate(ws)
        self.assertEqual(g["verdict"], "AGENT_DRIFT")
        self.assertEqual(g["findings"][0]["authority"], "EXPLICIT_SOURCE")

    def test_memory_without_spec_patch_is_not_canon(self):
        ws = self.clone("no-spec-marker")
        brief = ws / gate_mod.BRIEF_RELPATH
        brief.write_text(gate_mod.CANON_MARKER_RE.sub("", brief.read_text()))
        set_constant(ws / "api/handlers/recover.py", "CUSTOMER_IDENTITY_FIELD", "email")
        g = gate_mod.evaluate_gate(ws)
        self.assertEqual(g["canon_resolved"], [])
        self.assertEqual(g["verdict"], "DECISION_REQUIRED")

    def test_agreement_without_canon_is_not_ready(self):
        ws = self.clone("agree-no-canon")
        (ws / gate_mod.MEMORY_RELPATH).unlink()
        g = gate_mod.evaluate_gate(ws)
        self.assertEqual(g["verdict"], "DECISION_REQUIRED")
        self.assertEqual(g["findings"][0]["kind"], "SHARED_INFERRED")

    def test_failing_verification_is_never_ready(self):
        ws = self.clone("verify-fail")
        (ws / "contracts/test_zz_failing.py").write_text(
            "def test_fails():\n    assert False\n"
        )
        g = gate_mod.evaluate_gate(ws)
        self.assertEqual(g["verdict"], "VERIFICATION_FAILED")
        self.assertFalse(g["passed"])


# ---------------------------------------------------------------------------
# DECIDE → COMPILE → PATCH → VERIFY → REMEMBER
# ---------------------------------------------------------------------------

class TestDecisionCompiler(CompiledCase):

    def test_committed_tree_untouched(self):
        self.assertEqual(tree_snapshot(ROOT), self.source_before)
        self.assertTrue(self.result["manifest"]["source_tree_untouched"])

    def test_only_affected_workstreams_mutated(self):
        changed = {w["workstream"]: w["changed"] for w in self.result["manifest"]["workstreams"]}
        self.assertEqual(changed, {"api": True, "ledger": True, "notifications": False})
        self.assertEqual(
            (self.ws / "notifications/send_credit_notice.py").read_bytes(),
            (ROOT / "notifications/send_credit_notice.py").read_bytes(),
        )

    def test_repair_sources_are_separated(self):
        repaired = {
            (r["workstream"], r["concept"]): r["repair_source"]
            for r in self.result["repairs"] if r["action"] == "repaired"
        }
        self.assertEqual(repaired, {
            ("api", "customer_identity"): "CANON_PATCH",
            ("ledger", "field_name"): "AGENT_DRIFT_EVIDENCE",
        })

    def test_diff_exposes_targeted_repair(self):
        patch = self.result["repair_patch"]
        self.assertIn('-CUSTOMER_IDENTITY_FIELD = "email"', patch)
        self.assertIn('+CUSTOMER_IDENTITY_FIELD = "account_id"', patch)
        self.assertIn('+CREDIT_FIELD_NAME = "refund_amount"', patch)
        self.assertNotIn("notifications/", patch)

    def test_transition_two_conflicts_to_zero(self):
        m = self.result["manifest"]
        self.assertEqual(m["gate_before"], "DECISION_REQUIRED")
        self.assertEqual(m["gate_after"], "SEMANTICALLY_READY")
        self.assertEqual(m["integration_conflicts_before"], 2)
        self.assertEqual(m["integration_conflicts_after"], 0)
        self.assertEqual(m["integration_status_after"], "INTEGRATION_READY")

    def test_spec_patch_is_machine_readable_and_applied(self):
        sp = self.result["spec_patch"]
        self.assertEqual(sp["target"], gate_mod.BRIEF_RELPATH)
        self.assertEqual(sp["op"], "append_section")
        self.assertNotEqual(sp["sha256_before"], sp["sha256_after"])
        brief = (self.ws / gate_mod.BRIEF_RELPATH).read_text()
        self.assertIn(sp["marker"], brief)
        self.assertNotIn("collider:canon", (ROOT / gate_mod.BRIEF_RELPATH).read_text())

    def test_decision_memory_record(self):
        memory = json.loads((self.ws / gate_mod.MEMORY_RELPATH).read_text())
        rec = memory["decisions"][0]
        self.assertEqual(rec["concept"], "customer_identity")
        self.assertEqual(rec["canonical_value"], "account_id")
        self.assertEqual(rec["decision_source"], "human")
        self.assertEqual(rec["human_decision_source"], "CLI_OPERATOR")
        self.assertEqual(rec["affected_dependents"], ["api", "ledger"])
        self.assertEqual(rec["unaffected_workstreams"], ["notifications"])
        self.assertTrue((self.ws / rec["spec_patch_ref"]).exists())
        self.assertTrue((self.ws / rec["regression_artifact_ref"]).exists())
        self.assertTrue((self.ws / rec["decision_ref"]).exists())
        self.assertEqual(rec["evidence_state"], "OBSERVED")
        self.assertEqual(rec["provenance"]["execution_environment"], "LOCAL")
        self.assertEqual(rec["provenance"]["interpretation_source"], "PRESEEDED")
        self.assertEqual(rec["replay"], {
            "status": "NOT_EXECUTED", "runtime_state": "PENDING_LIVE_BOB",
        })

    def test_receipts_written(self):
        for name in [
            "manifest.json", "decision.json", "spec-patch.json", "spec.diff",
            "repair.patch", "impact-set.json", "repairs.json",
            "test_canon_customer_identity.py", "decision-memory.json",
            "gate-before.json", "gate-after.json", "verification.txt",
            "replay-contract.json",
        ]:
            self.assertTrue((self.out / name).exists(), name)

    def test_truth_boundary_in_manifest(self):
        tb = self.result["manifest"]["truth_boundary"]
        self.assertEqual(tb["execution"], "LOCAL")
        self.assertEqual(tb["interpretations"], "PRESEEDED")
        self.assertEqual(tb["fresh_agent_replay"], "NOT_EXECUTED / PENDING_LIVE_BOB")
        self.assertEqual(tb["wall_clock_improvement"], "NOT_MEASURED")
        self.assertEqual(tb["percentage_improvement"], "NOT_CLAIMED")
        self.assertFalse(tb["canonical_evidence_modified"])

    def test_resolved_tree_refuses_second_decision(self):
        with self.assertRaises(RuntimeError):
            compile_decision(
                "customer_identity", "account_id",
                human_decision_source="CLI_OPERATOR",
                decision_id="again",
                source_root=self.ws,
                workspace=self.tmp / "again-ws",
                out_dir=self.tmp / "again-out",
            )

    def test_refuses_existing_receipt_dir(self):
        with self.assertRaises(FileExistsError):
            compile_decision(
                "customer_identity", "account_id",
                human_decision_source="CLI_OPERATOR",
                decision_id="dup",
                workspace=self.tmp / "dup-ws",
                out_dir=self.out,
            )


class TestDecisionCompilerRefusals(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="collider-refuse-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def compile(self, value, **kw):
        return compile_decision(
            kw.pop("concept", "customer_identity"), value,
            human_decision_source=kw.pop("source", "CLI_OPERATOR"),
            decision_id="refusal",
            workspace=self.tmp / "ws", out_dir=self.tmp / "out",
        )

    def test_refuses_value_no_agent_proposed(self):
        with self.assertRaises(ValueError):
            self.compile("phone")
        self.assertFalse((self.tmp / "ws").exists())

    def test_refuses_unknown_decision_source(self):
        with self.assertRaises(ValueError):
            self.compile("account_id", source="LIVE_BOB")

    def test_refuses_uncompilable_concept(self):
        with self.assertRaises(ValueError):
            self.compile("integer_cents", concept="money_representation")

    def test_non_canonical_choice_is_reported_not_ready(self):
        result = self.compile("email")
        m = result["manifest"]
        # Ledger has no targeted repair for this value: the gate says so.
        self.assertEqual(m["gate_after"], "AGENT_DRIFT")
        self.assertEqual(m["integration_conflicts_after"], 1)
        self.assertEqual(result["memory"]["evidence_state"], "UNVERIFIED")
        ledger = next(
            r for r in result["repairs"]
            if r["workstream"] == "ledger" and r["concept"] == "customer_identity"
        )
        self.assertEqual(ledger["action"], "repair_not_implemented")


# ---------------------------------------------------------------------------
# REPLAY contract
# ---------------------------------------------------------------------------

class TestReplayContract(unittest.TestCase):

    RECORD = {
        "decision_id": "d", "concept": "customer_identity",
        "canonical_value": "account_id", "affected_dependents": ["api", "ledger"],
    }

    def request(self):
        return build_replay_request(self.RECORD, "BRIEF.md", "contracts/t.py")

    def test_request_is_not_executed(self):
        r = self.request()
        self.assertEqual(r["status"], "NOT_EXECUTED")
        self.assertEqual(r["runtime_state"], "PENDING_LIVE_BOB")
        self.assertIsNone(r["result"])
        self.assertIn("repaired implementation files", r["inputs"]["withheld"])

    def test_no_result_stays_not_executed(self):
        v = evaluate_replay_result(self.request(), None, "account_id")
        self.assertEqual(v["status"], "NOT_EXECUTED")
        self.assertFalse(v["accepted"])

    def test_local_self_replay_is_rejected(self):
        fake = {f: "x" for f in REQUIRED_RESULT_FIELDS}
        fake.update(execution_source="LOCAL", emitted_value="account_id", tests_passed=True)
        v = evaluate_replay_result(self.request(), fake, "account_id")
        self.assertEqual(v["status"], "REJECTED")
        self.assertFalse(v["accepted"])

    def test_incomplete_result_is_rejected(self):
        v = evaluate_replay_result(
            self.request(),
            {"execution_source": "LIVE_BOB_SESSION", "emitted_value": "account_id"},
            "account_id",
        )
        self.assertEqual(v["status"], "REJECTED")

    def test_contract_logic_for_independent_result(self):
        # Unit test of the acceptance rule only; not evidence of a replay.
        res = {f: "ref" for f in REQUIRED_RESULT_FIELDS}
        res.update(execution_source="LIVE_BOB_SESSION", emitted_value="email", tests_passed=True)
        self.assertEqual(
            evaluate_replay_result(self.request(), res, "account_id")["status"],
            "REPLAY_FAIL",
        )


# ---------------------------------------------------------------------------
# Committed decision receipt
# ---------------------------------------------------------------------------

class TestCommittedDecisionReceipt(unittest.TestCase):

    def load(self, name):
        return json.loads((RECEIPT / name).read_text())

    def test_receipt_invariants(self):
        m = self.load("manifest.json")
        self.assertEqual(m["gate_before"], "DECISION_REQUIRED")
        self.assertEqual(m["gate_after"], "SEMANTICALLY_READY")
        self.assertEqual((m["integration_conflicts_before"], m["integration_conflicts_after"]), (2, 0))
        self.assertTrue(m["source_tree_untouched"])
        self.assertEqual(m["truth_boundary"]["human_decision"], "PRESEEDED")
        self.assertFalse(m["truth_boundary"]["canonical_evidence_modified"])

    def test_receipt_replay_not_executed(self):
        r = self.load("replay-contract.json")
        self.assertEqual((r["status"], r["runtime_state"]), ("NOT_EXECUTED", "PENDING_LIVE_BOB"))
        self.assertIsNone(r["result"])

    def test_receipt_contract_matches_generator(self):
        from collider.decision_compiler import contract_source
        decision = self.load("decision.json")
        self.assertEqual(
            (RECEIPT / "test_canon_customer_identity.py").read_text(),
            contract_source(decision),
        )


# ---------------------------------------------------------------------------
# Local action server
# ---------------------------------------------------------------------------

class TestActionServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "collider_demo_server", ROOT / "demo-ui/server.py"
        )
        cls.server_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.server_mod)
        cls.tmp = Path(tempfile.mkdtemp(prefix="collider-srv-"))
        cls.server_mod.RUNS_DIR = cls.tmp / "runs"
        cls.server_mod.WORKSPACES_DIR = cls.tmp / "workspaces"
        cls.httpd = cls.server_mod.HTTPServer(("127.0.0.1", 0), cls.server_mod.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

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
            with urllib.request.urlopen(req, timeout=60) as res:
                return res.status, json.loads(res.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_state_reports_decision_required(self):
        status, body = self.call("/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(body["gate"]["verdict"], "DECISION_REQUIRED")

    def test_decide_compiles_for_real(self):
        status, body = self.call("/api/decide", {"choice": "USE_ACCOUNT_ID"})
        self.assertEqual(status, 200)
        self.assertEqual(body["decision"]["human_decision_source"], "INTERACTIVE_LOCAL_UI")
        self.assertEqual(body["gate_after"]["verdict"], "SEMANTICALLY_READY")
        self.assertEqual(body["manifest"]["integration_conflicts_after"], 0)
        self.assertIn('+CUSTOMER_IDENTITY_FIELD = "account_id"', body["repair_patch"])
        decision_id = body["decision"]["decision_id"]
        status, g = self.call(f"/api/gate?decision={decision_id}")
        self.assertEqual((status, g["verdict"]), (200, "SEMANTICALLY_READY"))

    def test_decide_rejects_arbitrary_values(self):
        for payload in ({"value": "phone"}, {"value": "email"},
                        {"choice": "email"}, {"choice": "USE_EMAIL"}):
            status, body = self.call("/api/decide", payload)
            self.assertEqual(status, 400, payload)
            self.assertIn("REFUSE", body["error"])

    def test_gate_rejects_path_escape(self):
        status, _ = self.call("/api/gate?decision=../../etc")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
