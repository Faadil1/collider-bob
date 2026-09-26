"""
COLLIDER Decision Compiler — DECIDE → COMPILE → PATCH → VERIFY → REMEMBER → GUARD.

Turns one human decision on an unresolved SPEC_GAP into executable state:

  1. canon decision artifact     canon/decisions/<concept>.json
  2. source-spec patch           BRIEF.md "Adopted Decisions" section with a
                                 machine-readable marker, plus
                                 canon/spec-patches/<concept>.json (+ spec.diff)
  3. targeted code repair        only workstreams routed to `repair`
                                 (CANON_PATCH for the decision,
                                  AGENT_DRIFT_EVIDENCE for explicit-source drift)
  4. regression contract         contracts/test_canon_<concept>.py
  5. decision memory             canon/decision-memory.json
  6. gate verdict                collider.gate on the compiled tree
  7. replay contract             fresh-agent replay request, NOT_EXECUTED

Where the mutation happens
--------------------------
The committed repository tree is the canonical *pre-decision* input for
baseline-001 and local-resolved-004; mutating it would change what those
receipts reproduce against. The compiler therefore materializes a workspace
copy of the three workstreams and the fixture spec, and applies every mutation
there for real (files are rewritten, tests execute against them). The source
tree's workstream and spec hashes are checked before and after and must be
unchanged.

Truth boundary
--------------
execution LOCAL; interpretations PRESEEDED; the human decision source is
recorded exactly as supplied (PRESEEDED / CLI_OPERATOR / INTERACTIVE_LOCAL_UI);
fresh-agent replay NOT_EXECUTED / PENDING_LIVE_BOB.
"""

import contextlib
import datetime
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from collider import gate as gate_mod
from collider.pipeline import (
    apply_targeted_repair,
    classify_concept,
    reconcile,
    route_agent_drift,
    route_impact,
)
from collider.replay import build_replay_request, evaluate_replay_result

ROOT = Path(__file__).resolve().parents[1]

WORKSPACE_COPY = ["api", "ledger", "notifications", "fixtures/failed-payment"]
INTERPRETATIONS_RELDIR = "fixtures/failed-payment/interpretations"

HUMAN_DECISION_SOURCES = ("PRESEEDED", "CLI_OPERATOR", "INTERACTIVE_LOCAL_UI")

# Only concept compiled in this slice. Keys map the canonical value to the
# API keyword that carries it, so the contract exercises real behavior.
COMPILABLE_CONCEPTS = {
    "customer_identity": {
        "identity_kwargs": {
            "account_id": "customer_account_id",
            "email": "customer_email",
        },
        "samples": {"account_id": "acct_42", "email": "user@example.com"},
    },
}


def now_iso() -> str:
    return (
        datetime.datetime.now(datetime.UTC)
        .replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def git_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root,
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
    except Exception:
        return "UNKNOWN"


def git_worktree_clean(root: Path) -> bool | None:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=root,
            stderr=subprocess.DEVNULL, text=True,
        )
    except Exception:
        return None
    return out.strip() == ""


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


@contextlib.contextmanager
def working_directory(path: Path):
    prev = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)


def tracked_files(root: Path) -> dict:
    files = dict(gate_mod.WORKSTREAM_FILES)
    files["spec"] = gate_mod.BRIEF_RELPATH
    return {k: (Path(root) / rel).read_text() for k, rel in files.items()}


def unified(rel: str, before: str, after: str) -> str:
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile=f"a/{rel}", tofile=f"b/{rel}",
    ))


# ---------------------------------------------------------------------------
# Artifact builders
# ---------------------------------------------------------------------------

def spec_patch_section(decision: dict) -> str:
    dependents = ", ".join(decision["affected_dependents"])
    return (
        "\n---\n\n"
        "## Adopted Decisions (COLLIDER canon)\n\n"
        "Decisions below were made by a human after COLLIDER classified the "
        "concept as SPEC_GAP / UNKNOWN. They are authoritative source from the "
        "decision onward.\n\n"
        f"<!-- collider:canon {decision['concept']}={decision['canonical_value']} "
        f"decision={decision['decision_id']} -->\n"
        f"- **{decision['concept']}** = `{decision['canonical_value']}` — "
        f"binds: {dependents}. Prior state: SPEC_GAP / UNKNOWN. "
        f"Decision source: human ({decision['human_decision_source']}). "
        f"Decision id: `{decision['decision_id']}`.\n"
    )


