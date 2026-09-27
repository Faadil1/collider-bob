import json
from pathlib import Path

import pytest

from collider.bob_live import LiveBobEvidenceError, validate_live_bundle
from collider.bob_rules import render_decision_rules
from collider.decision_compiler import compile_decision

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_live_bundle(root: Path, session_ref: str = "bob-session-123") -> None:
    root.mkdir(parents=True, exist_ok=True)
    for i, workstream in enumerate(("api", "ledger", "notifications"), start=1):
        obj = {
            "agent_id": f"bob-{workstream}-{i}",
            "workstream": workstream,
            "generation_mode": "LIVE_BOB",
            "session_ref": session_ref,
            "task_summary_ref": f"task-summary-{workstream}",
            "run_id": "live-bob-test",
            "git_commit": "abc123",
            "timestamp": "2026-09-27T10:00:00Z",
            "claims": [
                {
                    "concept": "money_representation",
                    "value": "integer_cents",
                    "epistemic_state": "INFERRED",
                    "evidence_refs": [
                        "fixtures/failed-payment/BRIEF.md — integer type; unit not specified"
                    ],
                    "evidence_relation": "INFERRED",
                    "consumed_by": [],
                    "artifact_refs": [f"{workstream}/artifact.py"],
                }
            ],
        }
        (root / f"{workstream}.json").write_text(json.dumps(obj))


def test_live_bob_bundle_accepts_three_unique_provenance_bound_agents(tmp_path):
    interpretations = tmp_path / "interpretations"
    _write_live_bundle(interpretations)

    receipt = validate_live_bundle(interpretations, "bob-session-123")

    assert receipt["execution_source"] == "LIVE_BOB_SESSION"
    assert receipt["interpretation_source"] == "LIVE_BOB"
    assert receipt["session_ref"] == "bob-session-123"
    assert receipt["unique_agents"] == 3
    assert len(receipt["artifacts"]) == 3
    assert len(receipt["bundle_sha256"]) == 64


def test_live_bob_bundle_rejects_preseeded_relabel(tmp_path):
    interpretations = tmp_path / "interpretations"
    _write_live_bundle(interpretations)

    api = json.loads((interpretations / "api.json").read_text())
    api["generation_mode"] = "PRESEEDED"
    (interpretations / "api.json").write_text(json.dumps(api))

    with pytest.raises(LiveBobEvidenceError, match="generation_mode must be LIVE_BOB"):
        validate_live_bundle(interpretations, "bob-session-123")


def test_live_bob_bundle_rejects_wrong_session_ref(tmp_path):
    interpretations = tmp_path / "interpretations"
    _write_live_bundle(interpretations)

    with pytest.raises(LiveBobEvidenceError, match="session_ref does not match"):
        validate_live_bundle(interpretations, "different-session")


def test_live_bob_bundle_rejects_duplicate_agent_identity(tmp_path):
    interpretations = tmp_path / "interpretations"
    _write_live_bundle(interpretations)

    api = json.loads((interpretations / "api.json").read_text())
    ledger = json.loads((interpretations / "ledger.json").read_text())
    ledger["agent_id"] = api["agent_id"]
    (interpretations / "ledger.json").write_text(json.dumps(ledger))

    with pytest.raises(LiveBobEvidenceError, match="unique agent_id"):
        validate_live_bundle(interpretations, "bob-session-123")


def test_live_bob_bundle_rejects_observed_claim_without_evidence(tmp_path):
    interpretations = tmp_path / "interpretations"
    _write_live_bundle(interpretations)

    api = json.loads((interpretations / "api.json").read_text())
    api["claims"][0]["epistemic_state"] = "OBSERVED"
    api["claims"][0]["evidence_relation"] = "EXPLICIT"
    api["claims"][0]["evidence_refs"] = []
    (interpretations / "api.json").write_text(json.dumps(api))

    with pytest.raises(LiveBobEvidenceError, match="OBSERVED requires"):
        validate_live_bundle(interpretations, "bob-session-123")


