"""
Tests for the Notifications workstream — send_credit_notice().

These are behavioral workstream tests for Notifications.
They test Notifications in ISOLATION.
Notifications has no customer_identity claim — it only receives notification_contact.
These tests pass both before and after the customer_identity SPEC_GAP is resolved.
That is expected: Notifications is structurally unaffected by the canon patch.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from notifications.send_credit_notice import (
    send_credit_notice,
    format_amount,
    NOTIFICATION_CONTACT_TYPE,
)


class TestFormatAmount(unittest.TestCase):

    def test_format_1000_cents_as_10_dollars(self):
        self.assertEqual(format_amount(1000), "$10.00")

    def test_format_0_cents(self):
        self.assertEqual(format_amount(0), "$0.00")

    def test_format_2550_cents(self):
        self.assertEqual(format_amount(2550), "$25.50")


class TestSendCreditNotice(unittest.TestCase):

    def test_successful_send_returns_ok(self):
        result = send_credit_notice(
            notification_contact="user@example.com",
            refund_amount=1000,
            charge_id="ch_001",
        )
        self.assertEqual(result["status"], "ok")

    def test_notification_contact_preserved(self):
        result = send_credit_notice(
            notification_contact="user@example.com",
            refund_amount=500,
            charge_id="ch_002",
        )
        self.assertEqual(result["notification_contact"], "user@example.com")

    def test_contact_type_is_notification_contact_type(self):
        """Notifications uses NOTIFICATION_CONTACT_TYPE for its delivery address."""
        result = send_credit_notice(
            notification_contact="user@example.com",
            refund_amount=100,
            charge_id="ch_003",
        )
        self.assertEqual(result["contact_type"], NOTIFICATION_CONTACT_TYPE)

    def test_refund_amount_preserved(self):
        result = send_credit_notice(
            notification_contact="user@example.com",
            refund_amount=2500,
            charge_id="ch_004",
        )
        self.assertEqual(result["refund_amount"], 2500)

    def test_message_preview_contains_charge_id(self):
        result = send_credit_notice(
            notification_contact="user@example.com",
            refund_amount=750,
            charge_id="ch_special_99",
        )
        self.assertIn("ch_special_99", result["message_preview"])

    def test_message_preview_contains_display_amount(self):
        result = send_credit_notice(
            notification_contact="user@example.com",
            refund_amount=1000,
            charge_id="ch_005",
        )
        self.assertIn("$10.00", result["message_preview"])

    def test_empty_notification_contact_raises(self):
        with self.assertRaises(ValueError):
            send_credit_notice(
                notification_contact="",
                refund_amount=100,
                charge_id="ch_006",
            )

    def test_negative_refund_amount_raises(self):
        with self.assertRaises(ValueError):
            send_credit_notice(
                notification_contact="user@example.com",
                refund_amount=-100,
                charge_id="ch_007",
            )

    def test_empty_charge_id_raises(self):
        with self.assertRaises(ValueError):
            send_credit_notice(
                notification_contact="user@example.com",
                refund_amount=100,
                charge_id="",
            )

    def test_zero_refund_amount_is_valid(self):
        result = send_credit_notice(
            notification_contact="user@example.com",
            refund_amount=0,
            charge_id="ch_008",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main(verbosity=2)
