"""
COLLIDER Semantic CI gate — GUARD.

Deterministic verdict over a repository root (the committed tree, or a
decision-compiled workspace):

  DECISION_REQUIRED    a cross-boundary SPEC_GAP has no canonical decision
  AGENT_DRIFT          an implementation violates explicit source or resolved canon
  SEMANTICALLY_READY   canon resolved, dependents conform, verification passes
  VERIFICATION_FAILED  structure conforms but behavioral / contract / integration
                       verification did not pass (never narrated as ready)

Precedence: DECISION_REQUIRED > AGENT_DRIFT > verification. A human decision is
the one blocker no repair can remove, so it is reported first; every finding is
still listed.

Canon is "resolved" for a concept only when BOTH exist in the root:
  - canon/decision-memory.json holds a CANONICAL record for it, and
  - the source spec (BRIEF.md) carries the matching machine-readable marker
    written by the decision compiler.
Agreement between agents without canon is never upgraded to resolved.

The gate reads workstream source by executing it in isolated namespaces, so it
never imports or caches transient module state.
"""

import inspect
import json
import re
import subprocess
import sys
from pathlib import Path

from collider.pipeline import classify_concept

ROOT = Path(__file__).resolve().parents[1]

BRIEF_RELPATH = "fixtures/failed-payment/BRIEF.md"
MEMORY_RELPATH = "canon/decision-memory.json"
CONTRACTS_RELDIR = "contracts"

WORKSTREAM_FILES = {
    "api": "api/handlers/recover.py",
    "ledger": "ledger/credit_entry.py",
    "notifications": "notifications/send_credit_notice.py",
}

WORKSTREAM_TESTS = [
    "api/tests/test_recover.py",
    "ledger/tests/test_credit_entry.py",
    "notifications/tests/test_send_credit_notice.py",
]

# Written into BRIEF.md by the decision compiler's spec patch.
CANON_MARKER_RE = re.compile(
    r"<!--\s*collider:canon\s+(?P<concept>[a-z_]+)=(?P<value>[A-Za-z0-9_]+)"
    r"\s+decision=(?P<decision>[A-Za-z0-9_.-]+)\s*-->"
)

VERDICTS = (
    "DECISION_REQUIRED",
    "AGENT_DRIFT",
    "SEMANTICALLY_READY",
    "VERIFICATION_FAILED",
)


# ---------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------

def load_namespaces(root: Path) -> dict:
    namespaces = {}
    for ws, rel in WORKSTREAM_FILES.items():
        path = Path(root) / rel
        ns = {"__name__": f"_collider_gate_{ws}", "__file__": str(path)}
        exec(compile(path.read_text(), str(path), "exec"), ns)
        namespaces[ws] = ns
    return namespaces


def observe_facts(root: Path) -> dict:
    ns = load_namespaces(root)
    api_params = inspect.signature(ns["api"]["process_recovery"]).parameters
    notif_params = inspect.signature(
        ns["notifications"]["send_credit_notice"]
    ).parameters
    return {
        "api_customer_identity_field": ns["api"]["CUSTOMER_IDENTITY_FIELD"],
        "ledger_customer_identity_field": ns["ledger"]["CUSTOMER_IDENTITY_FIELD"],
        "api_money_field": "refund_amount" if "refund_amount" in api_params else None,
        "ledger_money_field": ns["ledger"]["CREDIT_FIELD_NAME"],
        "notifications_money_field": (
            "refund_amount" if "refund_amount" in notif_params else None
        ),
    }


def probe_integration(facts: dict) -> dict:
    """Same conflict rules as the canonical baseline/pipeline probes."""
    conflicts = []
    if facts["api_customer_identity_field"] != facts["ledger_customer_identity_field"]:
        conflicts.append({
            "conflict_id": "customer-identity-interface-mismatch",
            "api_value": facts["api_customer_identity_field"],
            "ledger_value": facts["ledger_customer_identity_field"],
        })
    if facts["api_money_field"] != facts["ledger_money_field"]:
        conflicts.append({
            "conflict_id": "money-field-interface-mismatch",
            "api_value": facts["api_money_field"],
            "ledger_value": facts["ledger_money_field"],
        })
    return {
        "probe": "executable-interface-compatibility",
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "status": "INTEGRATION_READY" if not conflicts else "INTEGRATION_BLOCKED",
    }


def load_canon(root: Path) -> dict:
    """Return {concept: record} for concepts resolved in BOTH memory and spec."""
    root = Path(root)
    memory_path = root / MEMORY_RELPATH
    brief_path = root / BRIEF_RELPATH
    if not memory_path.exists():
        return {}
    memory = json.loads(memory_path.read_text())
    markers = {
        m.group("concept"): (m.group("value"), m.group("decision"))
        for m in CANON_MARKER_RE.finditer(brief_path.read_text())
    }
    canon = {}
    for record in memory.get("decisions", []):
        concept = record.get("concept")
        if record.get("decision_state") != "CANONICAL":
            continue
        marker = markers.get(concept)
        if marker and marker[0] == record.get("canonical_value"):
            canon[concept] = record
    return canon


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def _count(pattern: str, text: str) -> int:
    found = re.findall(pattern, text)
    return int(found[-1]) if found else 0


