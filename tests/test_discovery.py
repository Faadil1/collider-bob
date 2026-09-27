import pytest

from collider.discovery import (
    DiscoveryValidationError,
    group_proposals,
    validate_proposal,
)


def proposal(**overrides):
    base = {
        "proposal_id": "p-api-identity",
        "concept": "customer_identity",
        "label": "durable customer identity",
        "workstream": "api",
        "value": "email",
        "epistemic_state": "INFERRED",
        "source_relation": "SILENT",
        "source_refs": [],
        "artifact_refs": ["api/handlers/recover.py:CUSTOMER_IDENTITY_FIELD"],
        "generation_mode": "LOCAL",
        "status": "PROPOSED",
    }
    base.update(overrides)
    return base


def test_discovery_proposal_stays_proposed():
    item = validate_proposal(proposal())
    assert item["status"] == "PROPOSED"


def test_discovery_rejects_model_confidence_as_authority():
    with pytest.raises(DiscoveryValidationError, match="confidence"):
        validate_proposal(proposal(confidence=0.99))


def test_source_silence_cannot_be_observed_authority():
    with pytest.raises(DiscoveryValidationError, match="source-silent"):
        validate_proposal(proposal(epistemic_state="OBSERVED"))


def test_explicit_relation_requires_source_reference():
    with pytest.raises(DiscoveryValidationError, match="source_ref"):
        validate_proposal(
            proposal(source_relation="EXPLICIT", epistemic_state="OBSERVED")
        )


def test_live_bob_requires_real_provenance_fields():
    with pytest.raises(DiscoveryValidationError, match="session_ref"):
        validate_proposal(proposal(generation_mode="LIVE_BOB"))

    item = validate_proposal(
        proposal(
            generation_mode="LIVE_BOB",
            session_ref="session-1",
            task_summary_ref="task-1",
            agent_id="agent-1",
        )
    )
    assert item["generation_mode"] == "LIVE_BOB"


def test_grouping_never_promotes_consensus_to_canon():
    items = [
        proposal(proposal_id="p-api", workstream="api", value="account_id"),
        proposal(
            proposal_id="p-ledger",
            workstream="ledger",
            value="account_id",
            artifact_refs=["ledger/credit_entry.py:CUSTOMER_IDENTITY_FIELD"],
        ),
    ]
    snapshot = group_proposals(items)["customer_identity"]
    assert snapshot["workstream_values"] == {
        "api": "account_id",
        "ledger": "account_id",
    }
    assert snapshot["authority_state"] == "UNRATIFIED"
    assert snapshot["canonical_value"] is None


def test_grouping_preserves_disagreement_for_later_adjudication():
    items = [
        proposal(proposal_id="p-api", workstream="api", value="email"),
        proposal(
            proposal_id="p-ledger",
            workstream="ledger",
            value="account_id",
            artifact_refs=["ledger/credit_entry.py:CUSTOMER_IDENTITY_FIELD"],
        ),
    ]
    snapshot = group_proposals(items)["customer_identity"]
    assert set(snapshot["workstream_values"].values()) == {"email", "account_id"}
    assert snapshot["authority_state"] == "UNRATIFIED"
