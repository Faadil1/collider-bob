"""
COLLIDER fixture tests — claims A–F

Runs the LOCAL pipeline against the committed PRESEEDED fixture and verifies
every claim against fixtures/failed-payment/EXPECTED-TRUTH.md logic.

Usage:
    python3 -m pytest tests/test_fixture.py -v
    # or directly:
    python3 tests/test_fixture.py

All tests must pass before the LOCAL-001 run is considered verified.
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collider.pipeline import (
    reconcile,
    classify_concept,
    route_impact,
    scope_filter,
    normalize,
    run_pipeline,
    verify_fixture,
    load_json,
    CROSS_BOUNDARY_CONCEPTS,
)

FIXTURE_DIR = "fixtures/failed-payment"
BRIEF_PATH = "fixtures/failed-payment/BRIEF.md"
RUN_ID = "test-run"
RUN_DIR = "evidence/runs/test-run"


def load_interpretations():
    return [
        load_json(f"{FIXTURE_DIR}/interpretations/api.json"),
        load_json(f"{FIXTURE_DIR}/interpretations/ledger.json"),
        load_json(f"{FIXTURE_DIR}/interpretations/notifications.json"),
    ]


def brief_text():
    return Path(BRIEF_PATH).read_text()


class TestScopeFilter(unittest.TestCase):
    """Step 0 — scope filter"""

    def test_customer_identity_in_scope(self):
        self.assertTrue(scope_filter("customer_identity"))

    def test_field_name_in_scope(self):
        self.assertTrue(scope_filter("field_name"))

    def test_money_representation_in_scope(self):
        self.assertTrue(scope_filter("money_representation"))

    def test_internal_response_body_out_of_scope(self):
        self.assertFalse(scope_filter("internal_response_body"))
        self.assertFalse(scope_filter("response_body_status"))
        self.assertFalse(scope_filter("response_body_ok"))

    def test_arbitrary_field_out_of_scope(self):
        self.assertFalse(scope_filter("some_internal_field"))


class TestNormalize(unittest.TestCase):
    """Step 1 — normalization (pure string canonicalization)"""

    def test_lowercase(self):
        self.assertEqual(normalize("Account_ID"), "account_id")

    def test_strip_whitespace(self):
        self.assertEqual(normalize("  email  "), "email")

    def test_same_values_equal(self):
        self.assertEqual(normalize("integer_cents"), normalize("integer_cents"))

    def test_different_values_not_equal(self):
        self.assertNotEqual(normalize("refund_amount"), normalize("credit_amount"))


class TestReconciler(unittest.TestCase):
    """Concept grouping across workstreams"""

    def test_groups_customer_identity_for_api_and_ledger_only(self):
        interps = load_interpretations()
        groups = reconcile(interps)
        self.assertIn("customer_identity", groups)
        workstreams = set(groups["customer_identity"].keys())
        # Notifications must NOT be in customer_identity
        self.assertNotIn("notifications", workstreams)
        self.assertIn("api", workstreams)
        self.assertIn("ledger", workstreams)

    def test_groups_field_name_for_all_three(self):
        interps = load_interpretations()
        groups = reconcile(interps)
        self.assertIn("field_name", groups)
        workstreams = set(groups["field_name"].keys())
        self.assertIn("api", workstreams)
        self.assertIn("ledger", workstreams)
        self.assertIn("notifications", workstreams)

    def test_notifications_holds_notification_contact_not_customer_identity(self):
        interps = load_interpretations()
        notif = next(i for i in interps if i["workstream"] == "notifications")
        concepts = {c["concept"] for c in notif["claims"]}
        self.assertIn("notification_contact", concepts)
        self.assertNotIn("customer_identity", concepts)

    def test_groups_money_representation_for_all_three(self):
        interps = load_interpretations()
        groups = reconcile(interps)
        self.assertIn("money_representation", groups)
        self.assertEqual(len(groups["money_representation"]), 3)


class TestClaimA(unittest.TestCase):
    """Claim A — TRUE SPEC_GAP: customer_identity"""

    def setUp(self):
        interps = load_interpretations()
        self.groups = reconcile(interps)
        self.brief = brief_text()

    def test_classification_is_spec_gap(self):
        c = classify_concept("customer_identity", self.groups["customer_identity"], self.brief)
        self.assertEqual(c["classification"], "SPEC_GAP")

    def test_epistemic_state_is_unknown(self):
        c = classify_concept("customer_identity", self.groups["customer_identity"], self.brief)
        self.assertEqual(c["epistemic_state"], "UNKNOWN")

    def test_auto_resolve_is_false(self):
        c = classify_concept("customer_identity", self.groups["customer_identity"], self.brief)
        self.assertFalse(c["auto_resolve"])

    def test_scope_is_api_and_ledger(self):
        c = classify_concept("customer_identity", self.groups["customer_identity"], self.brief)
        self.assertIn("api", c["scope"])
        self.assertIn("ledger", c["scope"])

    def test_no_agent_drift_workstreams(self):
        c = classify_concept("customer_identity", self.groups["customer_identity"], self.brief)
        self.assertEqual(c["agent_drift_workstreams"], [])

    def test_minimal_question_present(self):
        c = classify_concept("customer_identity", self.groups["customer_identity"], self.brief)
        self.assertIn("minimal_question", c)
        self.assertTrue(len(c["minimal_question"]) > 10)

    def test_classifier_judgment_not_used(self):
        c = classify_concept("customer_identity", self.groups["customer_identity"], self.brief)
        self.assertFalse(c["classifier_judgment_used"])


class TestClaimB(unittest.TestCase):
    """Claim B — AGENT_DRIFT: refund_amount vs credit_amount"""

    def setUp(self):
        interps = load_interpretations()
        self.groups = reconcile(interps)
        self.brief = brief_text()

    def test_classification_is_agent_drift(self):
        c = classify_concept("field_name", self.groups["field_name"], self.brief)
        self.assertEqual(c["classification"], "AGENT_DRIFT")

    def test_ledger_is_drifted(self):
        c = classify_concept("field_name", self.groups["field_name"], self.brief)
        self.assertIn("ledger", c["agent_drift_workstreams"])

    def test_authoritative_value_is_refund_amount(self):
        c = classify_concept("field_name", self.groups["field_name"], self.brief)
        self.assertEqual(c["authoritative_value"], "refund_amount")

    def test_source_evidence_is_cited(self):
        c = classify_concept("field_name", self.groups["field_name"], self.brief)
        self.assertIsNotNone(c["source_evidence"])
        self.assertIsNotNone(c["source_evidence"]["excerpt"])

    def test_no_human_question_needed(self):
        c = classify_concept("field_name", self.groups["field_name"], self.brief)
        self.assertFalse(c["human_question_needed"])

    def test_not_classified_as_spec_gap(self):
        c = classify_concept("field_name", self.groups["field_name"], self.brief)
        self.assertNotEqual(c["classification"], "SPEC_GAP")


class TestClaimC(unittest.TestCase):
    """Claim C — SHARED INFERENCE: money_representation"""

    def setUp(self):
        interps = load_interpretations()
        self.groups = reconcile(interps)
        self.brief = brief_text()

    def test_classification_is_no_disagreement(self):
        c = classify_concept("money_representation", self.groups["money_representation"], self.brief)
        self.assertEqual(c["classification"], "NO_DISAGREEMENT")

    def test_subtype_is_shared_inferred(self):
        c = classify_concept("money_representation", self.groups["money_representation"], self.brief)
        self.assertEqual(c["classification_subtype"], "SHARED_INFERRED")

    def test_upgrades_to_fact_is_false(self):
        c = classify_concept("money_representation", self.groups["money_representation"], self.brief)
        self.assertFalse(c["upgrades_to_fact"])

    def test_consensus_is_true(self):
        c = classify_concept("money_representation", self.groups["money_representation"], self.brief)
        self.assertTrue(c["consensus"])


class TestClaimD(unittest.TestCase):
    """Claim D — UNAFFECTED WORKSTREAM: Notifications structural independence"""

    def test_notifications_not_in_customer_identity_dependency(self):
        interps = load_interpretations()
        # Route impact for customer_identity → account_id
        impact = route_impact("customer_identity", "account_id", interps)
        ws_impacts = {w["workstream"]: w for w in impact["workstream_impacts"]}

        # Notifications must be not_applicable (no claim)
        self.assertIn("notifications", ws_impacts)
        self.assertEqual(ws_impacts["notifications"]["action"], "not_applicable")
        self.assertFalse(ws_impacts["notifications"]["consumed_concept"])

    def test_api_requires_repair(self):
        interps = load_interpretations()
        impact = route_impact("customer_identity", "account_id", interps)
        ws_impacts = {w["workstream"]: w for w in impact["workstream_impacts"]}
        self.assertEqual(ws_impacts["api"]["action"], "repair")

    def test_ledger_preserved(self):
        interps = load_interpretations()
        impact = route_impact("customer_identity", "account_id", interps)
        ws_impacts = {w["workstream"]: w for w in impact["workstream_impacts"]}
        self.assertEqual(ws_impacts["ledger"]["action"], "preserve")


class TestClaimE(unittest.TestCase):
    """Claim E — UNKNOWN PATH: correct abstention"""

    def test_spec_gap_without_human_decision_does_not_auto_resolve(self):
        interps = load_interpretations()
        groups = reconcile(interps)
        brief = brief_text()
        c = classify_concept("customer_identity", groups["customer_identity"], brief)
        # Classification must be SPEC_GAP with auto_resolve=False
        self.assertEqual(c["classification"], "SPEC_GAP")
        self.assertFalse(c["auto_resolve"])
        self.assertEqual(c["epistemic_state"], "UNKNOWN")

    def test_no_canon_patch_emitted_without_human_decision(self):
        """Pipeline with no human_decisions must not write a canon patch for customer_identity"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_pipeline(
                fixture_dir=FIXTURE_DIR,
                brief_path=BRIEF_PATH,
                run_id="test-claim-e",
                run_dir=tmpdir,
                generation_mode="LOCAL",
                test_command="test",
                human_decisions={},  # NO decision supplied
                apply_repair=False,
            )
        # Impact set for customer_identity should have no canonical_value
        impact_entry = next(
            (e for e in result["impact_set"] if e.get("concept") == "customer_identity"),
            None,
        )
        self.assertIsNotNone(impact_entry)
        self.assertIsNone(impact_entry.get("canonical_value"))
        self.assertEqual(impact_entry.get("status"), "PENDING_HUMAN_DECISION")


