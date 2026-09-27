"""
COLLIDER semantic concept registry.

Every cross-boundary concept the Semantic CI gate checks is declared here once:
where each workstream expresses it, and what the gate does when the source is
silent and the workstreams happen to agree.

The gate applies the same truth table to every concept:

  resolved canon exists      → any dependent that differs is AGENT_DRIFT (RESOLVED_CANON)
  source explicit            → any workstream that differs is AGENT_DRIFT (EXPLICIT_SOURCE)
  source silent + disagree   → SPEC_GAP / UNKNOWN → human decision required
  source silent + agree      → SHARED ASSUMPTION, INFERRED, never OBSERVED

The last row has two policies:

  BLOCK     the question has already been raised (it was observed as a SPEC_GAP
            in baseline-001). A question once raised is closed only by authority,
            never by later agreement, so agreement without canon keeps the gate at
            DECISION_REQUIRED.
  DISCLOSE  no divergence has been observed yet. The agreement is reported as an
            unratified assumption: non-blocking, INFERRED, visible. The moment any
            future change makes the workstreams disagree, it becomes a SPEC_GAP.

Nothing in this file is taken from HTTP input.
"""

CONCEPTS = {
    "field_name": {
        "label": "money field name",
        "workstreams": {
            "api": "api_money_field",
            "ledger": "ledger_money_field",
            "notifications": "notifications_money_field",
        },
        "unresolved_agreement": "DISCLOSE",
        "question": None,  # decided by the source (API contract stub)
    },
    "customer_identity": {
        "label": "durable customer identity",
        "workstreams": {
            "api": "api_customer_identity_field",
            "ledger": "ledger_customer_identity_field",
        },
        "unresolved_agreement": "BLOCK",
        "question_raised_by": "baseline-001",
        "question": (
            "Which field should identify the customer at the API/Ledger boundary "
            "for credit operations — account_id (stable internal key) or "
            "email (portable but mutable)?"
        ),
    },
    "money_representation": {
        "label": "money unit",
        "workstreams": {
            "api": "api_money_unit",
            "ledger": "ledger_money_unit",
            "notifications": "notifications_money_unit",
        },
        "unresolved_agreement": "DISCLOSE",
        "question": (
            "What unit does the integer refund_amount carry across the API, Ledger "
            "and Notifications boundaries — integer cents or decimal dollars?"
        ),
    },
}

# Gate evaluation order (also the order findings are reported in).
ORDER = ("field_name", "customer_identity", "money_representation")

POLICIES = ("BLOCK", "DISCLOSE")

assert set(ORDER) == set(CONCEPTS)
assert all(c["unresolved_agreement"] in POLICIES for c in CONCEPTS.values())


def values_for(concept: str, facts: dict) -> dict:
    """{workstream: observed value} for one concept, from gate facts."""
    return {ws: facts[key] for ws, key in CONCEPTS[concept]["workstreams"].items()}
