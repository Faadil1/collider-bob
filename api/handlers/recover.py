"""
API Workstream — Failed Payment Recovery Handler

POST /charges/{charge_id}/recover

This handler accepts a failed-charge recovery request and triggers a credit.

CUSTOMER IDENTITY DECISION:
  This workstream uses 'email' to look up the customer for credit purposes.
  Epistemic state: UNKNOWN — no source evidence specifies which identity field to use.
  This is an independent local choice; the specification does not decide it.

FIELD NAME:
  The money field is 'refund_amount' as explicitly stated in the API contract stub
  (BRIEF.md §Source Document).

MONEY REPRESENTATION:
  Amounts are treated as integer cents (e.g. 1000 = $10.00).
  Epistemic state: INFERRED — the stub says integer type; unit is not specified.
"""

CUSTOMER_IDENTITY_FIELD = "email"  # LOCAL CHOICE — not specified by brief
MONEY_UNIT = "integer_cents"  # INFERRED — stub says integer; the unit is unspecified


def process_recovery(charge_id: str, refund_amount: int, notification_contact: str,
                     customer_email: str | None = None,
                     customer_account_id: str | None = None) -> dict:
    """
    Process a failed-charge recovery request.

    Returns:
        {"status": "credited", "customer_field": CUSTOMER_IDENTITY_FIELD,
         "customer_value": <resolved identity>, "refund_amount": refund_amount}

    Raises:
        ValueError if refund_amount is negative or required fields are missing.
    """
    if not charge_id:
        raise ValueError("charge_id is required")
    if refund_amount < 0:
        raise ValueError("refund_amount must be non-negative")
    if not notification_contact:
        raise ValueError("notification_contact is required")

    # Resolve the customer identity using the local field choice (email).
    if CUSTOMER_IDENTITY_FIELD == "email":
        customer_value = customer_email
    else:
        customer_value = customer_account_id

    if customer_value is None:
        raise ValueError(
            f"Customer identity field '{CUSTOMER_IDENTITY_FIELD}' not provided"
        )

    return {
        "status": "credited",
        "customer_field": CUSTOMER_IDENTITY_FIELD,
        "customer_value": customer_value,
        "refund_amount": refund_amount,
        "notification_contact": notification_contact,
    }