def contract_source(decision: dict) -> str:
    spec = COMPILABLE_CONCEPTS[decision["concept"]]
    return f'''"""
COLLIDER regression contract — {decision["concept"]} = {decision["canonical_value"]}

Generated by collider.decision_compiler for decision {decision["decision_id"]}.
Do not edit by hand; recompile the decision instead. This protects the resolved
canon: any workstream that drifts back to a non-canonical identity fails here.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.handlers import recover as api  # noqa: E402
from ledger import credit_entry as ledger  # noqa: E402

CONCEPT = {decision["concept"]!r}
CANONICAL_VALUE = {decision["canonical_value"]!r}
DECISION_ID = {decision["decision_id"]!r}
IDENTITY_KWARGS = {spec["identity_kwargs"]!r}
SAMPLES = {spec["samples"]!r}


def recover(**identity):
    return api.process_recovery(
        charge_id="ch_contract",
        refund_amount=100,
        notification_contact="user@example.com",
        **identity,
    )


class TestCanonCustomerIdentity(unittest.TestCase):

    def test_decision_memory_records_canon(self):
        memory = json.loads((ROOT / "canon/decision-memory.json").read_text())
        record = next(d for d in memory["decisions"] if d["concept"] == CONCEPT)
        self.assertEqual(record["canonical_value"], CANONICAL_VALUE)
        self.assertEqual(record["decision_state"], "CANONICAL")
        self.assertEqual(record["decision_id"], DECISION_ID)

    def test_spec_carries_canon_marker(self):
        brief = (ROOT / "fixtures/failed-payment/BRIEF.md").read_text()
        self.assertIn(
            f"collider:canon {{CONCEPT}}={{CANONICAL_VALUE}} decision={{DECISION_ID}}",
            brief,
        )

    def test_api_identity_field_is_canonical(self):
        self.assertEqual(api.CUSTOMER_IDENTITY_FIELD, CANONICAL_VALUE)

    def test_ledger_identity_field_is_canonical(self):
        self.assertEqual(ledger.CUSTOMER_IDENTITY_FIELD, CANONICAL_VALUE)

    def test_api_resolves_customer_by_canonical_identity_alone(self):
        kw = IDENTITY_KWARGS[CANONICAL_VALUE]
        result = recover(**{{kw: SAMPLES[CANONICAL_VALUE]}})
        self.assertEqual(result["customer_field"], CANONICAL_VALUE)
        self.assertEqual(result["customer_value"], SAMPLES[CANONICAL_VALUE])

    def test_api_rejects_non_canonical_identity_alone(self):
        for other, kw in IDENTITY_KWARGS.items():
            if other == CANONICAL_VALUE:
                continue
            with self.assertRaises(ValueError):
                recover(**{{kw: SAMPLES[other]}})

    def test_api_identity_hands_off_to_ledger_key(self):
        result = recover(**{{kw: SAMPLES[v] for v, kw in IDENTITY_KWARGS.items()}})
        entry = ledger.post_credit_entry(result["customer_value"], result["refund_amount"])
        self.assertEqual(entry["customer_field"], result["customer_field"])
        self.assertEqual(entry["customer_value"], result["customer_value"])


if __name__ == "__main__":
    unittest.main()
'''


# ---------------------------------------------------------------------------
# Compiler
# ---------------------------------------------------------------------------

def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def annotate_repairs(workspace: Path, repair_records: list, decision_id: str) -> None:
    """Replace the stale local-choice comment on each repaired line with its provenance."""
    for r in repair_records:
        if r.get("action") != "repaired":
            continue
        tag = (
            f"CANON {r['concept']} — decision {decision_id} (canon/decision-memory.json)"
            if r["repair_source"] == "CANON_PATCH"
            else "SOURCE EXPLICIT — BRIEF.md API contract stub (AGENT_DRIFT repaired)"
        )
        path = workspace / r["file_modified"]
        pattern = rf'^({re.escape(r["constant_modified"])}\s*=\s*"[^"]*")[ \t]*#.*$'
        path.write_text(re.sub(pattern, rf"\1  # {tag}", path.read_text(), flags=re.MULTILINE))