def test_decision_memory_exports_as_bob_workspace_rule():
    memory = {
        "schema": "collider.decision-memory/v1",
        "decisions": [
            {
                "decision_id": "decision-live-1",
                "concept": "customer_identity",
                "canonical_value": "account_id",
                "decision_state": "CANONICAL",
                "decision_source": "human",
                "human_decision_source": "INTERACTIVE",
                "prior_classification": "SPEC_GAP",
                "evidence_state": "OBSERVED",
            }
        ],
    }

    rendered = render_decision_rules(memory, "canon/decision-memory.json")

    assert "## customer_identity" in rendered
    assert "Canonical value: `account_id`" in rendered
    assert "Decision ID: `decision-live-1`" in rendered
    assert "Run the COLLIDER semantic guard" in rendered
    assert "future Bob agent's compliance is not proven" in rendered



def _write_fixture_live_bundle(root: Path, session_ref: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    fixture_dir = PROJECT_ROOT / "fixtures/failed-payment/interpretations"

    for workstream in ("api", "ledger", "notifications"):
        obj = json.loads((fixture_dir / f"{workstream}.json").read_text())
        obj["agent_id"] = f"bob-live-{workstream}"
        obj["generation_mode"] = "LIVE_BOB"
        obj["session_ref"] = session_ref
        obj["task_summary_ref"] = f"bob-task-summary-{workstream}"
        obj["run_id"] = "live-compiler-test"
        (root / f"{workstream}.json").write_text(json.dumps(obj))


def test_decision_compiler_consumes_validated_live_bob_bundle(tmp_path):
    session_ref = "bob-session-live-compiler"
    interpretations = tmp_path / "interpretations"
    _write_fixture_live_bundle(interpretations, session_ref)

    result = compile_decision(
        "customer_identity",
        "account_id",
        human_decision_source="INTERACTIVE_BOB",
        decision_id="live-bob-decision-test",
        source_root=PROJECT_ROOT,
        workspace=tmp_path / "workspace",
        out_dir=tmp_path / "receipts",
        interpretation_source="LIVE_BOB",
        interpretation_dir=interpretations,
        bob_session_ref=session_ref,
    )

    provenance = result["memory"]["provenance"]
    assert provenance["interpretation_source"] == "LIVE_BOB"
    assert provenance["bob_session_ref"] == session_ref
    assert len(provenance["live_bob_input_bundle_sha256"]) == 64
    assert provenance["human_decision_source"] == "INTERACTIVE_BOB"

    truth = result["manifest"]["truth_boundary"]
    assert truth["interpretations"] == "LIVE_BOB"
    assert truth["live_bob"] == "INTERPRETATION_INPUT_VALIDATED"
    assert truth["fresh_agent_replay"] == "NOT_EXECUTED / PENDING_LIVE_BOB"

    assert result["gate_after"]["verdict"] == "SEMANTICALLY_READY"
    assert result["memory"]["verification"]["tests_failed"] == 0
    assert (tmp_path / "receipts" / "bob-live-input.json").is_file()

    copied_api = json.loads(
        (tmp_path / "workspace" / "fixtures/failed-payment/interpretations/api.json").read_text()
    )
    assert copied_api["generation_mode"] == "LIVE_BOB"
    assert copied_api["session_ref"] == session_ref


def test_decision_compiler_refuses_live_bob_without_real_session_ref(tmp_path):
    interpretations = tmp_path / "interpretations"
    _write_fixture_live_bundle(interpretations, "bob-session-required")

    with pytest.raises(ValueError, match="real Bob session reference"):
        compile_decision(
            "customer_identity",
            "account_id",
            human_decision_source="INTERACTIVE_BOB",
            decision_id="missing-session-test",
            source_root=PROJECT_ROOT,
            workspace=tmp_path / "workspace",
            out_dir=tmp_path / "receipts",
            interpretation_source="LIVE_BOB",
            interpretation_dir=interpretations,
            bob_session_ref=None,
        )
