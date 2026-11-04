#!/usr/bin/env bash
# RD-01.4-PB04: audit installed Contabo source and route definitions, with zero writes.
# Run ON Contabo as a user allowed to inspect Docker, not on the Mac.
set -euo pipefail
echo PB04_CONTABO_SOURCE_GATE=START
for cname in sc-workspace-reporting-live sc-rd013-staging-app; do
    echo "PB04_CONTAINER=$cname"
    docker inspect --format='PB04_CONTAINER_STATUS={{.State.Status}} PB04_CONTAINER_IMAGE_ID={{.Image}}' "$cname"
    docker exec -i "$cname" python - <<'PY'
import ast
import hashlib
import sys
from pathlib import Path

root = next((Path(s or ".").resolve() / "app" for s in sys.path
             if (Path(s or ".").resolve() / "app" / "main.py").is_file()), None)
if root is None:
    print("PB04_APP_SOURCE_ROOT=NOT_FOUND")
    raise SystemExit(2)
print("PB04_APP_SOURCE_ROOT=" + str(root))
modules = (
    "main.py", "wxr_private_projects.py", "rd014_publication_records.py",
    "reporting_production_entry.py", "reporting_research_objects.py",
    "reporting_provider_contracts.py", "research_reporting_ui.js",
    "repository.py", "object_store.py", "session_auth.py",
    "schemas.py", "models.py",
)
for mod in modules:
    path = root / mod
    if not path.is_file():
        print("PB04_MODULE=" + mod + " STATUS=ABSENT")
        continue
    data = path.read_bytes()
    print("PB04_MODULE=" + mod + " STATUS=PRESENT SHA256=" + hashlib.sha256(data).hexdigest())
    if mod == "main.py":
        # Static analysis avoids importing/starting the production app.
        tree = ast.parse(data, filename=str(path))
        includes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "include_router":
                if node.args and isinstance(node.args[0], ast.Name):
                    includes.append(node.args[0].id)
        for token in ("wxr_private_projects", "rd014_publication_records", "reporting_production_entry"):
            print("PB04_MAIN_ROUTER_" + token.upper() + "=" + ("YES" if any(token in x for x in includes) else "NOT_DETECTED"))
        print("PB04_MAIN_ROUTER_REGISTRATIONS=" + str(len(includes)))
    elif mod in ("wxr_private_projects.py", "rd014_publication_records.py"):
        tree = ast.parse(data, filename=str(path))
        prefix = ""
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "router" for t in node.targets):
                if isinstance(node.value, ast.Call):
                    for kw in node.value.keywords:
                        if kw.arg == "prefix" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                            prefix = kw.value.value
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        if isinstance(dec.func.value, ast.Name) and dec.func.value.id == "router" and dec.func.attr in ("get", "post", "put", "delete", "patch"):
                            suffix = dec.args[0].value if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str) else "<dynamic>"
                            print("PB04_SOURCE_ROUTE=" + dec.func.attr.upper() + " " + prefix + suffix)
print("PB04_CONTAINER_INSPECTION=COMPLETE")
PY
done
# Anonymous GETs test proxy reachability, not owner authentication; no cookies sent.
for path in /health /v1/private-research/persistent-projects/ui /v1/private-research/reporting-studio/publication; do
    code=$(curl -sS --connect-timeout 4 --max-time 12 --output /dev/null --write-out '%{http_code}' "https://workspace.sustainablecatalyst.com$path" || true)
    echo "PB04_ANONYMOUS_GET=$path HTTP=$code"
done
echo PB04_OWNER_SESSION=NOT_USED
echo PB04_WORKSPACE_WRITES=NONE
echo PB04_PRODUCTION_CHANGES=NONE
echo PB04_CONTABO_SOURCE_GATE=READ_ONLY_COMPLETE
