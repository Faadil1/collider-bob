"""
COLLIDER pull-request Semantic CI gate.

This is the CI surface of COLLIDER's three-verdict model. It evaluates only
semantic concepts that actually changed in the pull request, so pre-existing
fixture disagreements do not contaminate unrelated PRs.

Verdicts:
  MERGE_ALLOWED      changed semantics do not violate source/canon and do not
                     introduce a new source-silent disagreement.
  MERGE_BLOCKED      a changed semantic value violates explicit source or an
                     existing canonical decision.
  DECISION_REQUIRED  a changed semantic value introduces disagreement where
                     source authority is silent.

The gate uses committed decision memory as semantic authority. It never promotes
consensus into truth.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from collider.concepts import CONCEPTS, ORDER, values_for
from collider.gate import WORKSTREAM_FILES, observe_facts
from collider.pipeline import resolve_evidence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEMORY = "evidence/decisions/decision-001/decision-memory.json"
DEFAULT_BRIEF = "fixtures/failed-payment/BRIEF.md"


def _git_show(base_ref: str, relpath: str, *, cwd: Path) -> str:
    result = subprocess.run(
        ["git", "show", f"{base_ref}:{relpath}"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cannot read {relpath} at {base_ref}: {result.stderr.strip()}"
        )
    return result.stdout


def observe_base_facts(base_ref: str, *, root: Path = ROOT) -> dict[str, Any]:
    """Materialize only the three executable workstream files from base_ref."""
    root = Path(root)
    with tempfile.TemporaryDirectory(prefix="collider-pr-base-") as tmp:
        tmp_root = Path(tmp)
        for _, relpath in WORKSTREAM_FILES.items():
            target = tmp_root / relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_git_show(base_ref, relpath, cwd=root))
        return observe_facts(tmp_root)


def _canon_by_concept(memory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    canon = {}
    for record in memory.get("decisions", []):
        if record.get("decision_state") == "CANONICAL" and record.get("concept"):
            canon[record["concept"]] = record
    return canon


def evaluate_changed_semantics(
    *,
    base_facts: dict[str, Any],
    head_facts: dict[str, Any],
    decision_memory: dict[str, Any],
    brief_text: str,
) -> dict[str, Any]:
    canon = _canon_by_concept(decision_memory)
    findings: list[dict[str, Any]] = []
    changed_concepts: list[dict[str, Any]] = []

    for concept in ORDER:
        base_values = values_for(concept, base_facts)
        head_values = values_for(concept, head_facts)
        changed_workstreams = [
            ws for ws in head_values
            if base_values.get(ws) != head_values.get(ws)
        ]

        if not changed_workstreams:
            continue

        changed_concepts.append(
            {
                "concept": concept,
                "changed_workstreams": changed_workstreams,
                "before": base_values,
                "after": head_values,
            }
        )

        canonical = canon.get(concept)
        if canonical:
            canonical_value = canonical.get("canonical_value")
            violating = [
                ws for ws in changed_workstreams
                if head_values.get(ws) != canonical_value
            ]
            if violating:
                findings.append(
                    {
                        "kind": "AGENT_DRIFT",
                        "concept": concept,
                        "authority": "RESOLVED_CANON",
                        "canonical_value": canonical_value,
                        "changed_workstreams": changed_workstreams,
                        "violating_workstreams": violating,
                        "decision_id": canonical.get("decision_id"),
                    }
                )
            continue

        evidence = resolve_evidence(concept, brief_text)
        if evidence["found"]:
            authoritative = evidence["value"]
            violating = [
                ws for ws in changed_workstreams
                if head_values.get(ws) != authoritative
            ]
            if violating:
                findings.append(
                    {
                        "kind": "AGENT_DRIFT",
                        "concept": concept,
                        "authority": "EXPLICIT_SOURCE",
                        "canonical_value": authoritative,
                        "changed_workstreams": changed_workstreams,
                        "violating_workstreams": violating,
                        "source_ref": evidence.get("reference"),
                    }
                )
            continue

        normalized = {str(value).strip().lower() for value in head_values.values()}
        if len(normalized) > 1:
            findings.append(
                {
                    "kind": "SPEC_GAP",
                    "concept": concept,
                    "authority": "SOURCE_SILENT",
                    "epistemic_state": "UNKNOWN",
                    "changed_workstreams": changed_workstreams,
                    "values": head_values,
                    "question": CONCEPTS[concept].get("question"),
                }
            )

    if any(f["kind"] == "AGENT_DRIFT" for f in findings):
        verdict = "MERGE_BLOCKED"
    elif any(f["kind"] == "SPEC_GAP" for f in findings):
        verdict = "DECISION_REQUIRED"
    else:
        verdict = "MERGE_ALLOWED"

    return {
        "gate": "collider-pr-semantic-ci",
        "verdict": verdict,
        "passed": verdict == "MERGE_ALLOWED",
        "changed_concepts": changed_concepts,
        "findings": findings,
        "truth_boundary": {
            "only_changed_semantics_judged": True,
            "consensus_upgrades_to_fact": False,
            "decision_required_is_not_test_failure": True,
        },
    }


def evaluate_pr(
    *,
    base_ref: str,
    root: Path = ROOT,
    memory_path: str = DEFAULT_MEMORY,
    brief_path: str = DEFAULT_BRIEF,
) -> dict[str, Any]:
    root = Path(root)
    base_facts = observe_base_facts(base_ref, root=root)
    head_facts = observe_facts(root)
    decision_memory = json.loads((root / memory_path).read_text())
    brief_text = (root / brief_path).read_text()

    result = evaluate_changed_semantics(
        base_facts=base_facts,
        head_facts=head_facts,
        decision_memory=decision_memory,
        brief_text=brief_text,
    )
    result.update(
        {
            "base_ref": base_ref,
            "memory_path": memory_path,
            "brief_path": brief_path,
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="COLLIDER PR Semantic CI")
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--memory", default=DEFAULT_MEMORY)
    parser.add_argument("--brief", default=DEFAULT_BRIEF)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = evaluate_pr(
        base_ref=args.base_ref,
        root=Path(args.root),
        memory_path=args.memory,
        brief_path=args.brief,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"COLLIDER PR GATE  {result['verdict']}")
        for finding in result["findings"]:
            print(
                f"  - {finding['kind']:<12} {finding['concept']} "
                f"({finding['authority']})"
            )
        if not result["changed_concepts"]:
            print("  no registered semantic concept changed")

    if result["verdict"] == "MERGE_ALLOWED":
        return 0
    if result["verdict"] == "DECISION_REQUIRED":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
