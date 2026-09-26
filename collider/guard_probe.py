"""
COLLIDER GUARD probe — a controlled future-agent change against persisted canon.

Runs inside an existing decision-compiled workspace, never the source tree:

  1. read decision memory           customer_identity = account_id
  2. apply the future-agent change  api/handlers/recover.py
                                    CUSTOMER_IDENTITY_FIELD: account_id → email
  3. run the Semantic CI gate       expect AGENT_DRIFT vs RESOLVED_CANON
  4. emit the guard verdict         MERGE_BLOCKED (only if the gate really blocked)
  5. run the regression contract    expect failures on the violating tree
  6. restore the exact prior bytes  (always, in `finally`)
  7. re-run the gate                expect SEMANTICALLY_READY, 0 conflicts

The probe is fixed: this slice allows exactly one probe, the canonical demo
attack customer_identity account_id → email. It is NOT the fresh-agent
replay; no independent agent is involved.
"""

import difflib
import hashlib
import json
import re
from pathlib import Path

from collider import gate as gate_mod
from collider.decision_compiler import (
    EXECUTION_ENVIRONMENTS,
    now_iso,
    tracked_files,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]

# The one allowed probe. Nothing here is taken from HTTP input.
PROBE = {
    "concept": "customer_identity",
    "canonical_value": "account_id",
    "attempted_value": "email",
    "affected_workstream": "api",
    "affected_file": "api/handlers/recover.py",
    "constant": "CUSTOMER_IDENTITY_FIELD",
}

RECEIPT_NAME = "guard-probe.json"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def strip(g: dict) -> dict:
    return {k: v for k, v in g.items() if k != "verification_output"}


def summarize_run(v: dict) -> dict:
    return {k: v[k] for k in (
        "command", "exit_code", "passed", "passed_count", "failed_count", "error_count",
    )}


