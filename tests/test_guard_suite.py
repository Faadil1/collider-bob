"""
GUARD suite — the Semantic CI gate judging future agent changes against memory.

Covers the concept registry (shared assumptions are disclosed, never upgraded)
and the three fixed future-agent probes:

  IDENTITY_REVERT    violates resolved canon          → MERGE_BLOCKED
  MONEY_UNIT_DRIFT   breaks an unratified assumption  → DECISION_REQUIRED
                     while every behavioral test still passes
  COMPATIBLE_CHANGE  touches no semantic concept      → MERGE_ALLOWED

Each probe records the same diff judged without decision memory. Everything
runs in a temporary compiled workspace; the source tree is never written.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from collider import gate as gate_mod
from collider.concepts import CONCEPTS, ORDER
from collider.decision_compiler import compile_decision
from collider.guard_probe import GUARD_VERDICTS, PROBES, run_guard_probe

ROOT = Path(__file__).resolve().parents[1]


def source_snapshot() -> dict:
    rels = list(gate_mod.WORKSTREAM_FILES.values()) + [gate_mod.BRIEF_RELPATH]
    return {rel: (ROOT / rel).read_bytes() for rel in rels}


class TestConceptRegistry(unittest.TestCase):

    def test_every_concept_is_evaluated_in_a_fixed_order(self):
        self.assertEqual(set(ORDER), set(CONCEPTS))

    def test_identity_is_blocking_money_unit_is_disclosed(self):
        self.assertEqual(CONCEPTS["customer_identity"]["unresolved_agreement"], "BLOCK")
        self.assertEqual(CONCEPTS["money_representation"]["unresolved_agreement"], "DISCLOSE")

    def test_committed_tree_discloses_money_unit_as_inferred(self):
        g = gate_mod.evaluate_gate(ROOT)
        self.assertEqual(g["verdict"], "DECISION_REQUIRED")
        self.assertEqual(len(g["assumptions"]), 1)
        a = g["assumptions"][0]
        self.assertEqual(a["concept"], "money_representation")
        self.assertEqual(a["value"], "integer_cents")
        self.assertEqual(a["epistemic_state"], "INFERRED")
        self.assertTrue(a["consensus"])
        self.assertFalse(a["upgrades_to_fact"])
        self.assertFalse(a["ratified"])
        self.assertFalse(a["blocking"])
        self.assertEqual(a["workstreams"], ["api", "ledger", "notifications"])

    def test_assumption_is_never_a_finding(self):
        g = gate_mod.evaluate_gate(ROOT)
        self.assertNotIn("money_representation", {f["concept"] for f in g["findings"]})


class GuardSuiteCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="collider-guard-suite-"))
        cls.source_before = source_snapshot()
        compiled = compile_decision(
            "customer_identity", "account_id",
            human_decision_source="CLI_OPERATOR",
            decision_id="guard-suite",
            workspace=cls.tmp / "ws",
            out_dir=cls.tmp / "out",
        )
        cls.ws = Path(compiled["workspace"])
        cls.out = Path(compiled["out_dir"])
        cls.bytes_before = {
            pid: (cls.ws / p["affected_file"]).read_bytes() for pid, p in PROBES.items()
        }
        cls.receipts = {
            pid: run_guard_probe(cls.ws, cls.out, probe_id=pid) for pid in PROBES
        }
        cls.source_after = source_snapshot()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)


class TestCompiledTreeAssumptions(GuardSuiteCase):

    def test_ready_tree_still_discloses_the_unratified_money_unit(self):
        g = gate_mod.evaluate_gate(self.ws)
        self.assertEqual(g["verdict"], "SEMANTICALLY_READY")
        self.assertEqual([a["concept"] for a in g["assumptions"]], ["money_representation"])


class TestIdentityRevert(GuardSuiteCase):

    def test_blocked_with_memory(self):
        r = self.receipts["IDENTITY_REVERT"]
        self.assertEqual(r["gate_during_probe"], "AGENT_DRIFT")
        self.assertEqual(r["guard_verdict"], "MERGE_BLOCKED")
        self.assertEqual(r["violation"]["authority"], "RESOLVED_CANON")
        self.assertTrue(r["as_expected"])

    def test_same_diff_without_memory_is_only_a_spec_gap(self):
        r = self.receipts["IDENTITY_REVERT"]
        cf = r["counterfactual_without_memory"]
        self.assertEqual(cf["verdict"], "DECISION_REQUIRED")
        self.assertIn("SPEC_GAP:customer_identity", cf["finding_kinds"])
        self.assertEqual(cf["canon_resolved"], [])
        self.assertTrue(r["memory_changed_verdict"])

    def test_tests_catch_it_too(self):
        s = self.receipts["IDENTITY_REVERT"]["verification_during_probe"]["full_suite"]
        self.assertFalse(s["passed"])


class TestMoneyUnitDrift(GuardSuiteCase):

    def test_every_behavioral_test_still_passes(self):
        r = self.receipts["MONEY_UNIT_DRIFT"]["verification_during_probe"]
        self.assertTrue(r["full_suite"]["passed"])
        self.assertEqual(r["full_suite"]["failed_count"], 0)
        self.assertTrue(r["regression_contract"]["passed"])

    def test_gate_holds_the_merge_for_a_new_decision(self):
        r = self.receipts["MONEY_UNIT_DRIFT"]
        self.assertEqual(r["gate_during_probe"], "DECISION_REQUIRED")
        self.assertEqual(r["guard_verdict"], "DECISION_REQUIRED")
        self.assertTrue(r["as_expected"])
        v = r["violation"]
        self.assertEqual(v["kind"], "SPEC_GAP")
        self.assertEqual(v["concept"], "money_representation")
        self.assertEqual(v["epistemic_state"], "UNKNOWN")
        self.assertEqual(v["candidates"]["ledger"], "decimal_dollars")
        self.assertEqual(v["candidates"]["api"], "integer_cents")
        self.assertIn("decimal dollars", r["surfaced_question"])

    def test_it_is_not_called_drift_because_nothing_was_decided(self):
        r = self.receipts["MONEY_UNIT_DRIFT"]
        self.assertNotIn("AGENT_DRIFT", {f["kind"] for f in r["gate_during_findings"]})
        self.assertEqual(r["gate_during_assumptions"], [])

    def test_memory_does_not_cover_an_undecided_concept(self):
        r = self.receipts["MONEY_UNIT_DRIFT"]
        self.assertEqual(r["counterfactual_without_memory"]["verdict"], "DECISION_REQUIRED")
        self.assertFalse(r["memory_changed_verdict"])


class TestCompatibleChange(GuardSuiteCase):

    def test_allowed_with_memory(self):
        r = self.receipts["COMPATIBLE_CHANGE"]
        self.assertEqual(r["gate_during_probe"], "SEMANTICALLY_READY")
        self.assertEqual(r["guard_verdict"], "MERGE_ALLOWED")
        self.assertIsNone(r["violation"])
        self.assertTrue(r["verification_during_probe"]["full_suite"]["passed"])
        self.assertTrue(r["as_expected"])

    def test_really_changed_the_file(self):
        r = self.receipts["COMPATIBLE_CHANGE"]
        self.assertNotEqual(r["sha_during_probe"], r["sha_before_probe"])
        self.assertIn("We have credited", r["probe_diff"])

    def test_without_memory_even_a_harmless_change_cannot_merge(self):
        r = self.receipts["COMPATIBLE_CHANGE"]
        self.assertEqual(r["counterfactual_without_memory"]["verdict"], "DECISION_REQUIRED")
        self.assertTrue(r["memory_changed_verdict"])


class TestEveryProbe(GuardSuiteCase):

    def test_restores_exact_bytes_and_ready_state(self):
        for pid, r in self.receipts.items():
            with self.subTest(probe=pid):
                self.assertTrue(r["restored_exact_bytes"])
                self.assertTrue(r["restoration_verified"])
                self.assertEqual(r["gate_after_restore"], "SEMANTICALLY_READY")
                path = self.ws / PROBES[pid]["affected_file"]
                self.assertEqual(path.read_bytes(), self.bytes_before[pid])
        self.assertEqual(gate_mod.evaluate_gate(self.ws)["verdict"], "SEMANTICALLY_READY")

    def test_receipts_on_disk_match(self):
        for pid, r in self.receipts.items():
            with self.subTest(probe=pid):
                on_disk = json.loads((self.out / PROBES[pid]["receipt_name"]).read_text())
                self.assertEqual(on_disk["guard_verdict"], r["guard_verdict"])
                self.assertEqual(on_disk["sha_during_probe"], r["sha_during_probe"])

    def test_verdicts_are_derived_from_the_gate(self):
        for pid, r in self.receipts.items():
            with self.subTest(probe=pid):
                self.assertEqual(r["guard_verdict"], GUARD_VERDICTS[r["gate_during_probe"]])

    def test_never_the_replay(self):
        for r in self.receipts.values():
            self.assertFalse(r["is_fresh_agent_replay"])
            self.assertEqual(r["truth_boundary"]["fresh_agent_replay"],
                             "NOT_EXECUTED / PENDING_LIVE_BOB")

    def test_counterfactual_never_writes_the_workspace(self):
        memory = self.ws / gate_mod.MEMORY_RELPATH
        self.assertTrue(memory.is_file())
        self.assertRegex((self.ws / gate_mod.BRIEF_RELPATH).read_text(), r"collider:canon")

    def test_each_probe_runs_once(self):
        for pid in PROBES:
            with self.subTest(probe=pid), self.assertRaises(FileExistsError):
                run_guard_probe(self.ws, self.out, probe_id=pid)

    def test_unknown_probe_refused(self):
        with self.assertRaises(ValueError):
            run_guard_probe(self.ws, self.tmp / "x", probe_id="rm -rf /")

    def test_source_tree_untouched(self):
        self.assertEqual(self.source_before, self.source_after)
        for r in self.receipts.values():
            self.assertTrue(r["source_tree_untouched"])


if __name__ == "__main__":
    unittest.main()
