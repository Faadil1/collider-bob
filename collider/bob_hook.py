"""
IBM Bob lifecycle-hook integration for COLLIDER.

SessionStart:
- captures Bob's real session_id from hook stdin;
- fingerprints the current Git state;
- reads canonical decision memory;
- evaluates the current COLLIDER gate;
- writes a transient machine receipt;
- prints concise semantic context back into Bob's model context.

Stop:
- captures the same session_id and final repository/gate state;
- writes a transient stop receipt.

Receipts live under .collider/ and are not canonical submission evidence until
reviewed. A hook receipt proves that Bob opened/stopped a session in this
workspace; it does NOT prove that subagents produced LIVE_BOB interpretations.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from collider.gate import evaluate_gate

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "evidence/decisions/decision-001/decision-memory.json"
RECEIPT_DIR = ROOT / ".collider/bob-hooks"


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "UNKNOWN"


def _read_payload(stream=None) -> dict[str, Any]:
    stream = stream or sys.stdin
    raw = stream.read()
    if not raw.strip():
        return {}
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("Bob hook payload must be a JSON object")
    return obj


def _decision_summary() -> list[dict[str, Any]]:
    if not MEMORY.exists():
        return []
    memory = json.loads(MEMORY.read_text())
    result = []
    for record in memory.get("decisions", []):
        if record.get("decision_state") != "CANONICAL":
            continue
        result.append(
            {
                "decision_id": record.get("decision_id"),
                "concept": record.get("concept"),
                "canonical_value": record.get("canonical_value"),
                "human_decision_source": record.get("human_decision_source"),
            }
        )
    return result


def build_receipt(event: str, session_id: str) -> dict[str, Any]:
    gate = evaluate_gate(ROOT)
    return {
        "schema": "collider.bob-hook/v1",
        "event": event,
        "captured_at": _now(),
        "session_id": session_id,
        "git": {
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "commit": _git("rev-parse", "HEAD"),
            "working_tree_clean": _git("status", "--porcelain") == "",
        },
        "semantic_gate": {
            "verdict": gate["verdict"],
            "findings": [
                {
                    "kind": finding.get("kind"),
                    "concept": finding.get("concept"),
                }
                for finding in gate.get("findings", [])
            ],
            "assumptions": [
                {
                    "concept": assumption.get("concept"),
                    "epistemic_state": assumption.get("epistemic_state"),
                }
                for assumption in gate.get("assumptions", [])
            ],
        },
        "canonical_decisions": _decision_summary(),
        "truth_boundary": {
            "hook_receipt_is_live_bob_interpretation_proof": False,
            "preseeded_can_be_relabelled_live_bob": False,
            "fresh_agent_replay_proven_by_hook": False,
        },
    }


def write_receipt(receipt: dict[str, Any]) -> Path:
    session_id = str(receipt.get("session_id") or "unknown").replace("/", "_")
    event = str(receipt["event"]).lower()
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPT_DIR / f"{session_id}-{event}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    return path


def render_session_context(receipt: dict[str, Any]) -> str:
    decisions = receipt.get("canonical_decisions", [])
    decision_text = (
        ", ".join(
            f"{d['concept']}={d['canonical_value']} ({d['decision_id']})"
            for d in decisions
        )
        if decisions
        else "none"
    )
    findings = receipt["semantic_gate"]["findings"]
    finding_text = (
        ", ".join(f"{f['kind']}:{f['concept']}" for f in findings)
        if findings
        else "none"
    )
    return "\n".join(
        [
            "[COLLIDER SESSION CONTEXT]",
            f"Bob session: {receipt['session_id']}",
            f"Git: {receipt['git']['branch']} @ {receipt['git']['commit']}",
            f"Semantic gate: {receipt['semantic_gate']['verdict']}",
            f"Findings: {finding_text}",
            f"Canonical decisions: {decision_text}",
            (
                "Truth boundary: consensus is not authority; PRESEEDED is never "
                "LIVE_BOB; a hook receipt is not fresh-agent replay proof."
            ),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="COLLIDER IBM Bob lifecycle hook")
    parser.add_argument("event", choices=("session-start", "stop"))
    args = parser.parse_args()

    try:
        payload = _read_payload()
        session_id = str(payload.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("Bob hook payload is missing session_id")

        expected = "SessionStart" if args.event == "session-start" else "Stop"
        observed = payload.get("event")
        if observed and observed != expected:
            raise ValueError(
                f"hook event mismatch: expected {expected}, received {observed}"
            )

        receipt = build_receipt(expected, session_id)
        write_receipt(receipt)

        if args.event == "session-start":
            print(render_session_context(receipt))

        return 0
    except Exception as exc:
        # Lifecycle integration must never lock a user out of Bob. Failure is
        # logged to stderr; the hook exits non-blocking.
        print(f"COLLIDER Bob hook warning: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
