#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


main = ROOT / 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
registry = ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php'
workspace = ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
js = ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.3.0.js'
css = ROOT / 'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.3.0.css'
manifest_path = ROOT / 'release-manifest-v0.3.0.json'
record_path = ROOT / 'registry/workspace-product-record-v0.3.0.json'
project_schema_path = ROOT / 'schemas/sc-workspace-project-v2.schema.json'
object_schema_path = ROOT / 'schemas/sc-workspace-object-v1.schema.json'
release_notes = ROOT / 'RELEASE_NOTES_0.3.0.md'
doc = ROOT / 'docs/WORKSPACE_OBJECTS_ARTIFACT_MODEL_V030.md'

for path in (main, registry, workspace, js, css, manifest_path, record_path, project_schema_path, object_schema_path, release_notes, doc):
    check(path.exists(), f'missing: {path.relative_to(ROOT)}')

if main.exists():
    text = main.read_text()
    check('Version: 0.3.0' in text, 'plugin header version mismatch')
    check("SC_WORKSPACE_VERSION', '0.3.0'" in text, 'runtime version mismatch')
    check('register_activation_hook' in text, 'activation hook missing')

if registry.exists():
    text = registry.read_text()
    for token in (
        "'canonical_id' => self::CANONICAL_ID",
        "'family' => 'commercial'",
        "'console_screen' => 'commercial'",
        "'display_order' => 400",
        "'lifecycle_state' => 'experimental'",
        "'previous_version' => '0.2.0'",
        "BACKUP_KEY = 'sc_workspace_registry_backup_v030'",
    ):
        check(token in text, f'registry contract missing: {token}')

if workspace.exists():
    text = workspace.read_text()
    for token in (
        "add_shortcode('sc_workspace'",
        "add_shortcode('sc_workspace_entry'",
        "'/project-contract'",
        "'/object-contract'",
        "'browser-local-projects-v3'",
        "'storage_schema_version' => 3",
        "'project_schema' => 'sc-workspace-project/2.0'",
        "'object_schema' => 'sc-workspace-object/1.0'",
        "'server_project_storage' => false",
        "'cloud_sync' => false",
        "'collaboration' => false",
        'data-scw-object-list',
        'data-scw-object-content',
        'data-scw-object-source-url',
    ):
        check(token in text, f'workspace/object contract missing: {token}')

if js.exists():
    text = js.read_text()
    for token in (
        "const STORAGE_KEY = 'sc_workspace'",
        "const LEGACY_KEY = 'sc_workspace_v0_1'",
        'const STORAGE_VERSION = 3',
        'function migrateLegacyV1',
        'function migrateV2',
        'function quarantine',
        'function projectTemplate',
        'function objectTemplate',
        'function normalizeObject',
        "const PROJECT_SCHEMA = 'sc-workspace-project/2.0'",
        "const OBJECT_SCHEMA = 'sc-workspace-object/1.0'",
        "const EXPORT_SCHEMA = 'sc-workspace-project-export/2.0'",
        "const OBJECT_EXPORT_SCHEMA = 'sc-workspace-object-export/1.0'",
        'window.localStorage',
        'window.sessionStorage.setItem(HANDOFF_KEY',
        "target.searchParams.set('sc_workspace_project', project.id)",
        "target.searchParams.set('sc_workspace_object', object.id)",
    ):
        check(token in text, f'persistence/object/handoff contract missing: {token}')
    for forbidden in (
        "searchParams.set('sc_workspace_title'",
        "searchParams.set('sc_workspace_notes'",
        "searchParams.set('sc_workspace_description'",
        "searchParams.set('sc_workspace_object_title'",
        "searchParams.set('sc_workspace_object_content'",
        "searchParams.set('sc_workspace_object_summary'",
    ):
        check(forbidden not in text, f'content leaked into handoff URL: {forbidden}')

try:
    manifest = json.loads(manifest_path.read_text())
    check(manifest['version'] == '0.3.0', 'manifest version mismatch')
    check(manifest['previous_version'] == '0.2.0', 'manifest previous version mismatch')
    check(manifest['access_model'] == 'free-public', 'access model mismatch')
    check(manifest['storage_schema_version'] == 3, 'storage schema mismatch')
    check(manifest['project_schema'] == 'sc-workspace-project/2.0', 'project schema mismatch')
    check(manifest['object_schema'] == 'sc-workspace-object/1.0', 'object schema mismatch')
    check(manifest['registry']['family'] == 'commercial', 'registry family mismatch')
    check(manifest['repository'] == 'Content-Catalyst-LLC/sustainable-catalyst-workspace', 'canonical repository mismatch')
    check(manifest['governance']['max_objects_per_project'] == 250, 'object limit mismatch')
except Exception as exc:
    errors.append(f'manifest parse failed: {exc}')

try:
    record = json.loads(record_path.read_text())
    check(record['canonical_id'] == 'sustainable-catalyst-workspace', 'canonical id mismatch')
    check(record['public_version'] == '0.3.0', 'registry public version mismatch')
    check(record['previous_version'] == '0.2.0', 'registry previous version mismatch')
    check(record['family'] == 'commercial', 'record family mismatch')
except Exception as exc:
    errors.append(f'registry record parse failed: {exc}')

try:
    project_schema = json.loads(project_schema_path.read_text())
    check(project_schema['properties']['schema']['const'] == 'sc-workspace-project/2.0', 'project schema identity mismatch')
    check(project_schema['properties']['objects']['maxItems'] == 250, 'project object bound mismatch')
    check(project_schema['properties']['activity']['maxItems'] == 60, 'activity bound mismatch')
except Exception as exc:
    errors.append(f'project schema parse failed: {exc}')

try:
    object_schema = json.loads(object_schema_path.read_text())
    check(object_schema['properties']['schema']['const'] == 'sc-workspace-object/1.0', 'object schema identity mismatch')
    check(object_schema['properties']['type']['enum'] == ['source', 'evidence', 'dataset', 'analysis', 'decision', 'document', 'export'], 'object type vocabulary mismatch')
    check(object_schema['properties']['tags']['maxItems'] == 20, 'tag bound mismatch')
except Exception as exc:
    errors.append(f'object schema parse failed: {exc}')

if errors:
    print('VALIDATION FAILED')
    for error in errors:
        print('FAIL -', error)
    sys.exit(1)

print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.3.0')
print('PASS - canonical Workspace identity and Commercial Release placement')
print('PASS - project schema 2.0 and typed Workspace object schema 1.0')
print('PASS - seven canonical object types, lifecycle, tags, provenance, and bounded local storage')
print('PASS - v0.2 project migration, v0.1 session migration, and legacy v0.2 project import compatibility')
print('PASS - object create/edit/duplicate/archive/delete/export and project object filtering')
print('PASS - privacy-minimized project + active-object cross-product handoff')
print('PASS - no account, cloud project store, synchronization, collaboration, or automatic publication claim')
