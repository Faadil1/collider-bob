"""COLLIDER V2 dynamic semantic discovery primitives.

This module validates and groups concept *proposals* produced by discovery
agents. It intentionally does not classify truth, choose canonical values, or
turn consensus into authority.

Boundary:
- discovery agents may propose semantic surfaces;
- source evidence determines authority later;
- human decisions resolve missing authority;
- deterministic CI enforces ratified canon.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

GENERATION_MODES = {"LIVE_BOB", "PRESEEDED", "SIMULATED", "LOCAL", "LOCAL_STUB"}
EPISTEMIC_STATES = {"OBSERVED", "INFERRED", "UNKNOWN"}
SOURCE_RELATIONS = {"EXPLICIT", "SILENT", "INFERRED", "CONFLICTING"}
REQUIRED_FIELDS = {
    "proposal_id",
    "concept",
    "label",
    "workstream",
    "value",
    "epistemic_state",
    "source_relation",
    "source_refs",
    "artifact_refs",
    "generation_mode",
    "status",
}


class DiscoveryValidationError(ValueError):
    """Raised when a dynamic concept proposal violates a truth boundary."""


def validate_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    """Validate one discovery proposal and return it unchanged.

    Validation is deliberately structural and truth-boundary oriented. It does
    not judge whether the proposed concept is semantically correct.
    """
    missing = sorted(REQUIRED_FIELDS - proposal.keys())
    if missing:
        raise DiscoveryValidationError(f"missing required fields: {missing}")

    if "confidence" in proposal:
        raise DiscoveryValidationError(
            "confidence is forbidden; cite evidence or preserve UNKNOWN"
        )

    if proposal["status"] != "PROPOSED":
        raise DiscoveryValidationError(
            "discovery output must remain PROPOSED until ratified"
        )

    if proposal["generation_mode"] not in GENERATION_MODES:
        raise DiscoveryValidationError("unsupported generation_mode")

    if proposal["epistemic_state"] not in EPISTEMIC_STATES:
        raise DiscoveryValidationError("unsupported epistemic_state")

    if proposal["source_relation"] not in SOURCE_RELATIONS:
        raise DiscoveryValidationError("unsupported source_relation")

    concept = proposal["concept"]
    if (
        not isinstance(concept, str)
        or not concept
        or not concept[0].isalpha()
        or concept.lower() != concept
        or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789_" for ch in concept)
    ):
        raise DiscoveryValidationError(
            "concept must be a lowercase snake_case semantic key"
        )

    if not isinstance(proposal["source_refs"], list):
        raise DiscoveryValidationError("source_refs must be a list")

    if not isinstance(proposal["artifact_refs"], list) or not proposal["artifact_refs"]:
        raise DiscoveryValidationError("artifact_refs must be a non-empty list")

    if proposal["source_relation"] == "EXPLICIT" and not proposal["source_refs"]:
        raise DiscoveryValidationError(
            "EXPLICIT source_relation requires at least one source_ref"
        )

    if proposal["source_relation"] == "SILENT" and proposal["epistemic_state"] == "OBSERVED":
        raise DiscoveryValidationError(
            "source-silent proposals cannot claim OBSERVED authority"
        )

    if proposal["generation_mode"] == "LIVE_BOB":
        for field in ("session_ref", "task_summary_ref", "agent_id"):
            if not str(proposal.get(field, "")).strip():
                raise DiscoveryValidationError(
                    f"LIVE_BOB proposal requires {field}"
                )

    return proposal


def group_proposals(proposals: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Group validated proposals without upgrading them to facts.

    The result is a discovery snapshot suitable for deterministic normalization
    and Spec X-Ray rendering. The authority state is always UNRATIFIED here.
    """
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for proposal in proposals:
        valid = validate_proposal(proposal)
        grouped[valid["concept"]].append(valid)

    snapshot: dict[str, dict[str, Any]] = {}
    for concept, items in sorted(grouped.items()):
        values = {
            item["workstream"]: item["value"]
            for item in sorted(items, key=lambda x: x["workstream"])
        }
        relations = sorted({item["source_relation"] for item in items})
        snapshot[concept] = {
            "concept": concept,
            "labels": sorted({item["label"] for item in items}),
            "workstream_values": values,
            "source_relations": relations,
            "source_refs": sorted({
                ref for item in items for ref in item["source_refs"]
            }),
            "artifact_refs": sorted({
                ref for item in items for ref in item["artifact_refs"]
            }),
            "proposal_ids": sorted(item["proposal_id"] for item in items),
            "authority_state": "UNRATIFIED",
            "canonical_value": None,
        }

    return snapshot