def run_guard_probe(workspace: Path, out_dir: Path, source_root: Path = ROOT,
                    execution_environment: str = "LOCAL") -> dict:
    if execution_environment not in EXECUTION_ENVIRONMENTS:
        raise ValueError(f"execution_environment must be one of {EXECUTION_ENVIRONMENTS}")
    workspace = Path(workspace).resolve()
    out_dir = Path(out_dir).resolve()
    source_root = Path(source_root).resolve()
    receipt_path = out_dir / RECEIPT_NAME

    if receipt_path.exists():
        raise FileExistsError(f"REFUSE: guard probe already recorded: {receipt_path}")
    if workspace == source_root:
        raise ValueError("REFUSE: guard probe must run in a compiled workspace, not the source tree")

    # 1. Decision memory is the authority.
    memory_path = workspace / gate_mod.MEMORY_RELPATH
    if not memory_path.exists():
        raise RuntimeError("REFUSE: no decision memory in workspace; nothing to guard")
    memory = json.loads(memory_path.read_text())
    record = next(
        (d for d in memory.get("decisions", []) if d.get("concept") == PROBE["concept"]),
        None,
    )
    if record is None or record.get("decision_state") != "CANONICAL":
        raise RuntimeError(f"REFUSE: no CANONICAL decision for {PROBE['concept']}")
    if record["canonical_value"] != PROBE["canonical_value"]:
        raise ValueError(
            "REFUSE: the only allowed probe is customer_identity account_id → email; "
            f"memory holds {record['canonical_value']!r}"
        )

    source_before = tracked_files(source_root)

    gate_before = gate_mod.evaluate_gate(workspace)
    if gate_before["verdict"] != "SEMANTICALLY_READY":
        raise RuntimeError(
            f"REFUSE: workspace must be SEMANTICALLY_READY before probing; "
            f"it is {gate_before['verdict']}"
        )

    target = workspace / PROBE["affected_file"]
    original = target.read_bytes()
    sha_before = sha256_bytes(original)
    pattern = rf'^({PROBE["constant"]}\s*=\s*)"{re.escape(PROBE["canonical_value"])}"'
    if not re.search(pattern, original.decode(), flags=re.M):
        raise RuntimeError(
            f"REFUSE: {PROBE['affected_file']} does not hold "
            f"{PROBE['constant']} = \"{PROBE['canonical_value']}\""
        )

    contract_rel = record["regression_artifact_ref"]
    restoration_applied = False
    try:
        # 2. Future-agent change.
        mutated = re.sub(
            pattern, rf'\1"{PROBE["attempted_value"]}"', original.decode(),
            count=1, flags=re.M,
        )
        target.write_text(mutated)
        sha_during = sha256_bytes(target.read_bytes())
        probe_diff = "".join(difflib.unified_diff(
            original.decode().splitlines(keepends=True),
            mutated.splitlines(keepends=True),
            fromfile=f"a/{PROBE['affected_file']}",
            tofile=f"b/{PROBE['affected_file']} (future agent)",
        ))

        # 3. Gate on the violating tree.
        gate_during = gate_mod.evaluate_gate(workspace)

        # 5. Regression contract on the violating tree.
        contract_during = gate_mod.run_pytest(workspace, [contract_rel])
        full_during = gate_mod.run_verification(workspace)
    finally:
        # 6. Always restore the exact prior bytes.
        target.write_bytes(original)
        restoration_applied = True

    sha_after_restore = sha256_bytes(target.read_bytes())

    # 7. Gate after restoration.
    gate_after = gate_mod.evaluate_gate(workspace)
    contract_after = gate_mod.run_pytest(workspace, [contract_rel])

    # 4. The guard verdict is derived from what the gate observed, not assumed.
    violation = next(
        (f for f in gate_during["findings"]
         if f["kind"] == "AGENT_DRIFT"
         and f["concept"] == PROBE["concept"]
         and f["authority"] == "RESOLVED_CANON"
         and f["violations"].get(PROBE["affected_workstream"]) == PROBE["attempted_value"]),
        None,
    )
    blocked = gate_during["verdict"] != "SEMANTICALLY_READY" and violation is not None
    guard_verdict = "MERGE_BLOCKED" if blocked else "GUARD_DID_NOT_BLOCK"

    restoration_verified = (
        sha_after_restore == sha_before
        and gate_after["verdict"] == "SEMANTICALLY_READY"
        and gate_after["integration"]["conflict_count"] == 0
        and contract_after["passed"]
    )
    source_untouched = tracked_files(source_root) == source_before

    receipt = {
        "probe": "future-agent-change",
        "is_fresh_agent_replay": False,
        "decision_id": record["decision_id"],
        "concept": PROBE["concept"],
        "canonical_value": record["canonical_value"],
        "attempted_value": PROBE["attempted_value"],
        "affected_workstream": PROBE["affected_workstream"],
        "affected_file": PROBE["affected_file"],
        "decision_memory_ref": gate_mod.MEMORY_RELPATH,
        "decision_memory_value": record["canonical_value"],
        "regression_contract": contract_rel,
        "sha_before_probe": sha_before,
        "sha_during_probe": sha_during,
        "probe_diff": probe_diff,
        "gate_before_probe": gate_before["verdict"],
        "gate_during_probe": gate_during["verdict"],
        "gate_during_findings": gate_during["findings"],
        "integration_during_probe": gate_during["integration"],
        "violation": violation,
        "guard_verdict": guard_verdict,
        "verification_during_probe": {
            "regression_contract": summarize_run(contract_during),
            "full_suite": summarize_run(full_during),
        },
        "restoration_applied": restoration_applied,
        "sha_after_restore": sha_after_restore,
        "restored_exact_bytes": sha_after_restore == sha_before,
        "gate_after_restore": gate_after["verdict"],
        "integration_after_restore": gate_after["integration"],
        "verification_after_restore": {
            "regression_contract": summarize_run(contract_after),
            "full_suite": {k: v for k, v in (gate_after["verification"] or {}).items()
                           if k not in ("cwd", "contract_files")},
        },
        "restoration_verified": restoration_verified,
        "source_tree_untouched": source_untouched,
        "executed_at": now_iso(),
        "truth_boundary": {
            "execution": execution_environment,
            "kind": "controlled future-change probe against persisted canon",
            "fresh_agent_replay": "NOT_EXECUTED / PENDING_LIVE_BOB",
        },
    }
    write_json(receipt_path, receipt)
    return receipt


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="COLLIDER guard probe")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    r = run_guard_probe(Path(args.workspace), Path(args.out_dir))
    print(f"MEMORY     {r['concept']} = {r['decision_memory_value']}")
    print(f"ATTEMPT    {r['canonical_value']} → {r['attempted_value']}  ({r['affected_file']})")
    print(f"GATE       during probe: {r['gate_during_probe']}")
    c = r["verification_during_probe"]["regression_contract"]
    print(f"CONTRACT   during probe: {c['passed_count']} passed, {c['failed_count']} failed")
    print(f"GUARD      {r['guard_verdict']}")
    print(f"RESTORE    exact bytes={r['restored_exact_bytes']}  gate={r['gate_after_restore']}  "
          f"conflicts={r['integration_after_restore']['conflict_count']}")
    print(f"VERIFIED   {r['restoration_verified']}")
    sys.exit(0 if r["guard_verdict"] == "MERGE_BLOCKED" and r["restoration_verified"] else 1)
