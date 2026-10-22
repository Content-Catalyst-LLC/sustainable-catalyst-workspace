"""Synthetic inventory and signed-session tests; never read production research."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.recovery_reconciliation import plan
from app import session_auth, wxr_recovery_review as review


@pytest.fixture
def inventory():
    return {"catalog_sha256": "a" * 64,
            "projects": [{"project_id": "source-p", "name": "Synthetic soil study", "owner_fingerprint": "b" * 16},
                         {"project_id": "source-gate", "name": "Synthetic deployment gate", "owner_fingerprint": "c" * 16}],
            "calculations": [{"record_id": "source-c", "project_id": "source-p", "owner_fingerprint": "b" * 16}],
            "artifacts": [{"artifact_id": "sha256:" + "d" * 64, "sha256": "d" * 64, "relative_path": "figures/a.svg", "collection": "svg", "size_bytes": 12},
                          {"artifact_id": "sha256:" + "d" * 64, "sha256": "d" * 64, "relative_path": "figures/b.svg", "collection": "svg", "size_bytes": 12}]}


def test_preserves_ids_owners_duplicates_and_blocks_every_target(inventory):
    before = deepcopy(inventory)
    result = plan(inventory)
    assert inventory == before
    assert result["summary"] == {"projects": 2, "calculations": 1, "artifact_occurrences": 2, "unique_artifacts": 1, "repeated_hash_occurrences": 1, "executable_operations": 0}
    assert {p["original_project_id"] for p in result["projects"]} == {"source-p", "source-gate"}
    assert result["calculations"][0]["original_calculation_id"] == "source-c"
    for section in ("projects", "calculations", "artifacts"):
        assert all(r["target_action"] == "NONE" and r["target_object_id"] is None and r["mapping_status"] == "BLOCKED" for r in result[section])
    assert result["staging"] == "NOT_PERFORMED"
    assert result["publication"] == "DISABLED"
    assert result["rollback"] == "NOT_APPLICABLE_NO_WRITES"
    assert all(a["artifact_integrity"] == "NOT_CHECKED_BY_PLANNER" for a in result["artifacts"])
    gate = next(r for r in result["projects"] if r["original_project_id"] == "source-gate")
    assert gate["classification_hint"] == "development_or_certification_candidate"


def test_stable_digest_under_reordering_and_repeat(inventory):
    first = plan(inventory)
    for key in ("projects", "calculations", "artifacts"):
        inventory[key].reverse()
    assert plan(inventory) == first
    assert plan(deepcopy(inventory))["plan_sha256"] == first["plan_sha256"]


@pytest.mark.parametrize("section,field,value", [("projects", "owner_fingerprint", "e" * 16), ("projects", "name", "Changed synthetic study"), ("calculations", "project_id", "missing-project"), ("artifacts", "relative_path", "figures/changed.svg")])
def test_material_changes_change_plan_digest(inventory, section, field, value):
    before = plan(inventory)["plan_sha256"]
    inventory[section][0][field] = value
    assert plan(inventory)["plan_sha256"] != before


def test_unresolved_and_cross_owner_references_are_preserved_as_blocked(inventory):
    inventory["calculations"][0]["owner_fingerprint"] = "f" * 16
    assert "source_owner_fingerprint_mismatch" in plan(inventory)["calculations"][0]["blockers"]
    inventory["calculations"][0]["project_id"] = "orphan-original"
    row = plan(inventory)["calculations"][0]
    assert row["original_project_id"] == "orphan-original" and "source_project_missing" in row["blockers"]


@pytest.mark.parametrize("section", ["projects", "calculations"])
def test_duplicate_identity_is_explicit_and_never_executable(inventory, section):
    inventory[section].append(deepcopy(inventory[section][0]))
    result = plan(inventory)
    rows = result[section]
    assert any("DUPLICATE" in row["classifications"] for row in rows)
    assert all(row["target_action"] == "NONE" for row in rows)
    inventory[section][-1]["owner_fingerprint"] = "f" * 16
    assert any("AMBIGUOUS" in row["classifications"] for row in plan(inventory)[section])


@pytest.mark.parametrize("bad", [None, {}, "not-a-list", [None]])
def test_malformed_section_rejected(inventory, bad):
    inventory["projects"] = bad
    with pytest.raises(ValueError):
        plan(inventory)


@pytest.mark.parametrize("bad", ["../private", "/private/path", "C:/private/path", "path\\escape", "bad\x00path"])
def test_unsafe_relative_paths_rejected(inventory, bad):
    inventory["artifacts"][0]["relative_path"] = bad
    with pytest.raises(ValueError):
        plan(inventory)


def test_private_source_fields_and_untrusted_approvals_do_not_enter_plan(inventory):
    inventory["approved"] = True
    inventory["projects"][0].update(owner_verified=True, owner_subject="private-original-owner")
    inventory["artifacts"][0]["original_source_path"] = "/private/original"
    raw = json.dumps(plan(inventory))
    assert "/private/original" not in raw and "private-original-owner" not in raw and "owner_verified" not in raw
    assert plan(inventory)["summary"]["executable_operations"] == 0


def test_second_study_uses_same_planner(inventory):
    inventory["projects"][0]["name"] = "Synthetic wetland nutrient study"
    result = plan(inventory)
    assert result["projects"][1]["original_name"] == "Synthetic wetland nutrient study"
    assert "wexford" not in json.dumps(result).lower()


def test_invalid_digest_and_conflicting_artifact_identity_rejected(inventory):
    invalid = deepcopy(inventory)
    invalid["catalog_sha256"] = "unverified"
    with pytest.raises(ValueError):
        plan(invalid)
    inventory["artifacts"][1]["sha256"] = "f" * 64
    with pytest.raises(ValueError):
        plan(inventory)


def test_conflicting_size_for_same_hash_rejected(inventory):
    inventory["artifacts"][1]["size_bytes"] = 13
    with pytest.raises(ValueError):
        plan(inventory)


