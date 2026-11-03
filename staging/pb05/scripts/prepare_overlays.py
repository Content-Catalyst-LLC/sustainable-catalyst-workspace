#!/usr/bin/env python3
"""Create explicit, hash-checked *isolated staging copies*, never patch live code.

Requires a narrow change of hard-coded Origin in two already inspected source
modules, from the real HTTPS Workspace origin to SSH-tunneled HTTPS localhost.
"""
import hashlib
from pathlib import Path
import sys

if len(sys.argv) != 4:
    raise SystemExit('Usage: prepare_overlays.py <installed_private_module> <tested_pb04_module> <output_dir>')
private, publication, out = [Path(x) for x in sys.argv[1:]]
if out.exists() and any(out.iterdir()):
    raise SystemExit('PB05_OVERLAY_OUTPUT_NOT_EMPTY')
out.mkdir(mode=0o700, parents=True, exist_ok=True)
expected = {
    'wxr_private_projects.py': '0ff03dd0567b2f73a91ca5bd16b03590c68c31f5f93439dcf34ff470c6af5df0',
    'rd014_publication_records.py': '480fa0e797101a1f9662eb5d89de7391ff417bd17936e2e405bee1cac32b4f9c',
}
old = 'ORIGIN = "https://workspace.sustainablecatalyst.com"'
new = 'ORIGIN = "https://localhost:18443"'
for path, name in [(private, 'wxr_private_projects.py'), (publication, 'rd014_publication_records.py')]:
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected[name]:
        raise SystemExit('PB05_SOURCE_DRIFT=' + name + ' SHA256=' + actual)
    text = raw.decode('utf-8')
    if text.count(old) != 1:
        raise SystemExit('PB05_ORIGIN_ANCHOR_MISSING_OR_AMBIGUOUS=' + name)
    changed = text.replace(old, new, 1)
    if changed.count(old) or changed.count(new) != 1:
        raise SystemExit('PB05_ORIGIN_REWRITE_FAILED=' + name)
    compile(changed, name, 'exec')
    (out / name).write_text(changed, encoding='utf-8')
    (out / name).chmod(0o600)
    print('PB05_OVERLAY=' + name + ' SHA256=' + hashlib.sha256(changed.encode()).hexdigest())
print('PB05_STRICT_HTTPS_STAGING_ORIGIN=PASS')
