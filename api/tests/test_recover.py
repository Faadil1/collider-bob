"""
Tests for the API workstream handler — process_recovery().

These are the behavioral workstream tests.
They test the API workstream in ISOLATION (each is internally self-consistent).
They do NOT test cross-boundary identity agreement with Ledger.

The "everything looks green locally" property is intentional: each workstream
passes its own tests while using a different customer_identity value.
That is the core demonstration of why COLLIDER is needed.

NOTE ON BEFORE/AFTER REPAIR:
  Before repair, CUSTOMER_IDENTITY_FIELD = "email"
  After repair,  CUSTOMER_IDENTITY_FIELD = "account_id"

  These tests always supply BOTH customer_email and customer_account_id so they
  pass in both states. The behavioral contract (returns status="credited",
  preserves refund_amount, validates inputs) is unchanged by the repair.
  Only the identity field used changes — which is the point of the demo.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.handlers.recover import process_recovery, CUSTOMER_IDENTITY_FIELD


class TestProcessRecovery(unittest.TestCase):

    # Always supply both identity values so tests work before and after repair.
    BOTH = {
        "customer_email": "user@example.com",
        "customer_account_id": "acct_42",
    }

    def test_successful_recovery_returns_credited_status(self):
        result = process_recovery(
            charge_id="ch_001",
            refund_amount=1000,
            notification_contact="user@example.com",
            **self.BOTH,
        )
        self.assertEqual(result["status"], "credited")

    def test_refund_amount_preserved_in_response(self):
        result = process_recovery(
            charge_id="ch_001",
            refund_amount=2500,
            notification_contact="user@example.com",
            **self.BOTH,
        )
        self.assertEqual(result["refund_amount"], 2500)

    def test_field_name_is_refund_amount(self):
        """The API stub explicitly names the field 'refund_amount'."""
        result = process_recovery(
            charge_id="ch_002",
            refund_amount=500,
            notification_contact="user@example.com",
            **self.BOTH,
        )
        self.assertIn("refund_amount", result)

    def test_customer_identity_field_used_in_response(self):
        """
        The response includes which identity field was used.
        Before repair: CUSTOMER_IDENTITY_FIELD = 'email'.
        After repair: CUSTOMER_IDENTITY_FIELD = 'account_id'.
        The field name changes; the behavior (a value is resolved) does not.
        """
        result = process_recovery(
            charge_id="ch_003",
            refund_amount=100,
            notification_contact="user@example.com",
            **self.BOTH,
        )
        self.assertEqual(result["customer_field"], CUSTOMER_IDENTITY_FIELD)

    def test_customer_identity_resolves_to_correct_value(self):
        """
        The resolved customer_value must match the field chosen by CUSTOMER_IDENTITY_FIELD.
        Before repair: resolves to email.
        After repair: resolves to account_id.
        Either is internally consistent.
        """
        result = process_recovery(
            charge_id="ch_006",
            refund_amount=750,
            notification_contact="user@example.com",
            customer_email="user@example.com",
            customer_account_id="acct_123",
        )
        if CUSTOMER_IDENTITY_FIELD == "email":
            self.assertEqual(result["customer_value"], "user@example.com")
        else:
            self.assertEqual(result["customer_value"], "acct_123")

    def test_negative_refund_amount_raises(self):
        with self.assertRaises(ValueError):
            process_recovery(
                charge_id="ch_004",
                refund_amount=-1,
                notification_contact="user@example.com",
                **self.BOTH,
            )

    def test_missing_charge_id_raises(self):
        with self.assertRaises(ValueError):
            process_recovery(
                charge_id="",
                refund_amount=100,
                notification_contact="user@example.com",
                **self.BOTH,
            )

    def test_missing_notification_contact_raises(self):
        with self.assertRaises(ValueError):
            process_recovery(
                charge_id="ch_005",
                refund_amount=100,
                notification_contact="",
                **self.BOTH,
            )

    def test_zero_refund_amount_is_valid(self):
        result = process_recovery(
            charge_id="ch_007",
            refund_amount=0,
            notification_contact="user@example.com",
            **self.BOTH,
        )
        self.assertEqual(result["status"], "credited")


if __name__ == "__main__":
    unittest.main(verbosity=2)
