from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "backend/app/visualization_specs.py",
    ROOT / "backend/migrations/028_declarative_visualization_specification_api.sql",
    ROOT / "backend/tests/test_visualization_specification_api_v2280.py",
    ROOT / "schemas/sc-workspace-visualization-spec-v1.schema.json",
    ROOT / "schemas/sc-workspace-visualization-spec-receipt-v1.schema.json",
    ROOT / "release-manifest-v2.28.0.json",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
assert not missing, missing
config = (ROOT / "backend/app/config.py").read_text()
assert 'service_version: str = "2.28.0"' in config
main = (ROOT / "backend/app/main.py").read_text()
for token in (
    "/v1/visualization-specs/profile",
    "/v1/visualization-specs",
    "declarativeVisualizationSpecificationApi",
    "rendererNeutralVisualizationSpecs",
    "browserDefinesAnalyticalMeaning",
):
    assert token in main, token
migration = (ROOT / "backend/migrations/028_declarative_visualization_specification_api.sql").read_text()
for table in ("workspace_visualization_specs", "workspace_visualization_spec_revisions", "workspace_visualization_spec_receipts"):
    assert table in migration, table
manifest = json.loads((ROOT / "release-manifest-v2.28.0.json").read_text())
assert manifest["version"] == "2.28.0"
assert manifest["rendererNeutral"] is True
print("PASS - v2.28.0 declarative visualization specification API contract")
