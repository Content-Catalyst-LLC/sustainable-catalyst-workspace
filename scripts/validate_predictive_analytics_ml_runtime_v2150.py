#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
required=["backend/ml-runtime/Dockerfile","backend/ml-runtime/service.py","backend/migrations/015_predictive_analytics_machine_learning_runtime.sql","schemas/sc-workspace-predictive-analytics-runtime-v1.schema.json","tests/test_predictive_analytics_ml_runtime_v2150.py","registry/workspace-product-record-v2.15.0.json","release-manifest-v2.15.0.json","RELEASE_NOTES_2.15.0.md"]
missing=[x for x in required if not (ROOT/x).is_file()]
assert not missing, f"missing v2.15 files: {missing}"
assert 'service_version: str = "2.15.0"' in (ROOT/'backend/app/config.py').read_text()
assert 'Version: 2.15.0' in (ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
m=json.loads((ROOT/'release-manifest-v2.15.0.json').read_text()); assert m['previous_version']=='2.14.0'; assert m['ml_runtime']['operation_count']==8; assert m['ml_runtime']['arbitrary_code_execution'] is False
print('PASS — Workspace v2.15.0 Predictive Analytics & Machine Learning Runtime validated')
