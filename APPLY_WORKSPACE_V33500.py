#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil, time
from pathlib import Path

NEW='3.35.0'; OLD='3.34.0'
MODIFIED_FILES=(
    'backend/app/config.py',
    'backend/app/main.py',
    'backend/app/polyglot.py',
    'backend/neural-runtime/service.py',
    'backend/tests/test_neural_gnn_runtime_foundation_v33300.py',
    'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php',
    'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php',
)

def fail(msg: str) -> None:
    raise SystemExit('ERROR: '+msg)

def copy_tree_files(src_root: Path, dest_root: Path) -> int:
    count=0
    if not src_root.exists():
        return 0
    for src in src_root.rglob('*'):
        if src.is_file():
            rel=src.relative_to(src_root)
            dest=dest_root/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dest)
            count+=1
    return count

def main() -> None:
    ap=argparse.ArgumentParser(description='Apply Workspace v3.35.0 using an idempotent authoritative-file overlay.')
    ap.add_argument('target')
    ap.add_argument('--release-root',default=str(Path(__file__).resolve().parent))
    ns=ap.parse_args()
    target=Path(ns.target).expanduser().resolve()
    rr=Path(ns.release_root).resolve()
    if not (target/'.git').is_dir():
        fail(f'Workspace git repository not found: {target}')
    cfg=target/'backend/app/config.py'
    svc=target/'backend/neural-runtime/service.py'
    if not cfg.exists() or not svc.exists():
        fail('Workspace backend baseline files are missing')
    ct=cfg.read_text(errors='replace')
    st=svc.read_text(errors='replace')
    cfg_ok=('service_version: str = "3.34.0"' in ct or 'service_version: str = "3.35.0"' in ct)
    svc_ok=('SERVICE_VERSION = "3.34.0"' in st or 'SERVICE_VERSION = "3.35.0"' in st)
    if not cfg_ok or not svc_ok:
        fail('v3.34.0/v3.35.0 baseline markers not found; refusing to overwrite an unknown Workspace version')

    repair=rr/'repair_payload'
    missing=[rel for rel in MODIFIED_FILES if not (repair/rel).is_file()]
    if missing:
        fail('repair payload is incomplete: '+', '.join(missing))

    stamp=time.strftime('%Y%m%d-%H%M%S')
    backup=target/'.workspace-repair-backups'/'v3.35.0.1'/stamp
    backed=0
    for rel in MODIFIED_FILES:
        src=target/rel
        if src.exists():
            dest=backup/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dest)
            backed+=1
    print(f'WORKSPACE_V335001_BACKUP={backup} files={backed}')

    overwritten=0
    for rel in MODIFIED_FILES:
        src=repair/rel
        dest=target/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dest)
        overwritten+=1

    added=copy_tree_files(rr/'payload',target)

    # Keep release-engineering files in the repository, matching prior Workspace releases.
    names=[
        'APPLY_AND_PUSH_WORKSPACE_V33500.sh','APPLY_WORKSPACE_V33500.py',
        'PACKAGE_WORKSPACE_V33500.sh','VALIDATE_WORKSPACE_V33500.py',
        'DEPLOY_WORKSPACE_BACKEND_V33500_CONTABO.sh','DEPLOY_WORKSPACE_BACKEND_V33500.md',
        'RELEASE_NOTES_3.35.0.md','GNN_EVALUATION_EXPLAINABILITY_GRAPH_EMBEDDINGS_V33500.md',
        'VALIDATION_REPORT_3.35.0.md','WORKSPACE_V33500.patch','REPAIR_NOTES_3.35.0.1.md'
    ]
    for name in names:
        src=rr/name
        if src.exists():
            shutil.copy2(src,target/name)
    backend=target/'backend'
    for name in [
        'DEPLOY_WORKSPACE_BACKEND_V33500.md','RELEASE_NOTES_3.35.0.md',
        'GNN_EVALUATION_EXPLAINABILITY_GRAPH_EMBEDDINGS_V33500.md','VALIDATION_REPORT_3.35.0.md'
    ]:
        src=rr/name
        if src.exists():
            shutil.copy2(src,backend/name)

    print(f'WORKSPACE_V335001_AUTHORITATIVE_OVERWRITE={overwritten}')
    print(f'WORKSPACE_V335001_NEW_PAYLOAD_FILES={added}')
    print('APPLIED_WORKSPACE_V33500=PASS')

if __name__=='__main__':
    main()
