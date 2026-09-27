"""
COLLIDER fresh-agent REPLAY — interface and evidence contract.

Purpose: after a decision is compiled, hand the patched spec (plus canon memory,
never the repaired code) to a FRESH, independent agent and observe whether it
now implements the resolved concept correctly without being told the answer.

This module defines the request and the acceptance contract only. It does not
execute an agent. The live runtime for this step is an independent Bob session. A replay request is
recorded as NOT_EXECUTED / PENDING_LIVE_BOB until an external execution result is
submitted and evaluated. The request builder never fabricates a live result.

A replay result may only be accepted if it comes from an independent execution
source and carries the evidence fields listed in REQUIRED_RESULT_FIELDS.
Anything else is rejected rather than narrated as a pass.
"""

import argparse
import json
from pathlib import Path


INDEPENDENT_EXECUTION_SOURCES = ("LIVE_BOB_SESSION",)

REQUIRED_RESULT_FIELDS = (
    "execution_source",      # must be in INDEPENDENT_EXECUTION_SOURCES
    "session_ref",           # external session identifier
    "agent_id",              # the fresh agent's identity
    "inputs_sha256",         # hash of the replay input bundle actually given
    "emitted_value",         # value the fresh agent chose for the concept
    "tests_passed",          # contract test result against its implementation
    "transcript_ref",        # where the raw agent output is stored
)


def build_replay_request(memory_record: dict, spec_relpath: str,
                         contract_relpath: str) -> dict:
    concept = memory_record["concept"]
    return {
        "replay": "fresh-agent",
        "concept": concept,
        "decision_id": memory_record["decision_id"],
        "status": "NOT_EXECUTED",
        "runtime_state": "PENDING_LIVE_BOB",
        "reason": (
            "Replay requires an independent live agent session. No replay result has "
            "been submitted yet, so the runtime state remains PENDING_LIVE_BOB. "
            "No result is fabricated."
        ),
        "inputs": {
            "patched_spec": spec_relpath,
            "decision_memory": "canon/decision-memory.json",
            "withheld": [
                "repaired implementation files",
                "repair.patch",
                "canonical_value (agent must derive it from the patched spec)",
            ],
        },
        "prompt_contract": (
            f"Implement the {', '.join(memory_record['affected_dependents'])} "
            f"workstream(s) from the patched specification. Emit an "
            f"interpretation object for '{concept}' with epistemic_state and "
            f"evidence_refs."
        ),
        "acceptance": {
            "execution_source_in": list(INDEPENDENT_EXECUTION_SOURCES),
            "emitted_value_equals": "canonical_value from decision memory",
            "emitted_epistemic_state": "OBSERVED (cites patched spec marker)",
            "regression_contract": contract_relpath,
            "required_result_fields": list(REQUIRED_RESULT_FIELDS),
        },
        "result": None,
    }


def evaluate_replay_result(request: dict, result: dict | None,
                           canonical_value: str) -> dict:
    """Deterministically judge a submitted replay result against the contract."""
    if result is None:
        return {"status": "NOT_EXECUTED", "runtime_state": "PENDING_LIVE_BOB",
                "accepted": False, "reasons": ["no replay result submitted"]}

    reasons = [f"missing field: {f}" for f in REQUIRED_RESULT_FIELDS if f not in result]
    if result.get("execution_source") not in INDEPENDENT_EXECUTION_SOURCES:
        reasons.append(
            f"execution_source {result.get('execution_source')!r} is not an "
            "independent execution source"
        )
    if reasons:
        return {"status": "REJECTED", "runtime_state": "INVALID_EVIDENCE",
                "accepted": False, "reasons": reasons}

    ok = result["emitted_value"] == canonical_value and result["tests_passed"] is True
    return {
        "status": "REPLAY_PASS" if ok else "REPLAY_FAIL",
        "runtime_state": result["execution_source"],
        "accepted": ok,
        "reasons": [] if ok else [
            f"emitted_value={result['emitted_value']!r}, "
            f"tests_passed={result['tests_passed']!r}"
        ],
    }


def _write_json(path: str | None, obj: dict) -> None:
    rendered = json.dumps(obj, indent=2)
    if path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered + "\n")
        print(f"wrote {out}")
    else:
        print(rendered)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or evaluate COLLIDER fresh-agent replay evidence"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    req = sub.add_parser("request")
    req.add_argument("--memory", required=True)
    req.add_argument("--spec", required=True)
    req.add_argument("--contract", required=True)
    req.add_argument("--out")

    ev = sub.add_parser("evaluate")
    ev.add_argument("--request", required=True)
    ev.add_argument("--result", required=True)
    ev.add_argument("--canonical-value", required=True)
    ev.add_argument("--receipt")

    args = parser.parse_args()

    if args.command == "request":
        memory = json.loads(Path(args.memory).read_text())
        decisions = memory.get("decisions", [])
        if not decisions:
            print("REPLAY REQUEST REJECTED: no decision memory")
            return 2
        request = build_replay_request(decisions[0], args.spec, args.contract)
        _write_json(args.out, request)
        return 0

    request = json.loads(Path(args.request).read_text())
    result = json.loads(Path(args.result).read_text())
    verdict = evaluate_replay_result(request, result, args.canonical_value)
    receipt = {
        "schema": "collider.fresh-agent-replay-receipt/v1",
        "request": request,
        "result": result,
        "verdict": verdict,
    }
    _write_json(args.receipt, receipt)
    return 0 if verdict["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
