"""Deterministic inventory planning only: no I/O, target mutations or authorization issuance.

The caller must authenticate and authorize the inventory before invoking this module.
Recorded source relationships are observations, never proof of historical ownership.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import PurePosixPath
import re


SCHEMA = "sc.workspace.recovery-reconciliation-plan.v1"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise ValueError("Invalid inventory text")
    return value


def _sha(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[a-f0-9]{64}", value) is None:
        raise ValueError("Invalid inventory digest")
    return value


def _relative_path(value: object) -> str:
    value = _text(value)
    if PurePosixPath(value).is_absolute() or ".." in PurePosixPath(value).parts or "\\" in value or "\x00" in value or re.match(r"^[A-Za-z]:", value):
        raise ValueError("Invalid artifact relative path")
    return value


def _rows(inventory: dict, key: str) -> list[dict]:
    rows = inventory.get(key)
    if not isinstance(rows, list) or len(rows) > 100000 or not all(isinstance(r, dict) for r in rows):
        raise ValueError("Invalid inventory section")
    return rows


def _groups(rows: list[dict], key: str):
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(_text(row.get(key)), []).append(row)
    for identity in sorted(groups):
        candidates = sorted(groups[identity], key=_canonical)
        variants = sorted({_digest(r) for r in candidates})
        yield candidates[0], {"source_occurrences": len(candidates), "source_variant_sha256": variants,
                              "classifications": ["UNMATCHED", "BLOCKED"] + (["DUPLICATE"] if len(candidates) > 1 else []) + (["AMBIGUOUS"] if len(variants) > 1 else [])}


def plan(inventory: dict) -> dict:
    """Plan from the already-authorized catalog projection; do not read files or write state.

    A plan's stable digest excludes caller/expiry metadata and is NOT an execution grant.
    Artifact hash fields are preserved claims, not independently verified artifact bytes.
    """
    if not isinstance(inventory, dict):
        raise ValueError("Invalid inventory")
    catalog_digest = _sha(inventory.get("catalog_sha256"))
    projects, calculations, artifacts = {}, {}, []
    artifact_ids, artifact_sizes = {}, {}
    for row, classification in _groups(_rows(inventory, "projects"), "project_id"):
        project_id = _text(row.get("project_id"))
        name = _text(row.get("name"))
        projects[project_id] = {
            **classification,
            "source_system": "workbench", "original_project_id": project_id,
            "original_name": name, "original_owner_fingerprint": _text(row.get("owner_fingerprint")),
            "classification_hint": "development_or_certification_candidate" if re.search(r"\bgate\b", name, re.I) else "unclassified",
            "classification_basis": "title_only_needs_human_review",
            "historical_ownership": "UNRESOLVED", "target_action": "NONE",
            "target_object_id": None, "mapping_status": "BLOCKED",
            "blockers": ["historical_ownership_unresolved", "destination_project_authorization_not_verified"],
        }
    for row, classification in _groups(_rows(inventory, "calculations"), "record_id"):
        record_id, project_id = _text(row.get("record_id")), _text(row.get("project_id"))
        owner = _text(row.get("owner_fingerprint"))
        blockers = ["historical_ownership_unresolved", "scientific_results_not_reassessed"]
        if project_id not in projects:
            blockers.append("source_project_missing")
        elif owner != projects[project_id]["original_owner_fingerprint"]:
            blockers.append("source_owner_fingerprint_mismatch")
        calculations[record_id] = {
            **classification,
            "source_system": "workbench", "original_calculation_id": record_id,
            "original_project_id": project_id, "original_owner_fingerprint": owner,
            "project_relationship": "catalog_reference_only", "target_action": "NONE",
            "target_object_id": None, "mapping_status": "BLOCKED", "blockers": blockers,
        }
    for row in _rows(inventory, "artifacts"):
        size = row.get("size_bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ValueError("Invalid artifact size")
        artifact_id, digest = _text(row.get("artifact_id")), _sha(row.get("sha256"))
        if artifact_id in artifact_ids and artifact_ids[artifact_id] != digest:
            raise ValueError("Ambiguous artifact identity")
        if digest in artifact_sizes and artifact_sizes[digest] != size:
            raise ValueError("Conflicting artifact sizes")
        artifact_ids[artifact_id], artifact_sizes[digest] = digest, size
        artifacts.append({
            "original_artifact_id": artifact_id,
            "original_sha256": digest, "original_size_bytes": size,
            "original_relative_path": _relative_path(row.get("relative_path")),
            "original_collection": _text(row.get("collection")),
            "artifact_integrity": "NOT_CHECKED_BY_PLANNER", "project_mapping": "UNRESOLVED",
            "calculation_mapping": "UNRESOLVED", "target_action": "NONE",
            "target_object_id": None, "mapping_status": "BLOCKED",
            "blockers": ["artifact_relationships_not_verified", "historical_ownership_unresolved"],
        })
    # Sort before assigning occurrence indices so input order is not plan identity.
    artifacts.sort(key=_canonical)
    for index, row in enumerate(artifacts):
        row["occurrence_index"] = index
    artifact_counts = Counter(r["original_sha256"] for r in artifacts)
    for row in artifacts:
        row["classifications"] = ["UNMATCHED", "BLOCKED"] + (["DUPLICATE"] if artifact_counts[row["original_sha256"]] > 1 else [])
    result = {
        "schema": SCHEMA, "mode": "DRY_RUN", "catalog_sha256": catalog_digest,
        "projects": [projects[k] for k in sorted(projects)],
        "calculations": [calculations[k] for k in sorted(calculations)], "artifacts": artifacts,
        "summary": {"projects": len(projects), "calculations": len(calculations),
                    "artifact_occurrences": len(artifacts), "unique_artifacts": len(artifact_counts),
                    "repeated_hash_occurrences": sum(n - 1 for n in artifact_counts.values()),
                    "executable_operations": 0},
        "source_preservation": "REQUIRED", "staging": "NOT_PERFORMED",
        "workspace_registration": "NOT_PERFORMED", "ownership_reassignment": "NOT_PERFORMED",
        "publication": "DISABLED", "rollback": "NOT_APPLICABLE_NO_WRITES",
        "authorization": "INVENTORY_REVIEW_ONLY_NOT_EXECUTION_AUTHORITY",
    }
    result["plan_sha256"] = _digest(result)
    return deepcopy(result)
