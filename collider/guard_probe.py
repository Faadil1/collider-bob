"""
COLLIDER GUARD — Semantic CI on a future agent's change, judged against memory.

Runs inside an existing decision-compiled workspace, never the source tree.
One of a fixed set of future-agent changes (PROBES) is applied, the Semantic CI
gate judges it, and the exact prior bytes are restored:

  IDENTITY_REVERT     api: CUSTOMER_IDENTITY_FIELD account_id → email
                      violates resolved canon          → MERGE_BLOCKED
  MONEY_UNIT_DRIFT    ledger: MONEY_UNIT integer_cents → decimal_dollars
                      breaks an unratified shared assumption; every test
                      still passes, but the workstreams now disagree where
                      the source is silent             → DECISION_REQUIRED
  COMPATIBLE_CHANGE   notifications: message wording only
                      touches no semantic concept      → MERGE_ALLOWED

For each probe the receipt also records a counterfactual: the SAME mutated
tree judged with decision memory (and its spec marker) removed. Where the two
verdicts differ, decision memory is what changed the outcome.

Steps (every probe):
  1. read decision memory (the workspace must hold a CANONICAL decision)
  2. require SEMANTICALLY_READY before the change
  3. apply the fixed future-agent change
  4. run the gate with memory, and the counterfactual gate without it
  5. run the resolved decision's regression contract and the full suite
  6. restore the exact prior bytes (always, in `finally`)
  7. re-run the gate; expect SEMANTICALLY_READY, 0 conflicts

Guard verdicts are derived from what the gate observed, never assumed:
  SEMANTICALLY_READY → MERGE_ALLOWED
  AGENT_DRIFT / VERIFICATION_FAILED → MERGE_BLOCKED
  DECISION_REQUIRED → DECISION_REQUIRED (merge held for a human decision)

The probes are fixed; nothing is taken from HTTP input except the probe id,
which must be a key of PROBES. None of this is the fresh-agent replay; no
independent agent is involved.
"""

import difflib
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from collider import gate as gate_mod
from collider.decision_compiler import (
    EXECUTION_ENVIRONMENTS,
    now_iso,
    tracked_files,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]

# The only future-agent changes the guard can apply. `find` must occur exactly
# once in `affected_file`; it is replaced by `replace`.
PROBES = {
    "IDENTITY_REVERT": {
        "title": "Future agent reverts API identity to email",
        "concept": "customer_identity",
        "canonical_value": "account_id",
        "attempted_value": "email",
        "affected_workstream": "api",
        "affected_file": "api/handlers/recover.py",
        "find": 'CUSTOMER_IDENTITY_FIELD = "account_id"',
        "replace": 'CUSTOMER_IDENTITY_FIELD = "email"',
        "expected_guard_verdict": "MERGE_BLOCKED",
        "receipt_name": "guard-probe.json",
    },
    "MONEY_UNIT_DRIFT": {
        "title": "Future agent switches Ledger to decimal dollars",
        "concept": "money_representation",
        "canonical_value": None,  # never decided: a shared INFERRED assumption
        "attempted_value": "decimal_dollars",
        "affected_workstream": "ledger",
        "affected_file": "ledger/credit_entry.py",
        "find": 'MONEY_UNIT = "integer_cents"',
        "replace": 'MONEY_UNIT = "decimal_dollars"',
        "expected_guard_verdict": "DECISION_REQUIRED",
        "receipt_name": "guard-probe-money-unit-drift.json",
    },
    "COMPATIBLE_CHANGE": {
        "title": "Future agent rewords the customer notice",
        "concept": None,  # touches no semantic concept
        "canonical_value": None,
        "attempted_value": None,
        "affected_workstream": "notifications",
        "affected_file": "notifications/send_credit_notice.py",
        "find": 'f"A credit of {display_amount} has been applied to your account."',
        "replace": 'f"We have credited {display_amount} to your account."',
        "expected_guard_verdict": "MERGE_ALLOWED",
        "receipt_name": "guard-probe-compatible-change.json",
    },
}
DEFAULT_PROBE = "IDENTITY_REVERT"

# Backward-compatible alias for the canonical demo attack.
PROBE = PROBES[DEFAULT_PROBE]
RECEIPT_NAME = PROBE["receipt_name"]

