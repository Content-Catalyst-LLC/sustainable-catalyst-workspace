"""SC-SCI-02: signing in from the Notebook Desk returns to the desk, and nowhere off-site.

The ERW account sign-in page reads ``?returnTo=`` and follows it only to the desk or the private research UI on
the same origin. The desk links to whichever sign-in the session profile says is configured.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from app import erw_identity_bridge as bridge

DESK_JS = Path(__file__).resolve().parents[1] / "app/static/notebook_desk/notebook-desk.js"

NODE = r"""
const [script, cases] = [process.argv[1], JSON.parse(process.argv[2])];
const out = [];
for (const search of cases) {
  let target = null;
  const fake = {
    location: { search, assign: (t) => { target = t; } },
    URLSearchParams,
    document: { querySelector: (q) => ({ value: q === '#password' ? 'pw' : 'u', textContent: '', set onsubmit(f) { this.f = f; } }) },
    fetch: async () => ({ ok: true }),
  };
  const forms = [];
  fake.document.querySelector = (q) => { const o = { value: 'x', textContent: '' }; if (q === '#form') forms.push(o); return o; };
  new Function('document', 'location', 'fetch', 'URLSearchParams', script)(fake.document, fake.location, fake.fetch, URLSearchParams);
  out.push(forms[0].onsubmit({ preventDefault() {} }).then(() => target));
}
Promise.all(out).then((r) => console.log(JSON.stringify(r)));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_erw_sign_in_returns_only_to_the_desk_or_the_research_ui():
    script = re.search(r"<script>(.*)</script>", bridge.LOGIN_HTML, re.S).group(1)
    cases = {
        "?returnTo=%2Fv1%2Fdesk%2Fnotebooks%3Fproject%3Dp1%26notebook%3Dn1": "/v1/desk/notebooks?project=p1&notebook=n1",
        "?returnTo=%2Fv1%2Fdesk%2Fnotebooks": "/v1/desk/notebooks",
        "?returnTo=%2Fv1%2Fprivate-research%2Fui%23projects": "/v1/private-research/ui#projects",
        "": "/v1/private-research/ui",
        "?returnTo=https%3A%2F%2Fevil.example%2Fv1%2Fdesk%2Fnotebooks": "/v1/private-research/ui",
        "?returnTo=%2F%2Fevil.example%2Fv1%2Fdesk%2Fnotebooks": "/v1/private-research/ui",
        "?returnTo=%2Fv1%2Fdesk%2Fnotebooks.evil": "/v1/private-research/ui",
        "?returnTo=%2Fv1%2Fdesk%2Fnotebooks%2F..%2F..%2Fadmin": "/v1/private-research/ui",
        "?returnTo=javascript%3Aalert(1)": "/v1/private-research/ui",
        "?returnTo=%2Fv1%2Fprojects": "/v1/private-research/ui",
    }
    raw = subprocess.run(["node", "-e", NODE, script, json.dumps(list(cases))], capture_output=True, text=True, check=True).stdout
    assert json.loads(raw) == list(cases.values())


def test_erw_sign_in_page_policy_is_unchanged():
    headers = bridge.login_page().headers
    assert "connect-src 'self'" in headers["content-security-policy"] and headers["cache-control"] == "no-store"


def test_desk_links_to_the_configured_sign_in_and_keeps_its_place():
    js = DESK_JS.read_text()
    show = js.split("async function showSignIn()", 1)[1].split("\n}\n", 1)[0]
    assert '"/v1/private-research/login"' in show and '"/v1/auth/login"' in show
    assert "returnTo=${encodeURIComponent(DESK + location.search)}" in show
    idp = js.split("async function identityProvider()", 1)[1].split("\n}\n", 1)[0]
    assert '"/v1/session/profile"' in idp and "globalIdentityProviderConfigured" in idp
    # Sign-out clears the Workspace session when there is no SC Identity session to end.
    assert 'fetch("/v1/session", { method: "DELETE"' in js