def run_pytest(root: Path, targets: list) -> dict:
    """Run pytest on `targets` (paths relative to `root`) with cwd=root."""
    root = Path(root)
    cmd = [
        sys.executable, "-B", "-m", "pytest", *targets, "-q",
        "-p", "no:cacheprovider", "--rootdir=.",
    ]
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    output = result.stdout + result.stderr
    return {
        "command": " ".join(["python3", *cmd[1:]]),
        "cwd": str(root),
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
        "passed_count": _count(r"(\d+) passed", output),
        "failed_count": _count(r"(\d+) failed", output),
        "error_count": _count(r"(\d+) errors?", output),
        "output": output,
    }


def contract_files_in(root: Path) -> list:
    contracts_dir = Path(root) / CONTRACTS_RELDIR
    if not contracts_dir.exists():
        return []
    return sorted(str(p.relative_to(root)) for p in contracts_dir.glob("test_*.py"))


def run_verification(root: Path) -> dict:
    """Run workstream behavioral tests + regression contracts inside `root`."""
    contract_files = contract_files_in(root)
    result = run_pytest(root, list(WORKSTREAM_TESTS) + contract_files)
    result["contract_files"] = contract_files
    return result


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------

def evaluate_gate(root: Path = ROOT) -> dict:
    root = Path(root)
    facts = observe_facts(root)
    brief_text = (root / BRIEF_RELPATH).read_text()
    canon = load_canon(root)
    integration = probe_integration(facts)
    findings = []

    def ws_values(pairs):
        return {
            ws: {"value": v, "epistemic_state": "UNKNOWN"} for ws, v in pairs.items()
        }

    # Explicit-source concept: the money field name (BRIEF API contract stub).
    money = classify_concept(
        "field_name",
        ws_values({
            "api": facts["api_money_field"],
            "ledger": facts["ledger_money_field"],
            "notifications": facts["notifications_money_field"],
        }),
        brief_text,
    )
    if money["classification"] == "AGENT_DRIFT":
        findings.append({
            "kind": "AGENT_DRIFT",
            "concept": "field_name",
            "authority": "EXPLICIT_SOURCE",
            "expected": money["authoritative_value"],
            "violations": {
                ws: money["workstream_values"][ws]
                for ws in money["agent_drift_workstreams"]
            },
            "source_evidence": money["source_evidence"]["excerpt"],
        })

    # Cross-boundary concept: customer identity (source silent until canon).
    identity_values = {
        "api": facts["api_customer_identity_field"],
        "ledger": facts["ledger_customer_identity_field"],
    }
    record = canon.get("customer_identity")
    if record:
        expected = record["canonical_value"]
        dependents = record.get("affected_dependents", sorted(identity_values))
        violations = {
            ws: identity_values[ws]
            for ws in dependents
            if ws in identity_values and identity_values[ws] != expected
        }
        if violations:
            findings.append({
                "kind": "AGENT_DRIFT",
                "concept": "customer_identity",
                "authority": "RESOLVED_CANON",
                "expected": expected,
                "violations": violations,
                "decision_id": record.get("decision_id"),
            })
    else:
        identity = classify_concept(
            "customer_identity", ws_values(identity_values), brief_text
        )
        if identity["classification"] == "SPEC_GAP":
            findings.append({
                "kind": "SPEC_GAP",
                "concept": "customer_identity",
                "authority": "NONE",
                "epistemic_state": "UNKNOWN",
                "candidates": identity["workstream_values"],
                "question": identity["minimal_question"],
            })
        elif identity["classification"] == "NO_DISAGREEMENT":
            findings.append({
                "kind": "SHARED_INFERRED",
                "concept": "customer_identity",
                "authority": "NONE",
                "note": "Agents agree without canon; agreement is not fact.",
            })

    verification = None
    if any(f["kind"] == "SPEC_GAP" for f in findings):
        verdict = "DECISION_REQUIRED"
    elif any(f["kind"] == "AGENT_DRIFT" for f in findings):
        verdict = "AGENT_DRIFT"
    elif "customer_identity" not in canon:
        # Shared inference without canon: not a gap, but not resolved either.
        verdict = "DECISION_REQUIRED"
    else:
        verification = run_verification(root)
        ready = (
            verification["passed"]
            and verification["contract_files"]
            and integration["status"] == "INTEGRATION_READY"
        )
        verdict = "SEMANTICALLY_READY" if ready else "VERIFICATION_FAILED"

    return {
        "gate": "collider-semantic-ci",
        "verdict": verdict,
        "passed": verdict == "SEMANTICALLY_READY",
        "findings": findings,
        "facts": facts,
        "integration": integration,
        "canon_resolved": sorted(canon),
        "verification": (
            {k: v for k, v in verification.items() if k != "output"}
            if verification else None
        ),
        "verification_output": verification.get("output") if verification else None,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="COLLIDER Semantic CI gate")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = evaluate_gate(Path(args.root))
    if args.json:
        print(json.dumps(
            {k: v for k, v in result.items() if k != "verification_output"},
            indent=2,
        ))
    else:
        print(f"COLLIDER GATE  {result['verdict']}")
        for f in result["findings"]:
            print(f"  - {f['kind']:<16} {f['concept']}")
        print(
            f"  integration: {result['integration']['conflict_count']} conflicts "
            f"({result['integration']['status']})"
        )
        v = result["verification"]
        if v:
            print(f"  verification: {v['passed_count']} passed, {v['failed_count']} failed")
    sys.exit(0 if result["passed"] else 1)
