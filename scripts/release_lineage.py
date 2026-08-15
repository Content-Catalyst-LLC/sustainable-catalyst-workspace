from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import re

VERSION_RE = re.compile(r'^\d+\.\d+\.\d+$')

@dataclass(frozen=True)
class CurrentRelease:
    root: Path
    version: str
    previous_version: str
    manifest_path: Path
    registry_path: Path
    plugin_main: Path
    script_name: str
    style_name: str
    script_path: Path
    style_path: Path
    asset_handle: str

def version_token(version: str) -> str:
    return ''.join(version.split('.'))

def plugin_version(root: Path) -> str:
    main = root / 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
    text = main.read_text(errors='replace')
    header = re.search(r'(?mi)^[ \t/*#@]*Version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$', text)
    const = re.search(r"define\('SC_WORKSPACE_VERSION',\s*'([^']+)'\);", text)
    if not header or not const:
        raise ValueError('plugin version markers are missing')
    if header.group(1) != const.group(1):
        raise ValueError(f'plugin header/constant version mismatch: {header.group(1)} != {const.group(1)}')
    if not VERSION_RE.match(header.group(1)):
        raise ValueError('plugin version is not semantic x.y.z')
    return header.group(1)

def release_manifest_path(root: Path, version: str) -> Path:
    current = root / f'release-manifest-v{version}.json'
    if current.exists():
        return current
    historical = root / f'history/release-manifest-v{version}.json'
    if historical.exists():
        return historical
    raise FileNotFoundError(f'release manifest not found for v{version}')

def registry_record_path(root: Path, version: str) -> Path:
    current = root / f'registry/workspace-product-record-v{version}.json'
    if current.exists():
        return current
    historical = root / f'history/workspace-product-record-v{version}.json'
    if historical.exists():
        return historical
    raise FileNotFoundError(f'registry record not found for v{version}')

def load_manifest(root: Path, version: str) -> dict:
    return json.loads(release_manifest_path(root, version).read_text())

def load_registry(root: Path, version: str) -> dict:
    return json.loads(registry_record_path(root, version).read_text())

def current_release(root: Path) -> CurrentRelease:
    root = Path(root).resolve()
    version = plugin_version(root)
    manifest_path = root / f'release-manifest-v{version}.json'
    registry_path = root / f'registry/workspace-product-record-v{version}.json'
    if not manifest_path.exists():
        raise FileNotFoundError(f'current release manifest missing: {manifest_path.name}')
    if not registry_path.exists():
        raise FileNotFoundError(f'current registry record missing: {registry_path.name}')
    manifest = json.loads(manifest_path.read_text())
    previous = str(manifest.get('previous_version', ''))
    if not VERSION_RE.match(previous):
        raise ValueError('current manifest previous_version is invalid')
    plugin = root / 'wordpress/sustainable-catalyst-workspace'
    token = version_token(version)
    return CurrentRelease(
        root=root,
        version=version,
        previous_version=previous,
        manifest_path=manifest_path,
        registry_path=registry_path,
        plugin_main=plugin/'sustainable-catalyst-workspace.php',
        script_name=f'workspace-v{version}.js',
        style_name=f'workspace-v{version}.css',
        script_path=plugin/'assets/js'/f'workspace-v{version}.js',
        style_path=plugin/'assets/css'/f'workspace-v{version}.css',
        asset_handle=f'sc-workspace-v{token}',
    )

def validate_current_release_lineage(root: Path, expected_version: str | None = None, expected_previous: str | None = None) -> dict:
    cur = current_release(root)
    errors: list[str] = []
    if expected_version and cur.version != expected_version:
        errors.append(f'plugin version {cur.version} != expected {expected_version}')
    if expected_previous and cur.previous_version != expected_previous:
        errors.append(f'previous version {cur.previous_version} != expected {expected_previous}')
    manifest = json.loads(cur.manifest_path.read_text())
    registry = json.loads(cur.registry_path.read_text())
    main = cur.plugin_main.read_text(errors='replace')
    php = (cur.root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(errors='replace')
    deployment = (cur.root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text(errors='replace')
    production = (cur.root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-certification.php').read_text(errors='replace')
    if str(manifest.get('version')) != cur.version:
        errors.append('manifest version does not match plugin version')
    if str(manifest.get('previous_version')) != cur.previous_version:
        errors.append('manifest previous_version mismatch')
    if str(registry.get('public_version')) != cur.version:
        errors.append('registry public_version mismatch')
    if str(registry.get('installed_version')) != cur.version:
        errors.append('registry installed_version mismatch')
    if str(registry.get('previous_version')) != cur.previous_version:
        errors.append('registry previous_version mismatch')
    if not cur.script_path.is_file():
        errors.append(f'current cumulative script missing: {cur.script_name}')
    if not cur.style_path.is_file():
        errors.append(f'current cumulative style missing: {cur.style_name}')
    if cur.asset_handle not in php:
        errors.append(f'current asset handle missing from WordPress enqueue: {cur.asset_handle}')
    if cur.script_name not in php or cur.style_name not in php:
        errors.append('current cumulative assets missing from WordPress enqueue')
    if f"PREVIOUS_RELEASE = '{cur.previous_version}'" not in deployment:
        errors.append('deployment predecessor mismatch')
    if cur.script_name not in deployment or cur.style_name not in deployment:
        errors.append('deployment expected cumulative assets mismatch')
    if f"PREVIOUS_RELEASE = '{cur.previous_version}'" not in production:
        errors.append('production certification predecessor mismatch')
    if cur.script_name not in production or cur.style_name not in production:
        errors.append('production certification expected cumulative assets mismatch')
    raw = cur.plugin_main.read_bytes()
    head = raw[:8192].decode('utf-8', errors='replace')
    for label, expected in [
        ('Plugin Name','Sustainable Catalyst Workspace'),
        ('Version',cur.version),
        ('Author','Content Catalyst LLC'),
        ('Requires at least','6.4'),
        ('Requires PHP','8.0'),
    ]:
        m = re.search(r'^[ \t/*#@]*'+re.escape(label)+r':(.*)$', head, re.I|re.M)
        if not m or m.group(1).strip() != expected:
            errors.append(f'8KiB WordPress header mismatch: {label}')
    if raw.find(b'Version:') >= 512 or raw.find(b'Requires PHP:') >= 512:
        errors.append('WordPress metadata moved outside compact header guard')
    return {
        'ok': not errors,
        'version': cur.version,
        'previous_version': cur.previous_version,
        'manifest': cur.manifest_path.name,
        'registry': cur.registry_path.name,
        'script': cur.script_name,
        'style': cur.style_name,
        'asset_handle': cur.asset_handle,
        'errors': errors,
    }
