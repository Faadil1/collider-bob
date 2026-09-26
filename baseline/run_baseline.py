"""
Deterministic LOCAL baseline for the failed-payment fixture.

This runner intentionally does NOT:
- import COLLIDER
- reconcile interpretation objects
- classify SPEC_GAP / AGENT_DRIFT
- read the fixture ground-truth oracle
- repair any implementation

It represents the control condition:
each workstream is locally green, then integration is attempted.
"""

import argparse
import datetime
import hashlib
import inspect
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

WORKSTREAM_TESTS = {
    "api": "api/tests/test_recover.py",
    "ledger": "ledger/tests/test_credit_entry.py",
    "notifications": "notifications/tests/test_send_credit_notice.py",
}

IMPLEMENTATION_FILES = {
    "api": "api/handlers/recover.py",
    "ledger": "ledger/credit_entry.py",
    "notifications": "notifications/send_credit_notice.py",
}


def now_iso():
    return (
        datetime.datetime.now(datetime.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def git_clean():
    out = subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    )
    return out.strip() == ""


def sha256_file(path):
    h = hashlib.sha256()
    with open(ROOT / path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2))


def run_local_suite(workstream, test_path):
    cmd = ["python3", "-m", "pytest", test_path, "-q"]
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    matches = re.findall(r"(\d+) passed", output)
    passed_count = int(matches[-1]) if matches else 0

    return {
        "workstream": workstream,
        "command": " ".join(cmd),
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
        "passed_count": passed_count,
        "output": output,
    }


def probe_integration():
    """
    Inspect the executable workstream interfaces directly.

    This is an integration compatibility probe, NOT a COLLIDER classifier.
    """
    from api.handlers import recover as api
    from ledger import credit_entry as ledger
    from notifications import send_credit_notice as notifications

    api_params = inspect.signature(api.process_recovery).parameters
    notif_params = inspect.signature(
        notifications.send_credit_notice
    ).parameters

    api_money_field = (
        "refund_amount"
        if "refund_amount" in api_params
        else None
    )

    notification_money_field = (
        "refund_amount"
        if "refund_amount" in notif_params
        else None
    )

    facts = {
        "api_customer_identity_field": api.CUSTOMER_IDENTITY_FIELD,
        "ledger_customer_identity_field": ledger.CUSTOMER_IDENTITY_FIELD,
        "api_money_field": api_money_field,
        "ledger_money_field": ledger.CREDIT_FIELD_NAME,
        "notifications_money_field": notification_money_field,
        "notifications_customer_identity_dependency": False,
    }

    conflicts = []

    if (
        facts["api_customer_identity_field"]
        != facts["ledger_customer_identity_field"]
    ):
        conflicts.append({
            "conflict_id": "customer-identity-interface-mismatch",
            "type": "INTERFACE_MISMATCH",
            "involved_workstreams": ["api", "ledger"],
            "api_value": facts["api_customer_identity_field"],
            "ledger_value": facts["ledger_customer_identity_field"],
            "detected_stage": "INTEGRATION",
            "classification": None,
            "notes": (
                "Baseline detects incompatible identity fields only when "
                "workstream interfaces are compared. No root-cause "
                "classification is attempted."
            ),
        })

    if facts["api_money_field"] != facts["ledger_money_field"]:
        conflicts.append({
            "conflict_id": "money-field-interface-mismatch",
            "type": "INTERFACE_MISMATCH",
            "involved_workstreams": ["api", "ledger"],
            "api_value": facts["api_money_field"],
            "ledger_value": facts["ledger_money_field"],
            "detected_stage": "INTEGRATION",
            "classification": None,
            "notes": (
                "Baseline observes incompatible field names at integration. "
                "It does not determine whether this is specification ambiguity "
                "or implementation drift."
            ),
        })

    return {
        "probe": "executable-interface-compatibility",
        "facts": facts,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "status": (
            "INTEGRATION_BLOCKED"
            if conflicts
            else "INTEGRATION_READY"
        ),
    }