def materialize_workspace(source_root: Path, workspace: Path) -> None:
    if workspace.exists() and any(workspace.iterdir()):
        raise FileExistsError(f"REFUSE: workspace already exists and is non-empty: {workspace}")
    for rel in WORKSPACE_COPY:
        shutil.copytree(
            source_root / rel, workspace / rel,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def compile_decision(
    concept: str,
    canonical_value: str,
    *,
    human_decision_source: str,
    decision_id: str,
    source_root: Path = ROOT,
    workspace: Path | None = None,
    out_dir: Path | None = None,
    rationale: str | None = None,
) -> dict:
    source_root = Path(source_root).resolve()
    workspace = Path(workspace or source_root / ".collider/workspaces" / decision_id).resolve()
    out_dir = Path(out_dir or source_root / ".collider/runs" / decision_id).resolve()

    if concept not in COMPILABLE_CONCEPTS:
        raise ValueError(f"concept {concept!r} is not compilable in this slice")
    if human_decision_source not in HUMAN_DECISION_SOURCES:
        raise ValueError(f"human_decision_source must be one of {HUMAN_DECISION_SOURCES}")
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"REFUSE: receipt directory already exists and is non-empty: {out_dir}")

    # --- DETECT ------------------------------------------------------------
    source_before = tracked_files(source_root)
    gate_before = gate_mod.evaluate_gate(source_root)
    gap = next(
        (f for f in gate_before["findings"]
         if f["kind"] == "SPEC_GAP" and f["concept"] == concept),
        None,
    )
    if gap is None:
        raise RuntimeError(
            f"REFUSE: no unresolved SPEC_GAP for {concept!r} in {source_root}; "
            f"gate verdict is {gate_before['verdict']}"
        )
    candidates = sorted(set(gap["candidates"].values()))
    if canonical_value not in candidates:
        raise ValueError(
            f"REFUSE: {canonical_value!r} is not an observed candidate for "
            f"{concept!r}; candidates: {candidates}"
        )

    # --- COMPILE: workspace + impact routing ---------------------------------
    materialize_workspace(source_root, workspace)
    ws_before = tracked_files(workspace)
    ws_hash_before = {k: sha256_text(v) for k, v in ws_before.items()}

    interp_dir = workspace / INTERPRETATIONS_RELDIR
    interpretations = [
        json.loads((interp_dir / f"{ws}.json").read_text())
        for ws in ("api", "ledger", "notifications")
    ]
    impact = route_impact(concept, canonical_value, interpretations)
    affected = sorted(
        w["workstream"] for w in impact["workstream_impacts"] if w["consumed_concept"]
    )
    unaffected = sorted(
        w["workstream"] for w in impact["workstream_impacts"] if not w["consumed_concept"]
    )

    compiled_at = now_iso()
    input_commit = git_head(source_root)
    clean_at_start = git_worktree_clean(source_root)
    decision = {
        "decision_id": decision_id,
        "concept": concept,
        "canonical_value": canonical_value,
        "decision_state": "CANONICAL",
        "decision_source": "human",
        "human_decision_source": human_decision_source,
        "decided_at": compiled_at,
        "question": gap["question"],
        "candidates": gap["candidates"],
        "prior_classification": "SPEC_GAP",
        "prior_epistemic_state": "UNKNOWN",
        "rationale": rationale,
        "affected_dependents": affected,
        "unaffected_workstreams": unaffected,
    }

    spec_rel = gate_mod.BRIEF_RELPATH
    decision_rel = f"canon/decisions/{concept}.json"
    spec_patch_rel = f"canon/spec-patches/{concept}.json"
    contract_rel = f"{gate_mod.CONTRACTS_RELDIR}/test_canon_{concept}.py"

    # --- PATCH: spec -------------------------------------------------------
    section = spec_patch_section(decision)
    brief_path = workspace / spec_rel
    brief_path.write_text(ws_before["spec"] + section)
    spec_patch = {
        "target": spec_rel,
        "op": "append_section",
        "section": "Adopted Decisions (COLLIDER canon)",
        "marker": f"collider:canon {concept}={canonical_value} decision={decision_id}",
        "content": section,
        "sha256_before": ws_hash_before["spec"],
        "sha256_after": sha256_text(brief_path.read_text()),
        "decision_ref": decision_rel,
    }
    write_json(workspace / decision_rel, decision)
    write_json(workspace / spec_patch_rel, spec_patch)

    # --- PATCH: code (targeted) ---------------------------------------------
    brief_text = brief_path.read_text()
    groups = reconcile(interpretations)
    repair_records = []
    impact_set = []
    with working_directory(workspace):
        for drift_concept, values in groups.items():
            cls = classify_concept(drift_concept, values, brief_text)
            if cls["classification"] != "AGENT_DRIFT":
                continue
            drift_impact = route_agent_drift(cls, interpretations)
            impact_set.append(drift_impact)
            repair_records += apply_targeted_repair(
                drift_concept, cls["authoritative_value"], drift_impact,
                repair_source="AGENT_DRIFT_EVIDENCE",
            )
        impact_set.append(impact)
        repair_records += apply_targeted_repair(
            concept, canonical_value, impact, repair_source="CANON_PATCH",
        )

    annotate_repairs(workspace, repair_records, decision_id)

    # --- REMEMBER (pre-verification record; gate reads it) --------------------
    (workspace / contract_rel).parent.mkdir(parents=True, exist_ok=True)
    (workspace / contract_rel).write_text(contract_source(decision))

    memory_record = {
        **{k: decision[k] for k in (
            "decision_id", "concept", "canonical_value", "decision_state",
            "decision_source", "human_decision_source", "decided_at",
            "prior_classification", "prior_epistemic_state",
        )},
        "affected_dependents": affected,
        "unaffected_workstreams": unaffected,
        "decision_ref": decision_rel,
        "spec_ref": spec_rel,
        "spec_patch_ref": spec_patch_rel,
        "regression_artifact_ref": contract_rel,
        "repairs": [
            {k: r.get(k) for k in (
                "workstream", "concept", "action", "file_modified",
                "prior_value", "canonical_value", "repair_source",
            )}
            for r in repair_records
        ],
        "provenance": {
            "execution_environment": "LOCAL",
            "interpretation_source": "PRESEEDED",
            "human_decision_source": human_decision_source,
            "compiler": "collider.decision_compiler",
            "input_commit": input_commit,
            "compiled_at": compiled_at,
        },
        "evidence_state": "PENDING_VERIFICATION",
    }
    memory_path = workspace / gate_mod.MEMORY_RELPATH
    write_json(memory_path, {"schema": "collider.decision-memory/v1",
                             "decisions": [memory_record]})

    ws_after = tracked_files(workspace)
    ws_hash_after = {k: sha256_text(v) for k, v in ws_after.items()}
    repair_patch = "".join(
        unified(rel, ws_before[k], ws_after[k])
        for k, rel in gate_mod.WORKSTREAM_FILES.items()
        if ws_before[k] != ws_after[k]
    )
    spec_diff = unified(spec_rel, ws_before["spec"], ws_after["spec"])

    # --- VERIFY + GUARD --------------------------------------------------------
    gate_after = gate_mod.evaluate_gate(workspace)
    verification = gate_after["verification"]

    # --- REPLAY (contract only) ------------------------------------------------
    replay_request = build_replay_request(memory_record, spec_rel, contract_rel)
    replay_state = evaluate_replay_result(replay_request, None, canonical_value)

    # --- REMEMBER (final) -----------------------------------------------------
    memory_record["evidence_state"] = (
        "OBSERVED" if gate_after["verdict"] == "SEMANTICALLY_READY" else "UNVERIFIED"
    )
    memory_record["verification"] = {
        "gate_verdict": gate_after["verdict"],
        "integration_conflicts_before": gate_before["integration"]["conflict_count"],
        "integration_conflicts_after": gate_after["integration"]["conflict_count"],
        "integration_status_after": gate_after["integration"]["status"],
        "tests_passed": verification["passed_count"] if verification else None,
        "tests_failed": verification["failed_count"] if verification else None,
        "command": verification["command"] if verification else None,
    }
    memory_record["replay"] = {
        "status": replay_state["status"],
        "runtime_state": replay_state["runtime_state"],
    }
    write_json(memory_path, {"schema": "collider.decision-memory/v1",
                             "decisions": [memory_record]})

    source_after = tracked_files(source_root)
    source_untouched = source_before == source_after

    workstreams = []
    for key, rel in gate_mod.WORKSTREAM_FILES.items():
        workstreams.append({
            "workstream": key,
            "path": rel,
            "sha256_before": ws_hash_before[key],
            "sha256_after": ws_hash_after[key],
            "changed": ws_hash_before[key] != ws_hash_after[key],
            "role": (
                "canon_dependent" if key in affected else "unaffected"
            ),
        })

    manifest = {
        "decision_id": decision_id,
        "action": "compile_decision",
        "command": (
            f"python3 -m collider.decision_compiler --concept {concept} "
            f"--value {canonical_value} --decision-id {decision_id} "
            f"--human-decision-source {human_decision_source}"
        ),
        "compiled_at": compiled_at,
        "input_commit": input_commit,
        "working_tree_clean_at_start": clean_at_start,
        "workspace": display_path(workspace, source_root),
        "loop": ["DETECT", "DECIDE", "COMPILE", "PATCH", "VERIFY", "REMEMBER", "GUARD"],
        "gate_before": gate_before["verdict"],
        "gate_after": gate_after["verdict"],
        "integration_conflicts_before": gate_before["integration"]["conflict_count"],
        "integration_conflicts_after": gate_after["integration"]["conflict_count"],
        "integration_status_after": gate_after["integration"]["status"],
        "workstreams": workstreams,
        "source_tree_untouched": source_untouched,
        "truth_boundary": {
            "execution": "LOCAL",
            "interpretations": "PRESEEDED",
            "human_decision": human_decision_source,
            "fresh_agent_replay": "NOT_EXECUTED / PENDING_LIVE_BOB",
            "live_bob": "NOT_EXECUTED",
            "wall_clock_improvement": "NOT_MEASURED",
            "percentage_improvement": "NOT_CLAIMED",
            "canonical_evidence_modified": False,
        },
    }

    # --- Receipts -------------------------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "manifest.json", manifest)
    write_json(out_dir / "decision.json", decision)
    write_json(out_dir / "spec-patch.json", spec_patch)
    (out_dir / "spec.diff").write_text(spec_diff)
    (out_dir / "repair.patch").write_text(repair_patch)
    write_json(out_dir / "impact-set.json", impact_set)
    write_json(out_dir / "repairs.json", repair_records)
    shutil.copy(workspace / contract_rel, out_dir / Path(contract_rel).name)
    shutil.copy(memory_path, out_dir / "decision-memory.json")
    strip = lambda g: {k: v for k, v in g.items() if k != "verification_output"}
    write_json(out_dir / "gate-before.json", strip(gate_before))
    write_json(out_dir / "gate-after.json", strip(gate_after))
    (out_dir / "verification.txt").write_text(
        f"command: {verification['command'] if verification else None}\n"
        f"cwd: <workspace>\n\n{gate_after['verification_output'] or ''}"
    )
    write_json(out_dir / "replay-contract.json", replay_request)

    return {
        "manifest": manifest,
        "decision": decision,
        "memory": memory_record,
        "spec_patch": spec_patch,
        "spec_diff": spec_diff,
        "repair_patch": repair_patch,
        "repairs": repair_records,
        "gate_before": strip(gate_before),
        "gate_after": strip(gate_after),
        "replay": replay_request,
        "contract": (workspace / contract_rel).read_text(),
        "out_dir": str(out_dir),
        "workspace": str(workspace),
    }


