from pathlib import Path
import json
import py_compile

root = Path(__file__).resolve().parents[1]
required = [
    "backend/app/domain_authority.py",
    "backend/migrations/024_backend_authority_domain_service.sql",
    "backend/tests/test_backend_domain_authority_v2240.py",
    "schemas/sc-workspace-domain-authority-v1.schema.json",
    "schemas/sc-workspace-domain-mutation-receipt-v1.schema.json",
    "release-manifest-v2.24.0.json",
    "registry/workspace-product-record-v2.24.0.json",
    "wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.24.0.js",
    "wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.24.0.css",
    "backend/deploy_workspace_backend_v2_24_0_vps.sh",
]
for rel in required:
    assert (root / rel).is_file(), rel

for rel in [
    "backend/app/domain_authority.py",
    "backend/app/repository.py",
    "backend/app/models.py",
    "backend/app/schemas.py",
    "backend/app/main.py",
    "backend/app/config.py",
]:
    py_compile.compile(str(root / rel), doraise=True)

for rel in [
    "schemas/sc-workspace-domain-authority-v1.schema.json",
    "schemas/sc-workspace-domain-mutation-receipt-v1.schema.json",
    "release-manifest-v2.24.0.json",
    "registry/workspace-product-record-v2.24.0.json",
]:
    json.load(open(root / rel))

main = (root / "backend/app/main.py").read_text()
repo = (root / "backend/app/repository.py").read_text()
deploy = (root / "backend/deploy_workspace_backend_v2_24_0_vps.sh").read_text()
wp = (root / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
plugin = (root / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()

for token in [
    '"backendDomainAuthority": True',
    '"backendAuthoritativeState": True',
    '"browserAuthoritativeState": False',
    '"domainMutationReceipts": True',
    '@app.get("/v1/domain-authority")',
    '@app.post("/v1/domain-authority/validate")',
    '@app.get("/v1/domain-mutation-receipts")',
]:
    assert token in main, token

assert "build_mutation_receipt" in repo
assert 'command="project.sync" if is_sync else "project.backup"' in repo
assert 'command="notebook.sync" if is_sync else "notebook.backup"' in repo
assert "migrations/024_backend_authority_domain_service.sql" in deploy
assert "d['version']=='2.24.0'" in deploy
assert "Workspace backend v2.24.0 API + authoritative domain state" in deploy
assert "workspace-v2.24.0.js" in wp and "workspace-v2.24.0.css" in wp
assert "Version: 2.24.0" in plugin and "SC_WORKSPACE_VERSION', '2.24.0" in plugin
print("PASS - v2.24.0 backend authority & domain service contract")
