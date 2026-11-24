"""SC-PUB-ENDTOEND-01 release tool: the Studio overlay must make the Studio keyless and name its Research endpoints.

Pure checks of scripts/sc_pub_e2e01_release.py with the remote read replaced; no SSH, Docker or production access.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import sc_pub_e2e01_release as release  # noqa: E402

GOOD = '''services:
  sc-workspace-reporting:
    environment:
      SC_WORKSPACE_REPORTING_STUDIO_ENABLED: "1"
      # the backend alone holds the Research signing key
      SC_WORKSPACE_RESEARCH_API_ORIGIN: "https://research-api.sustainablecatalyst.com"
      SC_WORKSPACE_RESEARCH_SIGNING_BACKEND_URL: "http://sc-workspace-backend:8089"
      SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE: ""
    volumes: !override
      - sc-workspace-data:/data
'''


def check(monkeypatch, text):
    monkeypatch.setattr(release.base, "ssh", lambda command, **kw: text)
    release.check_overlay()


def test_keyless_overlay_is_accepted(monkeypatch):
    check(monkeypatch, GOOD)


@pytest.mark.parametrize("text, reason", [
    (GOOD.replace('      SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE: ""\n', ""), "lacks"),  # inherited key path kept
    (GOOD.replace('KEY_FILE: ""', "KEY_FILE: /run/sc-research/export_seed"), "lacks"),
    (GOOD.replace('KEY_FILE: ""', 'KEY_FILE: "/run/secrets/seed"'), "lacks"),
    (GOOD + "      - /home/x/ws_research_export_seed:/run/sc-research/export_seed:ro\n", "signing key"),
    (GOOD.replace("https://research-api.sustainablecatalyst.com", "http://research-api.sustainablecatalyst.com"), "lacks"),
    (GOOD.replace('      SC_WORKSPACE_RESEARCH_SIGNING_BACKEND_URL: "http://sc-workspace-backend:8089"\n', ""), "lacks"),
])
def test_overlays_that_could_give_the_studio_the_key_or_wrong_endpoints_are_refused(monkeypatch, text, reason):
    with pytest.raises(RuntimeError, match=reason):
        check(monkeypatch, text)


def test_release_is_pinned_to_a_full_commit(monkeypatch):
    monkeypatch.setenv("SC_PUB_E2E01_SOURCE_SHA", "f4739414")
    with pytest.raises(RuntimeError, match="full reviewed main commit"):
        release.configure()
    monkeypatch.setenv("SC_PUB_E2E01_SOURCE_SHA", "a" * 40)
    release.configure()
    assert release.base.IMAGE == "sc-workspace-reporting:e2e01-" + "a" * 12
    assert release.base.RELEASE == "sc-pub-e2e01-" + "a" * 12