GUARD_VERDICTS = {
    "SEMANTICALLY_READY": "MERGE_ALLOWED",
    "AGENT_DRIFT": "MERGE_BLOCKED",
    "VERIFICATION_FAILED": "MERGE_BLOCKED",
    "DECISION_REQUIRED": "DECISION_REQUIRED",
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def strip(g: dict) -> dict:
    return {k: v for k, v in g.items() if k != "verification_output"}


def summarize_run(v: dict) -> dict:
    return {k: v[k] for k in (
        "command", "exit_code", "passed", "passed_count", "failed_count", "error_count",
    )}


def counterfactual_without_memory(workspace: Path) -> dict:
    """Judge the workspace's CURRENT workstream files with no decision memory.

    Copies only what the gate reads (workstream sources + spec) into a
    throwaway directory, removes the canon marker from the spec and omits
    canon/decision-memory.json. Nothing in `workspace` is written.
    """
    with tempfile.TemporaryDirectory(prefix="collider-cf-") as tmp:
        tmp = Path(tmp)
        for rel in [*gate_mod.WORKSTREAM_FILES.values(), gate_mod.BRIEF_RELPATH]:
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(workspace / rel, tmp / rel)
        brief = tmp / gate_mod.BRIEF_RELPATH
        brief.write_text(gate_mod.CANON_MARKER_RE.sub("", brief.read_text()))
        g = gate_mod.evaluate_gate(tmp)
    return {
        "verdict": g["verdict"],
        "guard_verdict": GUARD_VERDICTS[g["verdict"]],
        "finding_kinds": [f"{f['kind']}:{f['concept']}" for f in g["findings"]],
        "canon_resolved": g["canon_resolved"],
    }


def run_guard_probe(workspace: Path, out_dir: Path, source_root: Path = ROOT,
                    execution_environment: str = "LOCAL",
                    probe_id: str = DEFAULT_PROBE) -> dict:
    if execution_environment not in EXECUTION_ENVIRONMENTS:
        raise ValueError(f"execution_environment must be one of {EXECUTION_ENVIRONMENTS}")
    if probe_id not in PROBES:
        raise ValueError(f"REFUSE: probe must be one of {sorted(PROBES)}")
    probe = PROBES[probe_id]
    workspace = Path(workspace).resolve()
    out_dir = Path(out_dir).resolve()
    source_root = Path(source_root).resolve()
    receipt_path = out_dir / probe["receipt_name"]

    if receipt_path.exists():
        raise FileExistsError(f"REFUSE: guard probe already recorded: {receipt_path}")
    if workspace == source_root:
        raise ValueError("REFUSE: guard probe must run in a compiled workspace, not the source tree")

    # 1. Decision memory is the authority being guarded.
    memory_path = workspace / gate_mod.MEMORY_RELPATH
    if not memory_path.exists():
        raise RuntimeError("REFUSE: no decision memory in workspace; nothing to guard")
    memory = json.loads(memory_path.read_text())
    record = next(
        (d for d in memory.get("decisions", [])
         if d.get("concept") == "customer_identity"
         and d.get("decision_state") == "CANONICAL"),
        None,
    )
    if record is None:
        raise RuntimeError("REFUSE: no CANONICAL decision in memory; nothing to guard")
    if probe_id == "IDENTITY_REVERT" and record["canonical_value"] != probe["canonical_value"]:
        raise ValueError(
            "REFUSE: IDENTITY_REVERT guards customer_identity = account_id; "
            f"memory holds {record['canonical_value']!r}"
        )

    source_before = tracked_files(source_root)

    # 2. Only a verified tree can be guarded.
    gate_before = gate_mod.evaluate_gate(workspace)
    if gate_before["verdict"] != "SEMANTICALLY_READY":
        raise RuntimeError(
            f"REFUSE: workspace must be SEMANTICALLY_READY before probing; "
            f"it is {gate_before['verdict']}"
        )

    target = workspace / probe["affected_file"]
    original = target.read_bytes()
    sha_before = sha256_bytes(original)
    if original.decode().count(probe["find"]) != 1:
        raise RuntimeError(
            f"REFUSE: {probe['affected_file']} does not hold exactly one "
            f"{probe['find']!r}"
        )

    contract_rel = record["regression_artifact_ref"]
    restoration_applied = False
    try:
        # 3. Future-agent change.
        mutated = original.decode().replace(probe["find"], probe["replace"], 1)
        target.write_text(mutated)
        sha_during = sha256_bytes(target.read_bytes())
        probe_diff = "".join(difflib.unified_diff(
            original.decode().splitlines(keepends=True),
            mutated.splitlines(keepends=True),
            fromfile=f"a/{probe['affected_file']}",
            tofile=f"b/{probe['affected_file']} (future agent)",
        ))

        # 4. Gate with decision memory, and the same tree without it.
        gate_during = gate_mod.evaluate_gate(workspace)
        counterfactual = counterfactual_without_memory(workspace)

        # 5. Regression contract + full suite on the changed tree.
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

    guard_verdict = GUARD_VERDICTS[gate_during["verdict"]]
    violation = next(
        (f for f in gate_during["findings"]
         if probe["concept"] and f["concept"] == probe["concept"]),
        None,
    )
    surfaced_question = next(
        (f["question"] for f in gate_during["findings"] if f["kind"] == "SPEC_GAP"),
        None,
    )

    restoration_verified = (
        sha_after_restore == sha_before
        and gate_after["verdict"] == "SEMANTICALLY_READY"
        and gate_after["integration"]["conflict_count"] == 0
        and contract_after["passed"]
    )
    source_untouched = tracked_files(source_root) == source_before

    receipt = {
        "probe": "future-agent-change",
        "probe_id": probe_id,
        "title": probe["title"],
        "is_fresh_agent_replay": False,
        "decision_id": record["decision_id"],
        "concept": probe["concept"],
        "canonical_value": probe["canonical_value"],
        "attempted_value": probe["attempted_value"],
        "affected_workstream": probe["affected_workstream"],
        "affected_file": probe["affected_file"],
        "decision_memory_ref": gate_mod.MEMORY_RELPATH,
        "decision_memory_concept": record["concept"],
        "decision_memory_value": record["canonical_value"],
        "regression_contract": contract_rel,
        "sha_before_probe": sha_before,
        "sha_during_probe": sha_during,
        "probe_diff": probe_diff,
        "gate_before_probe": gate_before["verdict"],
        "gate_during_probe": gate_during["verdict"],
        "gate_during_findings": gate_during["findings"],
        "gate_during_assumptions": gate_during["assumptions"],
        "integration_during_probe": gate_during["integration"],
        "violation": violation,
        "surfaced_question": surfaced_question,
        "guard_verdict": guard_verdict,
        "expected_guard_verdict": probe["expected_guard_verdict"],
        "as_expected": guard_verdict == probe["expected_guard_verdict"],
        "counterfactual_without_memory": counterfactual,
        "memory_changed_verdict": counterfactual["verdict"] != gate_during["verdict"],
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
    parser.add_argument("--probe", choices=sorted(PROBES), default=DEFAULT_PROBE)
    args = parser.parse_args()
    r = run_guard_probe(Path(args.workspace), Path(args.out_dir), probe_id=args.probe)
    print(f"PROBE      {r['probe_id']}: {r['title']}")
    print(f"MEMORY     {r['decision_memory_concept']} = {r['decision_memory_value']}")
    print(f"GATE       with memory: {r['gate_during_probe']}   "
          f"without memory: {r['counterfactual_without_memory']['verdict']}")
    s = r["verification_during_probe"]["full_suite"]
    print(f"TESTS      during probe: {s['passed_count']} passed, {s['failed_count']} failed")
    print(f"GUARD      {r['guard_verdict']}  (expected {r['expected_guard_verdict']})")
    if r["surfaced_question"]:
        print(f"QUESTION   {r['surfaced_question']}")
    print(f"RESTORE    exact bytes={r['restored_exact_bytes']}  gate={r['gate_after_restore']}  "
          f"conflicts={r['integration_after_restore']['conflict_count']}")
    print(f"VERIFIED   {r['restoration_verified']}")
    sys.exit(0 if r["as_expected"] and r["restoration_verified"] else 1)