class TestClaimF(unittest.TestCase):
    """Claim F — NEGATIVE CONTROL: internal response body out of scope"""

    def test_scope_filter_rejects_internal_body_field(self):
        self.assertFalse(scope_filter("internal_response_body"))

    def test_scope_filter_result_is_out_of_scope_at_step_0(self):
        result = classify_concept(
            "internal_response_body",
            {
                "api": {"value": {"status": "credited"}, "epistemic_state": "OBSERVED",
                        "evidence_refs": [], "evidence_relation": "EXPLICIT",
                        "consumed_by": [], "artifact_refs": []},
                "notifications": {"value": {"ok": True}, "epistemic_state": "OBSERVED",
                                  "evidence_refs": [], "evidence_relation": "EXPLICIT",
                                  "consumed_by": [], "artifact_refs": []},
            },
            brief_text(),
        )
        self.assertEqual(result["classification"], "OUT_OF_SCOPE")
        self.assertEqual(result["classifier_step_reached"], 0)
        self.assertFalse(result.get("spec_gap_raised", False))

    def test_no_spec_gap_raised_for_body_field(self):
        result = classify_concept(
            "internal_response_body",
            {
                "api": {"value": {"status": "credited"}, "epistemic_state": "OBSERVED",
                        "evidence_refs": [], "evidence_relation": "EXPLICIT",
                        "consumed_by": [], "artifact_refs": []},
                "notifications": {"value": {"ok": True}, "epistemic_state": "OBSERVED",
                                  "evidence_refs": [], "evidence_relation": "EXPLICIT",
                                  "consumed_by": [], "artifact_refs": []},
            },
            brief_text(),
        )
        self.assertNotEqual(result["classification"], "SPEC_GAP")
        self.assertNotEqual(result["classification"], "AGENT_DRIFT")


