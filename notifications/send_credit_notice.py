"""
Notifications Workstream — Credit Notice Sender

Delivers a notification to the customer's contact address after a credit is posted.

CUSTOMER IDENTITY:
  This workstream does NOT hold a customer_identity claim.
  It receives 'notification_contact' as a pre-resolved input — a delivery address.
  It does not need to know how the upstream resolved customer identity.

NOTIFICATION CONTACT:
  The delivery address type is assumed to be email_address.
  Epistemic state: INFERRED — the stub says 'notification_contact: string';
  the channel type (email/phone/push) is not specified.

MONEY REPRESENTATION:
  Amounts are divided by 100 for display (integer cents → display dollars).
  Epistemic state: INFERRED.

STRUCTURAL INDEPENDENCE:
  Notifications does not participate in the customer_identity SPEC_GAP.
  It holds a separate concept (notification_contact) in its own scope.
  Impact router will find no dependency on customer_identity.
"""

NOTIFICATION_CONTACT_TYPE = "email_address"  # INFERRED — stub says string, type unspecified
MONEY_UNIT = "integer_cents"  # INFERRED — format_amount divides by 100; the stub never says cents


def format_amount(refund_amount_cents: int) -> str:
    """Format integer cents as a display string."""
    return f"${refund_amount_cents / 100:.2f}"


def send_credit_notice(
    notification_contact: str,
    refund_amount: int,
    charge_id: str,
) -> dict:
    """
    Send a credit notification to the customer's contact address.

    Parameters:
        notification_contact: Delivery address (assumed email_address; INFERRED).
        refund_amount: Credit amount in integer cents (INFERRED unit).
        charge_id: The charge that was recovered.

    Returns:
        {"status": "ok", "notification_contact": notification_contact,
         "contact_type": NOTIFICATION_CONTACT_TYPE,
         "message_preview": <formatted message>}

    Raises:
        ValueError if notification_contact is empty, refund_amount is negative,
        or charge_id is empty.
    """
    if not notification_contact:
        raise ValueError("notification_contact is required")
    if refund_amount < 0:
        raise ValueError("refund_amount must be non-negative")
    if not charge_id:
        raise ValueError("charge_id is required")

    display_amount = format_amount(refund_amount)
    message = (
        f"Your charge {charge_id} has been recovered. "
        f"A credit of {display_amount} has been applied to your account."
    )
    return {
        "status": "ok",
        "notification_contact": notification_contact,
        "contact_type": NOTIFICATION_CONTACT_TYPE,
        "refund_amount": refund_amount,
        "message_preview": message,
    }
