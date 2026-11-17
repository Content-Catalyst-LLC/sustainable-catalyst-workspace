#!/usr/bin/env python3
"""SC-PUB-ENDTOEND-01: guarded Reporting Studio release of Outputs & Publishing (with SC-PUB-LAYOUT-01).

Reuses the reviewed SC-PUB-PDFSVG-01 operator (exact-source build on the host, off-host backup and isolated restore
gate, studio.sh cutover and automatic rollback) and adds only what this release needs. Run on the off-host Mac
checkout with the exact reviewed main commit:

    SC_PUB_E2E01_SOURCE_SHA=<merged main sha> python3 scripts/sc_pub_e2e01_release.py status|build|recover|deploy|rollback

The Studio keeps running without the Research signing key: it asks the backend for each person's Research session and
to sign approval decisions. Deployment refuses unless the Studio overlay names the Research API and that backend, and
does not mount the key. It publishes nothing: every Research release stays a separate, confirmed action by the owner.
"""
from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sc_pub_pdfsvg_release as base  # noqa: E402

OVERLAY = "$HOME/sc-sci02/rd/reporting-studio.yml"
REQUIRED_ENV = {
    "SC_WORKSPACE_RESEARCH_API_ORIGIN": "https://research-api.sustainablecatalyst.com",
    "SC_WORKSPACE_RESEARCH_SIGNING_BACKEND_URL": "http://sc-workspace-backend:8089",
}
OUTPUTS = "http://127.0.0.1:20080/v1/private-research/reporting-studio/publication/projects/x/outputs"
# Exact image check: the new modules import, the outputs UI ships, and the layout engine is present. Synthetic only.
SMOKE_PY = ("import app.research_outputs as o, app.publication_layout, app.reporting_publication as p;"
            "import pathlib; assert pathlib.Path(p.__file__).with_name('reporting_outputs_ui.js').stat().st_size > 1000;"
            "assert o.SCHEMA == 'sc-workspace-research-output/1.0'")


def configure():
    sha = os.environ.get("SC_PUB_E2E01_SOURCE_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        base.fail("SC_PUB_E2E01_SOURCE_SHA must be the full reviewed main commit")
    base.SOURCE_SHA, base.SHORT = sha, sha[:12]
    base.IMAGE = f"sc-workspace-reporting:e2e01-{base.SHORT}"
    base.RELEASE = "sc-pub-e2e01-" + base.SHORT
    base.STATE = Path.home() / ".sc-pub-e2e01" / f"{base.RELEASE}.json"
    base.PDFSVG_SMOKE_PY = SMOKE_PY  # run by base.build() in the candidate image (network none)
    os.environ["SC_PUB_RECOVERY_RELEASE"] = base.RELEASE


def on_main():
    base.execute(["git", "-C", str(base.ROOT), "fetch", "-q", "origin", "main"], timeout=60)
    try:
        base.execute(["git", "-C", str(base.ROOT), "merge-base", "--is-ancestor", base.SOURCE_SHA, "origin/main"])
    except RuntimeError:
        base.fail("Source commit is not on reviewed origin/main")


def check_overlay():
    text = base.ssh("cat " + OVERLAY)
    missing = [f'      {k}: "{v}"' for k, v in REQUIRED_ENV.items() if not re.search(rf"^\s+{k}:\s*\"?{re.escape(v)}\"?\s*$", text, re.M)]
    if missing:
        base.fail("Studio overlay lacks the Outputs & Publishing settings; add under environment:\n" + "\n".join(missing))
    if re.search(r"SIGNING_KEY_FILE|export_seed|sc-research/", text):
        base.fail("Studio overlay must not give the Studio the Research signing key")


def verify_live(candidate):
    updated = base.assert_live()
    if updated["image_ref"] != base.IMAGE or updated["image_id"] != candidate["image_id"]:
        base.fail("Live container is not using the approved image digest")
    base.check_probe(after_cutover=True)
    code = base.ssh(base.quoted("curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "8", OUTPUTS))
    if code != "401":
        base.fail("Anonymous Outputs & Publishing access not refused (HTTP " + code + ")")
    base.ssh(base.quoted("docker", "exec", base.LIVE, "python", "-c", SMOKE_PY), timeout=60)
    # No key in the Studio, and the backend issuer it relies on answers (anonymous: 401). Values are never printed.
    keyless = base.ssh(base.quoted("docker", "exec", base.LIVE, "sh", "-c",
                                   "test ! -e /run/sc-research/export_seed && "
                                   "test -z \"$SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE\" && echo keyless"))
    if keyless != "keyless":
        base.fail("Studio has access to the Research signing key")
    issuer = base.ssh(base.quoted("docker", "exec", base.LIVE, "python", "-c",
                                  "import urllib.request as u\ntry:u.urlopen(u.Request("
                                  "'http://sc-workspace-backend:8089/v1/research-access/session',method='POST'),timeout=5)\n"
                                  "except Exception as e:print(getattr(e,'code','down'))"))
    if issuer != "401":
        base.fail("Backend Research session issuer not reachable from the Studio")


def deploy():
    on_main()
    state = base.read_state()
    live = base.assert_live()
    if live != state.get("live_before"):
        base.fail("Live Studio has changed since candidate build; refresh baseline")
    candidate = base.docker_inspect(base.IMAGE, True)
    if candidate["source_sha"] != base.SOURCE_SHA or candidate["image_id"] != state["candidate_image_id"]:
        base.fail("Candidate image no longer matches pinned build")
    base.verify_recovery(live)
    check_overlay()
    base.check_probe()
    if not sys.stdin.isatty():
        base.fail("Production deployment requires a real interactive operator terminal")
    print(f"READY FOR STUDIO CUTOVER | {base.LIVE}: {live['image_ref']} -> {base.IMAGE}")
    print("Publishes nothing. Research releases remain separate owner-confirmed actions.")
    if input("Type DEPLOY SC-PUB-ENDTOEND-01: ") != "DEPLOY SC-PUB-ENDTOEND-01":
        base.fail("Operator declined cutover")
    if base.assert_live() != live or base.docker_inspect(base.IMAGE, True) != candidate:
        base.fail("Image or live baseline changed immediately before cutover")
    try:
        base.ssh('bash "$HOME/sc-sci02/rd/studio.sh" cutover ' + shlex.quote(base.IMAGE), timeout=360)
    except Exception:
        base.fail("Protected cutover failed; inspect existing studio.sh rollback outcome")
    try:
        verify_live(candidate)
    except Exception as error:
        base.rollback(str(error))
    print("DEPLOYED: Outputs & Publishing and layout; health 200, anonymous 401, keyless Studio, backend issuer reachable.")
    print("Next: authenticated owner acceptance with synthetic content; no public release without the owner's approval.")


def main():
    configure()
    mode = sys.argv[1] if len(sys.argv) == 2 else ""
    if mode == "build":
        on_main()
        base.build()
    elif mode == "deploy":
        deploy()
    elif mode == "status":
        info = base.assert_live()
        print(f"LIVE: {info['image_ref']} | image_id={info['image_id']} | candidate={base.IMAGE}")
        base.check_probe()
        print("PASS: health and anonymous Studio access denial")
    elif mode in ("recover", "rollback"):
        sys.argv = [sys.argv[0], mode]
        base.main()
    else:
        base.fail("usage: status|build|recover|deploy|rollback")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(str(exc) if str(exc).startswith("NO-GO:") else "NO-GO: " + str(exc), file=sys.stderr)
        sys.exit(1)