def run(run_id, run_dir):
    run_dir = Path(run_dir)

    if run_dir.exists() and any(run_dir.iterdir()):
        raise FileExistsError(
            f"REFUSE: baseline evidence directory already exists "
            f"and is non-empty: {run_dir}"
        )

    input_commit = git_head()
    clean_start = git_clean()
    started = now_iso()

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "tests").mkdir(exist_ok=True)

    manifest = {
        "run_id": run_id,
        "run_type": "baseline",
        "execution_environment": "LOCAL",
        "generation_mode": "LOCAL",
        "implementation_source": "PRESEEDED_FIXTURE",
        "baseline_mode": "NO_COLLIDER_RECONCILIATION",
        "runtime_input_commit": input_commit,
        "working_tree_clean_at_start": clean_start,
        "timestamp": started,
        "known_limitations": [
            "Implementations are committed fixture artifacts, not live Bob outputs.",
            "No COLLIDER reconciliation, classifier, canon patch, or repair is used.",
            "Run stops at the observed integration compatibility result.",
            "Rework cycles and time-to-integration-ready are not measured because "
            "the baseline is intentionally not repaired in this evidence run.",
        ],
    }
    write_json(run_dir / "manifest.json", manifest)

    hashes = {
        ws: {
            "path": path,
            "sha256": sha256_file(path),
        }
        for ws, path in IMPLEMENTATION_FILES.items()
    }
    write_json(
        run_dir / "implementation-hashes.json",
        {
            "run_id": run_id,
            "runtime_input_commit": input_commit,
            "artifacts": hashes,
        },
    )

    suites = []
    for ws, test_path in WORKSTREAM_TESTS.items():
        result = run_local_suite(ws, test_path)
        suites.append(result)

        (run_dir / "tests" / f"{ws}.txt").write_text(
            result["output"]
        )

    local_green = all(s["passed"] for s in suites)
    local_passed_count = sum(s["passed_count"] for s in suites)

    integration = probe_integration()
    integration["run_id"] = run_id
    integration["timestamp"] = now_iso()
    write_json(run_dir / "integration-probe.json", integration)

    failures = []
    for conflict in integration["conflicts"]:
        failures.append({
            "failure_type": "integration_contract_mismatch",
            "workstreams": conflict["involved_workstreams"],
            "timestamp": now_iso(),
            "description": (
                f"{conflict['conflict_id']}: "
                f"{conflict['api_value']} != {conflict['ledger_value']}"
            ),
            "severity": "high",
            "resolution": "unresolved",
            "resolution_notes": (
                "Baseline records the mismatch and performs no COLLIDER repair."
            ),
        })

    write_json(
        run_dir / "failures.json",
        {
            "run_id": run_id,
            "failures": failures,
        },
    )

    metrics = {
        "run_id": run_id,
        "timestamp": now_iso(),
        "metrics": [
            {
                "metric": "local_workstream_test_suites_passed",
                "value": sum(1 for s in suites if s["passed"]),
                "unit": "count",
                "evidence_state": "OBSERVED",
            },
            {
                "metric": "local_workstream_tests_passed",
                "value": local_passed_count,
                "unit": "count",
                "evidence_state": "OBSERVED",
            },
            {
                "metric": "all_workstreams_locally_green",
                "value": local_green,
                "unit": "bool",
                "evidence_state": "OBSERVED",
            },
            {
                "metric": "contradictions_surfaced_pre_integration",
                "value": 0,
                "unit": "count",
                "evidence_state": "OBSERVED",
                "notes": "Baseline performs no pre-integration reconciliation.",
            },
            {
                "metric": "contradictions_surfaced_at_integration",
                "value": integration["conflict_count"],
                "unit": "count",
                "evidence_state": "OBSERVED",
            },
            {
                "metric": "integration_ready",
                "value": integration["status"] == "INTEGRATION_READY",
                "unit": "bool",
                "evidence_state": "OBSERVED",
            },
            {
                "metric": "rework_cycles",
                "value": None,
                "unit": "count",
                "evidence_state": "UNKNOWN",
                "notes": "Not measured: run stops at first integration probe.",
            },
            {
                "metric": "time_to_integration_ready_minutes",
                "value": None,
                "unit": "minutes",
                "evidence_state": "UNKNOWN",
                "notes": "Not measured because baseline remains integration-blocked.",
            },
        ],
    }
    write_json(run_dir / "metrics.json", metrics)

    print(f"BASELINE RUN: {run_id}")
    print(f"runtime_input_commit: {input_commit}")
    print(f"working_tree_clean_at_start: {clean_start}")
    print(
        f"local tests: {local_passed_count} passed across "
        f"{sum(1 for s in suites if s['passed'])}/3 suites"
    )
    print(f"integration status: {integration['status']}")
    print(f"integration conflicts: {integration['conflict_count']}")
    for conflict in integration["conflicts"]:
        print(
            f"  - {conflict['conflict_id']}: "
            f"{conflict['api_value']} != {conflict['ledger_value']}"
        )

    return {
        "manifest": manifest,
        "integration": integration,
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser(
        description="COLLIDER no-reconciliation baseline runner"
    )
    parser.add_argument("--run-id", default="baseline-001")
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    run(args.run_id, args.run_dir)


if __name__ == "__main__":
    main()
