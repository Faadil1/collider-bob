"""
COLLIDER live IBM Bob interpretation validation.

This module is the provenance gate between Bob subagent output and the COLLIDER
pipeline. It deliberately refuses to consume an interpretation as LIVE_BOB
unless the artifact carries a real Bob session reference and a task-summary
reference, uses the LIVE_BOB generation mode, and satisfies the interpretation
contract.

It does not call Bob itself. Bob executes the subagents; this module validates
and fingerprints what Bob produced before COLLIDER consumes it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

EXPECTED_WORKSTREAMS = ("api", "ledger", "notifications")
REQUIRED_TOP_LEVEL = (
    "agent_id",
    "workstream",
    "generation_mode",
    "session_ref",
    "task_summary_ref",
    "claims",
)
REQUIRED_CLAIM_FIELDS = (
    "concept",
    "value",
    "epistemic_state",
    "evidence_refs",
    "evidence_relation",
    "consumed_by",
    "artifact_refs",
)
ALLOWED_EPISTEMIC_STATES = {"OBSERVED", "INFERRED", "UNKNOWN"}
ALLOWED_EVIDENCE_RELATIONS = {"EXPLICIT", "INFERRED", "UNAVAILABLE", "CONFLICTING"}


class LiveBobEvidenceError(ValueError):
    """Raised when a purported LIVE_BOB bundle fails provenance validation."""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_claim(claim: dict[str, Any], *, workstream: str, index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"{workstream}.claims[{index}]"

    for field in REQUIRED_CLAIM_FIELDS:
        if field not in claim:
            errors.append(f"{prefix}: missing field {field}")

    if "confidence" in claim:
        errors.append(f"{prefix}: confidence is forbidden; cite evidence instead")

    state = claim.get("epistemic_state")
    if state not in ALLOWED_EPISTEMIC_STATES:
        errors.append(f"{prefix}: invalid epistemic_state {state!r}")

    relation = claim.get("evidence_relation")
    if relation not in ALLOWED_EVIDENCE_RELATIONS:
        errors.append(f"{prefix}: invalid evidence_relation {relation!r}")

    evidence_refs = claim.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        errors.append(f"{prefix}: evidence_refs must be a list")
        evidence_refs = []

    if state == "OBSERVED" and not evidence_refs:
        errors.append(f"{prefix}: OBSERVED requires at least one evidence_ref")

    if relation == "EXPLICIT" and not evidence_refs:
        errors.append(f"{prefix}: EXPLICIT requires at least one evidence_ref")

    for list_field in ("consumed_by", "artifact_refs"):
        value = claim.get(list_field)
        if not isinstance(value, list):
            errors.append(f"{prefix}: {list_field} must be a list")

    if not claim.get("concept"):
        errors.append(f"{prefix}: concept must be non-empty")

    return errors


def validate_live_interpretation(
    obj: dict[str, Any],
    *,
    expected_workstream: str,
    session_ref: str,
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_TOP_LEVEL:
        if field not in obj:
            errors.append(f"{expected_workstream}: missing field {field}")

    if obj.get("workstream") != expected_workstream:
        errors.append(
            f"{expected_workstream}: workstream field is {obj.get('workstream')!r}"
        )

    if obj.get("generation_mode") != "LIVE_BOB":
        errors.append(
            f"{expected_workstream}: generation_mode must be LIVE_BOB, "
            f"got {obj.get('generation_mode')!r}"
        )

    if obj.get("session_ref") != session_ref:
        errors.append(
            f"{expected_workstream}: session_ref does not match requested Bob session"
        )

    if not str(obj.get("task_summary_ref", "")).strip():
        errors.append(f"{expected_workstream}: task_summary_ref must be non-empty")

    if not str(obj.get("agent_id", "")).strip():
        errors.append(f"{expected_workstream}: agent_id must be non-empty")

    claims = obj.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append(f"{expected_workstream}: claims must be a non-empty list")
    else:
        for i, claim in enumerate(claims):
            if not isinstance(claim, dict):
                errors.append(f"{expected_workstream}.claims[{i}]: must be an object")
                continue
            errors.extend(
                _validate_claim(claim, workstream=expected_workstream, index=i)
            )

    return errors


def validate_live_bundle(interpretations_dir: str | Path, session_ref: str) -> dict[str, Any]:
    root = Path(interpretations_dir)

    if not session_ref.strip():
        raise LiveBobEvidenceError("LIVE_BOB validation requires a real session_ref")

    if not root.is_dir():
        raise LiveBobEvidenceError(f"interpretations directory does not exist: {root}")

    errors: list[str] = []
    agents: list[str] = []
    artifacts: list[dict[str, Any]] = []

    for workstream in EXPECTED_WORKSTREAMS:
        path = root / f"{workstream}.json"
        if not path.is_file():
            errors.append(f"missing interpretation file: {path}")
            continue

        try:
            obj = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue

        if not isinstance(obj, dict):
            errors.append(f"{path}: top-level JSON must be an object")
            continue

        errors.extend(
            validate_live_interpretation(
                obj,
                expected_workstream=workstream,
                session_ref=session_ref,
            )
        )

        if str(obj.get("agent_id", "")).strip():
            agents.append(str(obj["agent_id"]))

        artifacts.append(
            {
                "workstream": workstream,
                "path": str(path),
                "sha256": _sha256(path),
                "agent_id": obj.get("agent_id"),
                "task_summary_ref": obj.get("task_summary_ref"),
            }
        )

    if len(agents) != len(set(agents)):
        errors.append("LIVE_BOB workstreams must use unique agent_id values")

    if len(agents) != len(EXPECTED_WORKSTREAMS):
        errors.append(
            f"expected {len(EXPECTED_WORKSTREAMS)} validated agents, got {len(agents)}"
        )

    if errors:
        raise LiveBobEvidenceError("\n".join(errors))

    bundle_material = "\n".join(
        f"{item['workstream']}:{item['sha256']}" for item in artifacts
    ).encode()
    bundle_sha256 = hashlib.sha256(bundle_material).hexdigest()

    return {
        "schema": "collider.live-bob-input/v1",
        "validated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "execution_source": "LIVE_BOB_SESSION",
        "interpretation_source": "LIVE_BOB",
        "session_ref": session_ref,
        "workstreams": list(EXPECTED_WORKSTREAMS),
        "unique_agents": len(set(agents)),
        "artifacts": artifacts,
        "bundle_sha256": bundle_sha256,
        "truth_boundary": {
            "validated": (
                "Artifacts satisfy COLLIDER's LIVE_BOB provenance contract."
            ),
            "not_proven": (
                "This receipt alone does not prove fresh-agent replay or that any "
                "human decision was interactive."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate provenance for a LIVE_BOB interpretation bundle"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("--interpretations-dir", required=True)
    validate.add_argument("--session-ref", required=True)
    validate.add_argument("--receipt")

    args = parser.parse_args()

    try:
        receipt = validate_live_bundle(args.interpretations_dir, args.session_ref)
    except LiveBobEvidenceError as exc:
        print("LIVE_BOB INPUT REJECTED")
        print(str(exc))
        return 2

    rendered = json.dumps(receipt, indent=2)
    print("LIVE_BOB INPUT ACCEPTED")
    print(rendered)

    if args.receipt:
        out = Path(args.receipt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered + "\n")
        print(f"wrote {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
