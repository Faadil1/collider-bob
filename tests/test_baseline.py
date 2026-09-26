import inspect
import unittest

import baseline.run_baseline as baseline


class TestBaselineIntegrity(unittest.TestCase):

    def test_probe_observes_two_integration_conflicts(self):
        result = baseline.probe_integration()
        self.assertEqual(result["status"], "INTEGRATION_BLOCKED")
        self.assertEqual(result["conflict_count"], 2)

    def test_identity_conflict_is_api_ledger_only(self):
        result = baseline.probe_integration()
        conflict = next(
            c for c in result["conflicts"]
            if c["conflict_id"] == "customer-identity-interface-mismatch"
        )
        self.assertEqual(conflict["involved_workstreams"], ["api", "ledger"])

    def test_baseline_does_not_classify_root_cause(self):
        result = baseline.probe_integration()
        for conflict in result["conflicts"]:
            self.assertIsNone(conflict["classification"])

    def test_runner_has_no_collider_or_expected_truth_dependency(self):
        source = inspect.getsource(baseline)
        self.assertNotIn("import collider", source)
        self.assertNotIn("from collider", source)
        self.assertNotIn("EXPECTED-TRUTH.md", source)


if __name__ == "__main__":
    unittest.main()
