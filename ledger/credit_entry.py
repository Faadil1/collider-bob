"""
Ledger Workstream — Credit Entry Recorder

Records a double-entry credit against a customer account after a failed charge.

CUSTOMER IDENTITY DECISION:
  This workstream uses 'account_id' to key credit entries.
  Epistemic state: UNKNOWN — no source evidence specifies which identity field to use.
  This is an independent local choice; the specification does not decide it.

FIELD NAME:
  The money field is called 'credit_amount' in this workstream.
  Epistemic state: INFERRED — the brief says "credit the customer"; domain terminology.
  NOTE: The API contract stub says 'refund_amount'. This workstream has drifted.
  This drift will be classified as AGENT_DRIFT by COLLIDER.

MONEY REPRESENTATION:
  Amounts are stored as integer cents.
  Epistemic state: INFERRED — consistent with stub's integer type, not proven.
"""

CUSTOMER_IDENTITY_FIELD = "account_id"  # LOCAL CHOICE — not specified by brief
CREDIT_FIELD_NAME = "credit_amount"     # AGENT DRIFT vs source stub's 'refund_amount'
MONEY_UNIT = "decimal_dollars"          # INFERRED — stub says integer; the unit is unspecified


def post_credit_entry(account_id: str, credit_amount: int) -> dict:
    """
    Post a credit entry to the ledger.

    Parameters:
        account_id: The customer's account identifier (using CUSTOMER_IDENTITY_FIELD='account_id').
        credit_amount: The credit amount in integer cents (INFERRED unit).

    Returns:
        {"entry_type": "credit", "customer_field": CUSTOMER_IDENTITY_FIELD,
         "customer_value": account_id, "credit_amount": credit_amount, "status": "posted"}

    Raises:
        ValueError if account_id is empty or credit_amount is negative.
    """
    if not account_id:
        raise ValueError("account_id is required")
    if credit_amount < 0:
        raise ValueError("credit_amount must be non-negative")

    return {
        "entry_type": "credit",
        "customer_field": CUSTOMER_IDENTITY_FIELD,
        "customer_value": account_id,
        CREDIT_FIELD_NAME: credit_amount,
        "status": "posted",
    }
