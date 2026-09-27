#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
wp = root / 'wordpress/sustainable-catalyst-workspace'
plugin = (wp / 'sustainable-catalyst-workspace.php').read_text()
klass = (wp / 'includes/class-sc-workspace.php').read_text()
deployment = (wp / 'includes/class-sc-workspace-deployment.php').read_text()

errors=[]
def require(condition, message):
    if not condition:
        errors.append(message)

require(' * Version: 3.20.0.1' in plugin, 'plugin header is not 3.20.0.1')
require("define('SC_WORKSPACE_VERSION', '3.20.0.1');" in plugin, 'SC_WORKSPACE_VERSION is not 3.20.0.1')

js = wp / 'assets/js/workspace-v3.20.0.1.js'
css = wp / 'assets/css/workspace-v3.20.0.1.css'
require(js.is_file() and js.stat().st_size > 0, 'v3.20.0.1 JS shell asset missing/empty')
require(css.is_file() and css.stat().st_size > 0, 'v3.20.0.1 CSS shell asset missing/empty')
require("assets/js/workspace-v3.20.0.1.js" in klass, 'enqueue does not reference v3.20.0.1 JS')
require("assets/css/workspace-v3.20.0.1.css" in klass, 'enqueue does not reference v3.20.0.1 CSS')
require("assets/js/workspace-v3.19.0.js" not in klass, 'stale v3.19.0 JS enqueue remains')
require("assets/css/workspace-v3.19.0.css" not in klass, 'stale v3.19.0 CSS enqueue remains')
require("'current_script' => 'assets/js/workspace-v' . SC_WORKSPACE_VERSION . '.js'" in deployment, 'deployment current_script contract changed unexpectedly')
require("'current_style' => 'assets/css/workspace-v' . SC_WORKSPACE_VERSION . '.css'" in deployment, 'deployment current_style contract changed unexpectedly')

# This patch intentionally aliases the stable shell bytes; a shell behavior change is out of scope.
old_js = wp / 'assets/js/workspace-v3.19.0.js'
old_css = wp / 'assets/css/workspace-v3.19.0.css'
if js.is_file() and old_js.is_file():
    require(hashlib.sha256(js.read_bytes()).digest() == hashlib.sha256(old_js.read_bytes()).digest(), 'v3.20.0.1 JS differs from stable v3.19 shell unexpectedly')
if css.is_file() and old_css.is_file():
    require(hashlib.sha256(css.read_bytes()).digest() == hashlib.sha256(old_css.read_bytes()).digest(), 'v3.20.0.1 CSS differs from stable v3.19 shell unexpectedly')

backend_config = (root / 'backend/app/config.py').read_text()
require('service_version: str = "3.20.0"' in backend_config, 'backend version should remain 3.20.0 for this package-only repair')
require((root / 'backend/neural-runtime/service.py').is_file(), 'v3.20.0 neural runtime is missing')

manifest_path = root / 'release-manifest-v3.20.0.1.json'
require(manifest_path.is_file(), 'v3.20.0.1 release manifest missing')
if manifest_path.is_file():
    manifest=json.loads(manifest_path.read_text())
    require(manifest.get('version') == '3.20.0.1', 'manifest version mismatch')
    require(manifest.get('backendVersion') == '3.20.0', 'manifest backend version mismatch')
    require(manifest.get('backendMutationRequired') is False, 'manifest must declare no backend mutation')

if errors:
    for e in errors:
        print('FAIL:', e)
    raise SystemExit(1)
print('PASS: Workspace v3.20.0.1 stable server package and asset coherence validation')