class TestFullPipeline(unittest.TestCase):
    """End-to-end: run the LOCAL pipeline and verify all A–F"""

    @classmethod
    def setUpClass(cls):
        """Run the pipeline once for all tests in this class.
        Saves the pre-repair state of api/handlers/recover.py and restores it
        in tearDownClass so later tests in the same session are not affected.
        """
        import api.handlers.recover as _rec
        cls._recover_path = Path("api/handlers/recover.py")
        cls._recover_original = cls._recover_path.read_text()

        cls.result = run_pipeline(
            fixture_dir=FIXTURE_DIR,
            brief_path=BRIEF_PATH,
            run_id=RUN_ID,
            run_dir=RUN_DIR,
            generation_mode="LOCAL",
            test_command="python3 -m pytest api/tests/ ledger/tests/ notifications/tests/ -v",
            human_decisions={"customer_identity": "account_id"},
            execution_environment="LOCAL",
            interpretation_source="PRESEEDED",
            human_decision_source="PRESEEDED",
            apply_repair=True,
        )
        cls.verification = verify_fixture(cls.result)

    @classmethod
    def tearDownClass(cls):
        """Restore api/handlers/recover.py to its pre-repair state."""
        import importlib, api.handlers.recover as _rec
        cls._recover_path.write_text(cls._recover_original)
        importlib.reload(_rec)

    def test_all_claims_pass(self):
        for claim_id, verdict in self.verification["verdicts"].items():
            with self.subTest(claim=claim_id):
                self.assertTrue(
                    verdict["pass"],
                    msg=f"Claim {claim_id} failed: {verdict['detail']}"
                )

    def test_no_pipeline_failures(self):
        self.assertEqual(
            len(self.result["failures"]), 0,
            msg=f"Pipeline failures: {self.result['failures']}"
        )

    def test_manifest_generation_mode_is_local(self):
        manifest = load_json(os.path.join(RUN_DIR, "manifest.json"))
        self.assertEqual(manifest["generation_mode"], "LOCAL")
        self.assertIsNone(manifest["bob_session_ref"])

    def test_manifest_not_live_bob(self):
        manifest = load_json(os.path.join(RUN_DIR, "manifest.json"))
        self.assertNotEqual(manifest["generation_mode"], "LIVE_BOB")

    def test_manifest_has_provenance_fields(self):
        """Manifest must carry separate execution_environment, interpretation_source, human_decision_source."""
        manifest = load_json(os.path.join(RUN_DIR, "manifest.json"))
        self.assertEqual(manifest["execution_environment"], "LOCAL")
        self.assertEqual(manifest["interpretation_source"], "PRESEEDED")
        self.assertEqual(manifest["human_decision_source"], "PRESEEDED")

    def test_classifications_json_written(self):
        self.assertTrue(os.path.exists(os.path.join(RUN_DIR, "classifications.json")))

    def test_canon_patch_written_for_customer_identity(self):
        patch_path = os.path.join(RUN_DIR, "canon-patches", "customer_identity.json")
        self.assertTrue(os.path.exists(patch_path))
        patch = load_json(patch_path)
        self.assertEqual(patch["canonical_value"], "account_id")
        self.assertEqual(patch["decision_source"], "human")
        self.assertEqual(patch["evidence_state"], "OBSERVED")

    def test_canon_patch_has_prior_epistemic_state(self):
        """Canon patch must carry prior_epistemic_state=UNKNOWN (requirement 8)."""
        patch = load_json(os.path.join(RUN_DIR, "canon-patches", "customer_identity.json"))
        self.assertEqual(patch["prior_epistemic_state"], "UNKNOWN")

    def test_canon_patch_has_prior_classification_spec_gap(self):
        """Canon patch must carry prior_classification=SPEC_GAP (requirement 8)."""
        patch = load_json(os.path.join(RUN_DIR, "canon-patches", "customer_identity.json"))
        self.assertEqual(patch["prior_classification"], "SPEC_GAP")

    def test_canon_patch_decision_state_is_canonical(self):
        """Canon patch must carry decision_state=CANONICAL (requirement 8)."""
        patch = load_json(os.path.join(RUN_DIR, "canon-patches", "customer_identity.json"))
        self.assertEqual(patch["decision_state"], "CANONICAL")

    def test_canon_patch_decision_source_is_human_clarification(self):
        """Canon patch must carry decision_source_detail=HUMAN_CLARIFICATION (requirement 8)."""
        patch = load_json(os.path.join(RUN_DIR, "canon-patches", "customer_identity.json"))
        self.assertEqual(patch["decision_source_detail"], "HUMAN_CLARIFICATION")

    def test_api_implementation_repaired(self):
        """
        Targeted repair must actually change api/handlers/recover.py.
        After repair, CUSTOMER_IDENTITY_FIELD must be 'account_id'.
        """
        from api.handlers import recover
        import importlib
        importlib.reload(recover)
        self.assertEqual(recover.CUSTOMER_IDENTITY_FIELD, "account_id",
                         "API CUSTOMER_IDENTITY_FIELD must be 'account_id' after repair")

    def test_repairs_json_records_api_changed(self):
        """repairs.json must record that api/handlers/recover.py was modified."""
        repairs_path = os.path.join(RUN_DIR, "repairs.json")
        self.assertTrue(os.path.exists(repairs_path))
        repairs = load_json(repairs_path)
        api_repair = next((r for r in repairs if r["workstream"] == "api"), None)
        self.assertIsNotNone(api_repair)
        self.assertEqual(api_repair["action"], "repaired")
        self.assertIsNotNone(api_repair["file_modified"])

    def test_repairs_json_records_ledger_unchanged(self):
        """repairs.json must record that ledger was preserved (not repaired)."""
        repairs = load_json(os.path.join(RUN_DIR, "repairs.json"))
        ledger_repair = next((r for r in repairs if r["workstream"] == "ledger"), None)
        self.assertIsNotNone(ledger_repair)
        self.assertEqual(ledger_repair["action"], "preserve")
        self.assertIsNone(ledger_repair.get("file_modified"))

    def test_repairs_json_records_notifications_not_applicable(self):
        """repairs.json must record that notifications was not_applicable (no dependency)."""
        repairs = load_json(os.path.join(RUN_DIR, "repairs.json"))
        notif_repair = next((r for r in repairs if r["workstream"] == "notifications"), None)
        self.assertIsNotNone(notif_repair)
        self.assertEqual(notif_repair["action"], "not_applicable")

    def test_tests_before_contain_workstream_results(self):
        """tests-before.txt must be real pytest behavioral test output."""
        txt = Path(os.path.join(RUN_DIR, "tests-before.txt")).read_text()
        # pytest output contains "passed"
        self.assertIn("passed", txt)
        # Must not claim it's schema validation
        self.assertNotIn("schema validation", txt)

    def test_tests_after_contain_workstream_results(self):
        """tests-after.txt must be real pytest behavioral test output."""
        txt = Path(os.path.join(RUN_DIR, "tests-after.txt")).read_text()
        self.assertIn("passed", txt)

    def test_tests_before_all_pass(self):
        self.assertTrue(self.result["tests_before_passed"],
                        "Behavioral tests must pass before repair")

    def test_tests_after_all_pass(self):
        self.assertTrue(self.result["tests_after_passed"],
                        "Behavioral tests must pass after repair")

    def test_failures_json_is_empty(self):
        failures = load_json(os.path.join(RUN_DIR, "failures.json"))
        self.assertEqual(failures["failures"], [])

    def test_metrics_written(self):
        metrics = load_json(os.path.join(RUN_DIR, "metrics.json"))
        metric_names = {m["metric"] for m in metrics["metrics"]}
        self.assertIn("spec_gaps_detected", metric_names)
        self.assertIn("agent_drifts_detected", metric_names)
        self.assertIn("canon_patches_written", metric_names)
        self.assertIn("tests_before_passed", metric_names)
        self.assertIn("tests_after_passed", metric_names)

    def test_classifier_judgment_never_used(self):
        metrics = load_json(os.path.join(RUN_DIR, "metrics.json"))
        m = next(m for m in metrics["metrics"] if m["metric"] == "classifier_judgment_used_count")
        self.assertEqual(m["value"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
