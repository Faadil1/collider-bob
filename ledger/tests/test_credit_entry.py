"""
Tests for the Ledger workstream — post_credit_entry().

These are behavioral workstream tests for the Ledger.
They test the Ledger in ISOLATION (internally self-consistent).
They do NOT test whether 'account_id' agrees with the API workstream's choice.

The "everything looks green locally" property is intentional.
COLLIDER is needed to detect the cross-boundary identity conflict.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ledger.credit_entry import post_credit_entry, CUSTOMER_IDENTITY_FIELD, CREDIT_FIELD_NAME


class TestPostCreditEntry(unittest.TestCase):

    def test_successful_credit_returns_posted_status(self):
        result = post_credit_entry(account_id="acct_42", credit_amount=1000)
        self.assertEqual(result["status"], "posted")

    def test_entry_type_is_credit(self):
        result = post_credit_entry(account_id="acct_42", credit_amount=500)
        self.assertEqual(result["entry_type"], "credit")

    def test_customer_identity_field_is_account_id(self):
        """Ledger uses account_id — its independent local choice."""
        self.assertEqual(CUSTOMER_IDENTITY_FIELD, "account_id")
        result = post_credit_entry(account_id="acct_42", credit_amount=100)
        self.assertEqual(result["customer_field"], "account_id")
        self.assertEqual(result["customer_value"], "acct_42")

    def test_credit_field_name_in_response(self):
        """
        The credit field is named CREDIT_FIELD_NAME.
        Before repair: 'credit_amount' (AGENT DRIFT vs stub's 'refund_amount').
        After AGENT_DRIFT repair: 'refund_amount'.
        """
        result = post_credit_entry(account_id="acct_42", credit_amount=750)
        self.assertIn(CREDIT_FIELD_NAME, result)

    def test_credit_amount_preserved_in_response(self):
        result = post_credit_entry(account_id="acct_99", credit_amount=2500)
        self.assertEqual(result[CREDIT_FIELD_NAME], 2500)

    def test_negative_credit_amount_raises(self):
        with self.assertRaises(ValueError):
            post_credit_entry(account_id="acct_42", credit_amount=-1)

    def test_empty_account_id_raises(self):
        with self.assertRaises(ValueError):
            post_credit_entry(account_id="", credit_amount=100)

    def test_zero_credit_amount_is_valid(self):
        result = post_credit_entry(account_id="acct_42", credit_amount=0)
        self.assertEqual(result["status"], "posted")


if __name__ == "__main__":
    unittest.main(verbosity=2)
