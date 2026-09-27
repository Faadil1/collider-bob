import io
import json

from collider import bob_hook


def test_session_start_context_contains_gate_and_truth_boundary(monkeypatch, tmp_path):
    receipt_dir = tmp_path / "bob-hooks"
    monkeypatch.setattr(bob_hook, "RECEIPT_DIR", receipt_dir)

    receipt = bob_hook.build_receipt("SessionStart", "ses_test_123")
    text = bob_hook.render_session_context(receipt)

    assert "COLLIDER SESSION CONTEXT" in text
    assert "ses_test_123" in text
    assert "Semantic gate:" in text
    assert "PRESEEDED is never LIVE_BOB" in text


def test_hook_receipt_truth_boundary_is_explicit():
    receipt = bob_hook.build_receipt("SessionStart", "ses_truth")

    assert receipt["truth_boundary"]["hook_receipt_is_live_bob_interpretation_proof"] is False
    assert receipt["truth_boundary"]["preseeded_can_be_relabelled_live_bob"] is False
    assert receipt["truth_boundary"]["fresh_agent_replay_proven_by_hook"] is False


def test_write_receipt_uses_real_session_id(monkeypatch, tmp_path):
    receipt_dir = tmp_path / "bob-hooks"
    monkeypatch.setattr(bob_hook, "RECEIPT_DIR", receipt_dir)

    receipt = bob_hook.build_receipt("Stop", "ses_demo")
    path = bob_hook.write_receipt(receipt)

    assert path.name == "ses_demo-stop.json"
    saved = json.loads(path.read_text())
    assert saved["session_id"] == "ses_demo"
    assert saved["event"] == "Stop"


def test_read_payload_accepts_bob_hook_shape():
    payload = bob_hook._read_payload(
        io.StringIO('{"event":"SessionStart","session_id":"ses_abc"}')
    )

    assert payload == {"event": "SessionStart", "session_id": "ses_abc"}
