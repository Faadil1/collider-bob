import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

baseline_dir = ROOT / "evidence/runs/baseline-001"
collider_dir = ROOT / "evidence/runs/local-resolved-004"
comparison = ROOT / "evidence/comparisons/baseline-001-vs-local-resolved-004.json"

baseline_manifest = json.loads((baseline_dir / "manifest.json").read_text())
baseline_probe = json.loads((baseline_dir / "integration-probe.json").read_text())
baseline_metrics = json.loads((baseline_dir / "metrics.json").read_text())

collider_manifest = json.loads((collider_dir / "manifest.json").read_text())
classifications = json.loads((collider_dir / "classifications.json").read_text())
integration = json.loads((collider_dir / "integration-after.json").read_text())
repairs = json.loads((collider_dir / "repairs.json").read_text())
artifact_hashes = json.loads((collider_dir / "artifact-hashes.json").read_text())

comparison_obj = json.loads(comparison.read_text())

B = {x["metric"]: x["value"] for x in baseline_metrics["metrics"]}
classes = {x["concept"]: x for x in classifications}

changed = [
    r for r in repairs
    if r["action"] == "repaired"
]

hashes = {
    a["workstream"]: {
        "before": a["sha256_before"],
        "after": a["sha256_after"],
        "restored": a["sha256_restored"],
        "changed": a["changed_during_repair"],
        "restored_to_input": a["restored_to_input"],
    }
    for a in artifact_hashes["artifacts"]
}

data = {
    "project": "COLLIDER",
    "fixture": "failed-payment",
    "truthBoundary": "LOCAL / PRESEEDED",
    "baseline": {
        "runId": baseline_manifest["run_id"],
        "commit": baseline_manifest["runtime_input_commit"],
        "testsPassed": B["local_workstream_tests_passed"],
        "suitesGreen": 3,
        "conflicts": baseline_probe["conflict_count"],
        "status": baseline_probe["status"],
        "conflictList": baseline_probe["conflicts"],
    },
    "classifications": {
        "customerIdentity": {
            "concept": "customer_identity",
            "classification": classes["customer_identity"]["classification"],
            "epistemicState": classes["customer_identity"]["epistemic_state"],
            "autoResolve": classes["customer_identity"]["auto_resolve"],
            "question": classes["customer_identity"]["minimal_question"],
            "values": classes["customer_identity"]["workstream_values"],
        },
        "fieldName": {
            "concept": "field_name",
            "classification": classes["field_name"]["classification"],
            "authoritativeValue": classes["field_name"]["authoritative_value"],
            "values": classes["field_name"]["workstream_values"],
            "source": classes["field_name"]["source_evidence"]["excerpt"],
        },
        "moneyRepresentation": {
            "concept": "money_representation",
            "classification": classes["money_representation"]["classification"],
            "subtype": classes["money_representation"]["classification_subtype"],
            "upgradesToFact": classes["money_representation"]["upgrades_to_fact"],
        },
    },
    "repairs": [
        {
            "concept": r["concept"],
            "workstream": r["workstream"],
            "before": r["prior_value"],
            "after": r["canonical_value"],
            "source": r["repair_source"],
        }
        for r in changed
    ],
    "result": {
        "runId": collider_manifest["run_id"],
        "commit": collider_manifest["runtime_input_commit"],
        "conflicts": integration["conflict_count"],
        "status": integration["status"],
        "facts": integration["facts"],
        "baselineRestored": artifact_hashes["baseline_restored"],
    },
    "hashes": hashes,
    "fairness": comparison_obj["fairness"],
    "evidenceCommit": "49d59a6c48aae5dce5ebad9f36909b5c71e77bb6",
}

# --- Decision receipt (DECIDE → COMPILE → PATCH → VERIFY → REMEMBER → GUARD) ---
# Shown in static mode, labelled as a committed receipt. The live local action
# server (demo-ui/server.py) returns the same shape from a real compile.
decision_dir = ROOT / "evidence/decisions/decision-001"


def dj(name):
    return json.loads((decision_dir / name).read_text())


decision_manifest = dj("manifest.json")
decision_memory = dj("decision-memory.json")["decisions"][0]

data["decisionReceipt"] = {
    "receipt_dir": "evidence/decisions/decision-001",
    "manifest": decision_manifest,
    "decision": dj("decision.json"),
    "memory": decision_memory,
    "spec_patch": dj("spec-patch.json"),
    "spec_diff": (decision_dir / "spec.diff").read_text(),
    "repair_patch": (decision_dir / "repair.patch").read_text(),
    "contract": (decision_dir / "test_canon_customer_identity.py").read_text(),
    "gate_before": dj("gate-before.json"),
    "gate_after": dj("gate-after.json"),
    "replay": dj("replay-contract.json"),
}

R = data["decisionReceipt"]
assert R["gate_before"]["verdict"] == "DECISION_REQUIRED"
assert R["gate_after"]["verdict"] == "SEMANTICALLY_READY"
assert decision_manifest["integration_conflicts_before"] == 2
assert decision_manifest["integration_conflicts_after"] == 0
assert decision_manifest["integration_status_after"] == "INTEGRATION_READY"
assert decision_manifest["source_tree_untouched"] is True
assert {w["workstream"]: w["changed"] for w in decision_manifest["workstreams"]} == {
    "api": True, "ledger": True, "notifications": False,
}
assert decision_memory["canonical_value"] == "account_id"
assert decision_memory["human_decision_source"] == "PRESEEDED"
assert decision_memory["evidence_state"] == "OBSERVED"
assert decision_memory["verification"]["tests_failed"] == 0
assert R["replay"]["status"] == "NOT_EXECUTED"
assert R["replay"]["runtime_state"] == "PENDING_LIVE_BOB"
assert R["replay"]["result"] is None

assert data["baseline"]["testsPassed"] == 30
assert data["baseline"]["conflicts"] == 2
assert data["classifications"]["customerIdentity"]["classification"] == "SPEC_GAP"
assert data["classifications"]["customerIdentity"]["epistemicState"] == "UNKNOWN"
assert data["classifications"]["fieldName"]["classification"] == "AGENT_DRIFT"
assert data["result"]["conflicts"] == 0
assert data["result"]["status"] == "INTEGRATION_READY"
assert len(data["repairs"]) == 2
assert data["fairness"]["starting_workstream_artifacts_byte_identical"] is True

out = Path(__file__).with_name("evidence.json")
out.write_text(json.dumps(data, indent=2))

print("✓ wrote", out)
print("✓ evidence-bound demo data verified")
