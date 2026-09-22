#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

config = (BACKEND / "app/config.py").read_text()
main = (BACKEND / "app/main.py").read_text()
adapter = (BACKEND / "app/analytics_r_provider.py").read_text()
dockerfile = (BACKEND / "r-runtime/Dockerfile").read_text()
runner = (BACKEND / "r-runtime/provider_runner.R").read_text()
service = (BACKEND / "r-runtime/service.py").read_text()
compose = (BACKEND / "docker-compose.example.yml").read_text()
manifest = json.loads((ROOT / "release-manifest-v3.5.0.json").read_text())
wp = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
wp_class = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()

require('service_version: str = "3.5.0"' in config, "backend service version is not 3.5.0")
require('036_catalyst_analytics_r_runtime_adapter.sql' in main, "health migration lineage is not v3.5")
for flag in ["catalystAnalyticsRRuntimeAdapter", "catalystAnalyticsRProviderInstalled", "analyticalProviderReceipts"]:
    require(flag in main, f"missing health capability {flag}")
require('PROVIDER_VERSION = "2.1.0"' in adapter, "provider adapter version mismatch")
require('CORE_CONTRACT = "sc.core.analytical-runtime-provider.v1"' in adapter, "Core provider contract mismatch")
require('arbitraryFunctionDispatch' in adapter and 'arbitraryCodeExecution' in adapter, "adapter security boundary missing")
require('r-cran-ggplot2' in dockerfile and 'r-cran-rlang' in dockerfile, "R image dependencies missing")
require('R CMD INSTALL --preclean /opt/catalystanalyticsr' in dockerfile, "provider is not installed at image build time")
require('EXECUTABLE_METHODS <- c(' in runner and 'scenario_projection' not in runner, "provider whitelist/projection-only boundary invalid")
require('eval(parse(' not in runner, "arbitrary R parse/eval found")
require('/v1/providers/catalystanalyticsr/execute' in service, "R runtime provider execute endpoint missing")
r_section = compose.split('\n  sc-workspace-r-runtime:\n',1)[1].split('\n  sc-workspace-julia-runtime:\n',1)[0]
require('read_only: true' in r_section, "production R runtime is not read-only")
require(manifest.get('version') == '3.5.0' and manifest.get('typedEndpointCount') == 69, "release manifest mismatch")
require('Version: 3.5.0' in wp and "SC_WORKSPACE_VERSION', '3.5.0" in wp, "WordPress plugin version mismatch")
require('backend_typed_analytics_r_execute' in wp_class, "WordPress analytical provider proxy missing")
require((ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-catalyst-analytics-r-v3500.js').exists(), "WordPress analytical provider JS adapter missing")
require((BACKEND/'migrations/036_catalyst_analytics_r_runtime_adapter.sql').exists(), "migration 036 missing")
require((BACKEND/'r-runtime/vendor/catalystanalyticsr/DESCRIPTION').exists(), "vendored Catalyst Analytics R package missing")

if errors:
    for error in errors:
        print('ERROR:', error)
    raise SystemExit(1)
print('PASS: Workspace v3.5.0 Catalyst Analytics R Runtime Adapter release contract')
print('PASS: Catalyst Analytics R 2.1.0 is build-time installed; production R runtime remains read-only and bounded')
print('PASS: provider discovery/validation/execution + durable receipts + WordPress proxy + typed endpoints are present')
