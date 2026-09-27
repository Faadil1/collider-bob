from collider.pr_gate import evaluate_changed_semantics


MEMORY = {
    "schema": "collider.decision-memory/v1",
    "decisions": [
        {
            "decision_id": "decision-001",
            "concept": "customer_identity",
            "canonical_value": "account_id",
            "decision_state": "CANONICAL",
        }
    ],
}

BRIEF = """
After a failed charge, credit the customer and notify them.
request_body:
  refund_amount: integer
"""


def facts(
    *,
    api_identity="email",
    ledger_identity="account_id",
    api_field="refund_amount",
    ledger_field="credit_amount",
    notifications_field="refund_amount",
    api_unit="integer_cents",
    ledger_unit="integer_cents",
    notifications_unit="integer_cents",
):
    return {
        "api_customer_identity_field": api_identity,
        "ledger_customer_identity_field": ledger_identity,
        "api_money_field": api_field,
        "ledger_money_field": ledger_field,
        "notifications_money_field": notifications_field,
        "api_money_unit": api_unit,
        "ledger_money_unit": ledger_unit,
        "notifications_money_unit": notifications_unit,
    }


def test_unrelated_change_is_merge_allowed():
    base = facts()
    head = facts()

    result = evaluate_changed_semantics(
        base_facts=base,
        head_facts=head,
        decision_memory=MEMORY,
        brief_text=BRIEF,
    )

    assert result["verdict"] == "MERGE_ALLOWED"
    assert result["changed_concepts"] == []


def test_canon_violation_is_merge_blocked():
    base = facts()
    head = facts(ledger_identity="email")

    result = evaluate_changed_semantics(
        base_facts=base,
        head_facts=head,
        decision_memory=MEMORY,
        brief_text=BRIEF,
    )

    assert result["verdict"] == "MERGE_BLOCKED"
    finding = result["findings"][0]
    assert finding["kind"] == "AGENT_DRIFT"
    assert finding["authority"] == "RESOLVED_CANON"
    assert finding["concept"] == "customer_identity"
    assert finding["canonical_value"] == "account_id"


def test_source_explicit_violation_is_merge_blocked():
    base = facts()
    head = facts(api_field="credit_amount")

    result = evaluate_changed_semantics(
        base_facts=base,
        head_facts=head,
        decision_memory=MEMORY,
        brief_text=BRIEF,
    )

    assert result["verdict"] == "MERGE_BLOCKED"
    finding = result["findings"][0]
    assert finding["authority"] == "EXPLICIT_SOURCE"
    assert finding["concept"] == "field_name"
    assert finding["canonical_value"] == "refund_amount"


def test_new_source_silent_disagreement_requires_decision():
    base = facts()
    head = facts(ledger_unit="decimal_dollars")

    result = evaluate_changed_semantics(
        base_facts=base,
        head_facts=head,
        decision_memory=MEMORY,
        brief_text=BRIEF,
    )

    assert result["verdict"] == "DECISION_REQUIRED"
    finding = result["findings"][0]
    assert finding["kind"] == "SPEC_GAP"
    assert finding["authority"] == "SOURCE_SILENT"
    assert finding["concept"] == "money_representation"
    assert finding["epistemic_state"] == "UNKNOWN"


def test_semantic_change_that_conforms_to_canon_is_allowed():
    base = facts(api_identity="email")
    head = facts(api_identity="account_id")

    result = evaluate_changed_semantics(
        base_facts=base,
        head_facts=head,
        decision_memory=MEMORY,
        brief_text=BRIEF,
    )

    assert result["verdict"] == "MERGE_ALLOWED"
    assert result["findings"] == []
    assert result["changed_concepts"][0]["concept"] == "customer_identity"