def record_abstention(
    concept: str,
    *,
    human_decision_source: str,
    action_id: str,
    source_root: Path = ROOT,
    out_dir: Path | None = None,
) -> dict:
    """
    KEEP UNKNOWN — the human declines to decide. Correct abstention.

    Writes NO canon, NO decision memory, NO spec patch, and repairs nothing.
    Only a bounded local action receipt (abstention.json) is recorded; it is
    not a canonical decision receipt. The gate must still say DECISION_REQUIRED.
    """
    source_root = Path(source_root).resolve()
    out_dir = Path(out_dir or source_root / ".collider/runs" / action_id).resolve()

    if concept not in COMPILABLE_CONCEPTS:
        raise ValueError(f"concept {concept!r} is not decidable in this slice")
    if human_decision_source not in HUMAN_DECISION_SOURCES:
        raise ValueError(f"human_decision_source must be one of {HUMAN_DECISION_SOURCES}")
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"REFUSE: receipt directory already exists and is non-empty: {out_dir}")

    before = tracked_files(source_root)
    gate = gate_mod.evaluate_gate(source_root)
    gap = next(
        (f for f in gate["findings"] if f["kind"] == "SPEC_GAP" and f["concept"] == concept),
        None,
    )
    if gap is None:
        raise RuntimeError(
            f"REFUSE: no unresolved SPEC_GAP for {concept!r}; gate verdict is {gate['verdict']}"
        )
    after = tracked_files(source_root)

    receipt = {
        "action_id": action_id,
        "action": "keep_unknown",
        "receipt_kind": "LOCAL_ACTION_RECEIPT (abstention; not a canonical decision receipt)",
        "concept": concept,
        "human_choice": "KEEP_UNKNOWN",
        "human_decision_source": human_decision_source,
        "canonical_value": None,
        "epistemic_state": "UNKNOWN",
        "candidates": gap["candidates"],
        "question": gap["question"],
        "canon_written": False,
        "decision_memory_written": False,
        "spec_patch_written": False,
        "repairs_applied": [],
        "message": "No canon written. No dependent work repaired.",
        "gate_verdict": gate["verdict"],
        "gate_findings": gate["findings"],
        "integration": gate["integration"],
        "source_sha256": {k: sha256_text(v) for k, v in before.items()},
        "source_tree_untouched": before == after,
        "recorded_at": now_iso(),
        "input_commit": git_head(source_root),
        "truth_boundary": {
            "execution": "LOCAL",
            "interpretations": "PRESEEDED",
            "human_decision": f"{human_decision_source} (abstained)",
        },
    }
    write_json(out_dir / "abstention.json", receipt)
    receipt["out_dir"] = str(out_dir)
    return receipt


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="COLLIDER decision compiler")
    parser.add_argument("--concept", default="customer_identity")
    parser.add_argument("--value", required=True)
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--human-decision-source", default="CLI_OPERATOR",
                        choices=HUMAN_DECISION_SOURCES)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--rationale", default=None)
    args = parser.parse_args()

    result = compile_decision(
        args.concept, args.value,
        human_decision_source=args.human_decision_source,
        decision_id=args.decision_id,
        out_dir=Path(args.out_dir) if args.out_dir else None,
        workspace=Path(args.workspace) if args.workspace else None,
        rationale=args.rationale,
    )
    m = result["manifest"]
    print(f"DECISION   {args.concept} = {args.value}  ({args.human_decision_source})")
    for w in m["workstreams"]:
        print(f"PATCH      {w['workstream']:<14} {'CHANGED' if w['changed'] else 'unchanged'}")
    v = result["memory"]["verification"]
    print(f"VERIFY     {v['tests_passed']} passed, {v['tests_failed']} failed")
    print(f"INTEGRATE  {m['integration_conflicts_before']} → {m['integration_conflicts_after']} "
          f"conflicts ({m['integration_status_after']})")
    print(f"GUARD      {m['gate_before']} → {m['gate_after']}")
    print(f"REPLAY     {result['memory']['replay']['status']} / {result['memory']['replay']['runtime_state']}")
    print(f"SOURCE     untouched={m['source_tree_untouched']}")
    print(f"RECEIPTS   {result['out_dir']}")
    sys.exit(0 if m["gate_after"] == "SEMANTICALLY_READY" and m["source_tree_untouched"] else 1)
