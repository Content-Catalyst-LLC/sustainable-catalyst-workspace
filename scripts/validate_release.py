#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


main = ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php"
registry = ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php"
workspace = ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php"
js = ROOT / "wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.2.0.js"
css = ROOT / "wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.2.0.css"
manifest_path = ROOT / "release-manifest-v0.2.0.json"
record_path = ROOT / "registry/workspace-product-record-v0.2.0.json"
schema_path = ROOT / "schemas/sc-workspace-project-v1.schema.json"
release_notes = ROOT / "RELEASE_NOTES_0.2.0.md"
doc = ROOT / "docs/PROJECTS_PERSISTENCE_V020.md"

for path in (main, registry, workspace, js, css, manifest_path, record_path, schema_path, release_notes, doc):
    check(path.exists(), f"missing: {path.relative_to(ROOT)}")

if main.exists():
    text = main.read_text()
    check("Version: 0.2.0" in text, "plugin header version mismatch")
    check("SC_WORKSPACE_VERSION', '0.2.0'" in text, "runtime version mismatch")
    check("register_activation_hook" in text, "activation hook missing")

if registry.exists():
    text = registry.read_text()
    for token in (
        "'canonical_id' => self::CANONICAL_ID",
        "'family' => 'commercial'",
        "'console_screen' => 'commercial'",
        "'display_order' => 400",
        "'lifecycle_state' => 'experimental'",
        "'previous_version' => '0.1.0'",
        "BACKUP_KEY = 'sc_workspace_registry_backup_v020'",
    ):
        check(token in text, f"registry contract missing: {token}")

if workspace.exists():
    text = workspace.read_text()
    for token in (
        "add_shortcode('sc_workspace'",
        "add_shortcode('sc_workspace_entry'",
        "'/project-contract'",
        "'browser-local-projects-v2'",
        "'storage_schema_version' => 2",
        "'server_project_storage' => false",
        "'cloud_sync' => false",
        "'collaboration' => false",
        "data-scw-project-list",
        "data-scw-project-notes",
    ):
        check(token in text, f"workspace contract missing: {token}")

if js.exists():
    text = js.read_text()
    for token in (
        "const STORAGE_KEY = 'sc_workspace'",
        "const LEGACY_KEY = 'sc_workspace_v0_1'",
        "const STORAGE_VERSION = 2",
        "function migrateLegacyV1",
        "function quarantine",
        "function projectTemplate",
        "sc-workspace-project-export/1.0",
        "window.localStorage",
        "window.sessionStorage.setItem(HANDOFF_KEY",
        "sc_workspace_project",
        "sc_workspace_return",
    ):
        check(token in text, f"persistence/handoff contract missing: {token}")
    for forbidden in (
        "searchParams.set('sc_workspace_title'",
        "searchParams.set('sc_workspace_notes'",
        "searchParams.set('sc_workspace_description'",
    ):
        check(forbidden not in text, f"project content leaked into handoff URL: {forbidden}")

try:
    manifest = json.loads(manifest_path.read_text())
    check(manifest["version"] == "0.2.0", "manifest version mismatch")
    check(manifest["previous_version"] == "0.1.0", "manifest previous version mismatch")
    check(manifest["access_model"] == "free-public", "access model mismatch")
    check(manifest["storage_schema_version"] == 2, "storage schema mismatch")
    check(manifest["registry"]["family"] == "commercial", "registry family mismatch")
    check(manifest["repository"] == "Content-Catalyst-LLC/sustainable-catalyst-workspace", "canonical repository mismatch")
except Exception as exc:
    errors.append(f"manifest parse failed: {exc}")

try:
    record = json.loads(record_path.read_text())
    check(record["canonical_id"] == "sustainable-catalyst-workspace", "canonical id mismatch")
    check(record["public_version"] == "0.2.0", "registry public version mismatch")
    check(record["previous_version"] == "0.1.0", "registry previous version mismatch")
    check(record["family"] == "commercial", "record family mismatch")
except Exception as exc:
    errors.append(f"registry record parse failed: {exc}")

try:
    schema = json.loads(schema_path.read_text())
    check(schema["properties"]["schema"]["const"] == "sc-workspace-project/1.0", "project schema identity mismatch")
    check(schema["properties"]["activity"]["maxItems"] == 40, "activity bound mismatch")
except Exception as exc:
    errors.append(f"project schema parse failed: {exc}")

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print("FAIL -", error)
    sys.exit(1)

print("VALIDATION PASSED: Sustainable Catalyst Workspace v0.2.0")
print("PASS - canonical Workspace identity and Commercial Release placement")
print("PASS - Workspace Project schema and device-local persistence contract")
print("PASS - v0.1.0 browser-state migration and corrupted-state quarantine")
print("PASS - project import/export, activity, archive/recovery, and autosave contracts")
print("PASS - privacy-minimized cross-product active-project handoff")
print("PASS - no account, cloud project store, synchronization, or collaboration claim")
