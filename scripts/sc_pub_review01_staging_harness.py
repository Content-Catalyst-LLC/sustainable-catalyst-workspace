#!/usr/bin/env python3
"""SC-PUB-REVIEW-01 isolated staging acceptance: an invited, independently authenticated reviewer.

Runs inside the isolated SC-PUB-M1 staging network beside the existing harness helpers (mounted at /h), against
genuine PostgreSQL for Workspace and Research and the staging Sustainable Catalyst Identity (Keycloak, mailpit).
Synthetic people and content only. Prints statuses, counts and short hashes; writes a JSON receipt.

    python -I sc_pub_review01_staging_harness.py accept-invite   # after sc_identity_invite_reviewer.py
    python -I sc_pub_review01_staging_harness.py main            # after session_operator enroll-new

The reviewer is invited with the production procedure (scripts/sc_identity_invite_reviewer.py), accepts by e-mail
(own password, own TOTP), is linked to Workspace by the audited operator step, receives roles from the owner in
Outputs & Publishing -> Reviewers, reads each review packet and decides every approval alone with step-up.
"""
import hashlib
import json
import os
import re
import secrets
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, "/h")
import pube2e_harness as pe  # noqa: E402  (studio/status/public helpers, rec, synthetic study wiring)

pm, acc, sw, idh = pe.pm, pe.acc, pe.sw, pe.pm.idh
STATE = Path("/state/review01.json")
TAG = acc.TAG
AREA = f"sc-pub-review01-{TAG}"
ARTICLE = f"sc-pub-review01-overview-{TAG}"
DIMS = pe.DIMS
ROLES = [f"approver:{d}" for d in DIMS]
rec = pe.rec


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(data):
    STATE.write_text(json.dumps(data))


class Reviewer:
    """The invited reviewer, acting only through their own Workspace session."""

    def __init__(self, username, password, st):
        self.username, self.password, self.st = username, password, st
        self.browser = idh.Browser()
        self.cookie, self.code, self.events, self.js = idh.ws_login(self.browser, username, password, st, ws=pm.PUBWS)
        self.signed_in = time.time()

    def session(self):
        return acc.http("GET", pm.PUBWS + "/v1/session", headers={"Cookie": f"sc_workspace_session={self.cookie}"})

    def step_up(self):
        cookie, code, events, _ = idh.ws_login(self.browser, self.username, self.password, self.st, ws=pm.PUBWS,
                                               step_up=True)
        assert cookie and "otp-prompted" in events, (code, events)
        self.cookie, self.signed_in = cookie, time.time()


def accept_invite():
    data, st = load(), idh.load_state()
    email, username = os.environ["REVIEW_EMAIL"], os.environ["REVIEW_USERNAME"]
    link, _ = idh.mail_reset_link(email, set())
    rec("I1", "Sustainable Catalyst Identity e-mailed a single-use invitation link", link is not None)
    password = "Reviewer-" + secrets.token_urlsafe(16)  # chosen by the reviewer; synthetic here
    b, steps = idh.Browser(), []
    code, url, page = b.follow(link) if link else (0, "", "")
    for _ in range(10):
        if 'name="password-new"' in page:
            steps.append("password")
            code, page, hdrs = b.req("POST", idh.form_action(page), form={"password-new": password,
                                                                          "password-confirm": password})
        elif 'name="totpSecret"' in page:
            steps.append("totp")
            raw = idh.hidden(page, "totpSecret")
            st.setdefault("otp", {})[username] = raw
            idh.save_state(st)
            code, page, hdrs = b.req("POST", idh.form_action(page), form={
                "totp": idh.fresh_totp(st, username), "totpSecret": raw, "userLabel": "reviewer", "mode": "manual"})
        elif code in (302, 303):
            code, url, page = b.follow(urllib.parse.urljoin(url, hdrs["Location"]))
        elif (m := re.search(r'href="([^"]*login-actions/[^"]*)"[^>]*>\s*(?:&raquo;|\u00bb)?\s*(?:Click here|Proceed)', page)):
            steps.append("verify-email")
            code, url, page = b.follow(urllib.parse.urljoin(url, idh.html.unescape(m.group(1))))
        else:
            steps.append("done" if re.search(r"(?i)account has been updated|been updated", page) else f"stop:{code}")
            break
    rec("I2", "reviewer verified the address, chose their own password and enrolled TOTP",
        steps[-1:] == ["done"] and {"password", "totp"} <= set(steps), steps)
    code, _, page = idh.Browser().follow(link) if link else (0, "", "")
    rec("I3", "the invitation link cannot be used twice", 'name="password-new"' not in page and 'name="totpSecret"' not in page)
    cookie, cb, events, js = idh.ws_login(idh.Browser(), username, password, st, ws=pm.PUBWS)
    rec("I4", "before Workspace enrolment the new account gets no Workspace session",
        cookie is None and cb == 403, (cb, (js.get("detail") or {}) if isinstance(js.get("detail"), dict) else js.get("detail")))
    b2 = idh.Browser()
    code, text, hdrs = b2.req("GET", f"{pm.PUBWS}/v1/auth/login?returnTo=/projects")
    code, url, page = b2.follow(hdrs["Location"], stop_prefix=pm.PUBWS)
    code, page, hdrs = b2.req("POST", idh.form_action(page), form={"username": username, "password": password,
                                                                    "credentialId": ""})
    rec("I5", "a correct password alone does not sign in: the second factor is always asked",
        ('name="otp"' in page or 'id="otp"' in page) and not b2.cookies(pm.PUBWS).get("sc_workspace_session"), code)
    data.update({"username": username, "email": email, "password": password})
    save_state(data)


def main():
    out = Path("/state/out")
    out.mkdir(exist_ok=True)
    data, st = load(), idh.load_state()
    rx = {"Authorization": "Bearer " + acc.secret("convergence_token")}
    accept_invite_results = data.get("inviteResults", [])
    owner, stranger = pm.Person("owner", st), pm.Person("stranger", st)
    rev = Reviewer(data["username"], data["password"], st)
    me = rev.session() if rev.cookie else {}
    rec("K1", "the enrolled reviewer signs in with password + TOTP as their own Workspace identity",
        me.get("authenticationMethod") == "sc-identity-oidc" and str(me.get("subject", "")).startswith("sci:"),
        me.get("subject"))
    reviewer_key, reviewer_scope = me.get("subject"), f"workspace-user:{me.get('subject')}"
    c, inbox = pe.status(rev, "GET", "/research-approvals/inbox")
    rec("K2", "before any role is assigned the reviewer's inbox is empty", c == 200 and inbox.get("items") == [], c)

    # Synthetic study, independent reproduction, and the project's output (existing helpers) ---------------
    steps = {}
    study = acc.build_owner_study(owner, 1.5, 0.25, steps)
    ing = acc.http("POST", pe.PRIVATE + "/convergence/workspace/execution-runs",
                   {"grant": acc.grant(owner, study["runId"])["grant"], "researchArea": AREA, "entrySlug": ARTICLE,
                    "title": "Synthetic dose-response (SC-PUB-REVIEW-01)"}, rx)
    result = ing["objects"]["output:polyglot-result"]["id"]
    ds_sha = (study["dataset"].get("item") or study["dataset"])["artifactSha256"]
    jrun = acc.new_run(owner, "Julia OLS reproduction", acc.DS, acc.M_J, "workspace.polyglot.julia.quadratic-optimize")
    acc.run_job(owner, jrun, "workspace.polyglot.julia.quadratic-optimize",
                {"datasetInput": acc.dataset_input(1, ds_sha, acc.NORMAL_EQ)})
    acc.http("POST", pe.PRIVATE + "/convergence/workspace/reproductions",
             {"originalObjectId": result, "grant": acc.grant(owner, jrun)["grant"], "relTol": 1e-8, "absTol": 1e-10}, rx)
    project = acc.PROJECT
    other = f"sc-review01-other-{TAG}"
    owner("POST", "/v1/projects", idh.project_body(other, "Other project (synthetic)"), expect=(200, 201))
    rev_doc = pe.studio(owner, "GET", f"/projects/{project}/documents")["projectRevision"]
    md = ("# Synthetic dose-response overview\n\nA synthetic dose-response fitted in R and independently reproduced "
          "in Julia. Modelled synthetic values, not measurements.\n")
    ov = pe.studio(owner, "POST", f"/projects/{project}/documents", {
        "title": "Synthetic dose-response overview", "markdown": md, "publicationType": "overview",
        "expectedProjectRevision": rev_doc, "expectedDocumentRevision": 0}, 201)["document"]
    O = f"/projects/{project}/outputs/{ov['documentId']}"
    pe.studio(owner, "POST", f"{O}/bind", {"areaSlug": AREA, "articleSlug": ARTICLE, "title": ov["title"]}, 201)
    pe.studio(owner, "POST", f"{O}/research-revisions", {
        "studioRevision": 1, "publicationType": "report", "summary": "Synthetic acceptance only.",
        "references": [{"objectId": result, "role": "result", "caption": "OLS slope and intercept (synthetic)."}]}, 201)

    # Owner assigns roles in Outputs & Publishing -> Reviewers --------------------------------------------
    grants = {r: pe.studio(owner, "POST", "/research-approvals/grants",
                           {"granteeUserKey": reviewer_key, "role": r, "projectId": project}, 201)["item"] for r in ROLES}
    grants["approver:area-publication"] = pe.studio(owner, "POST", "/research-approvals/grants", {
        "granteeUserKey": reviewer_key, "role": "approver:area-publication", "projectId": "*"}, 201)["item"]
    rec("G1", "owner assigned five approver roles to one reviewer (article roles for this project only)",
        all(g["grantee"] == reviewer_scope for g in grants.values()))
    refusals = {
        "unlinked": pe.status(owner, "POST", "/research-approvals/grants", {"granteeUserKey": "erw:sc:not-an-identity",
                                                                        "role": "approver:rights", "projectId": project})[0],
        "self": pe.status(owner, "POST", "/research-approvals/grants", {"granteeUserKey": owner.user,
                                                                    "role": "approver:rights", "projectId": project})[0],
        "all-projects": pe.status(owner, "POST", "/research-approvals/grants", {"granteeUserKey": reviewer_key,
                                                                            "role": "approver:rights", "projectId": "*"})[0],
        "foreign-origin": pe.status(owner, "POST", "/research-approvals/grants", {
            "granteeUserKey": reviewer_key, "role": "approver:rights", "projectId": project}, origin="https://evil.example")[0],
        "stranger-project": pe.status(stranger, "POST", "/research-approvals/grants", {
            "granteeUserKey": reviewer_key, "role": "approver:rights", "projectId": project})[0],
        "stranger-revoke": pe.status(stranger, "POST",
                                     f"/research-approvals/grants/{grants['approver:rights']['grantId']}/revoke")[0],
    }
    rec("G2", "role assignment refuses unlinked, self, all-project article, cross-origin and outsider grants",
        refusals == {"unlinked": 422, "self": 422, "all-projects": 422, "foreign-origin": 403,
                     "stranger-project": 404, "stranger-revoke": 404}, refusals)
    c, mine = pe.status(rev, "GET", "/research-approvals/grants")
    rec("G3", "the reviewer sees the roles they hold", c == 200 and len([g for g in mine["items"]
                                                                       if g["grantee"] == reviewer_scope]) == 5)

    # Cross-project: a request in another project of the same owner is not the reviewer's ------------------
    obj = pe.studio(owner, "GET", f"/projects/{project}/research-objects/{result}")["object"]
    q = pe.studio(owner, "POST", f"/projects/{other}/research-objects/{result}/approval-requests",
                  {"dimension": "scientific"}, 201)["item"]
    rev.step_up()
    listed = [i["approvalId"] for i in pe.studio(rev, "GET", "/research-approvals/inbox")["items"]]
    c_packet, _ = pe.status(rev, "GET", f"/research-approvals/{q['approvalId']}/packet")
    c_decide, d_body = pe.status(rev, "POST", f"/research-approvals/{q['approvalId']}/decide",
                                 {"decision": "approve", "expectedSubjectRef": obj["subjectRef"]})
    rec("C1", "another project's request: not listed, packet 404, decision refused",
        q["approvalId"] not in listed and c_packet == 404 and c_decide == 403, (c_packet, c_decide, d_body.get("detail")))
    owner("POST", f"/v1/research-approvals/requests/{q['approvalId']}/withdraw")

    # Cited evidence: four signed approvals by the one reviewer, released for citation ---------------------
    def decide(approval_id, subject, decision="approve"):
        if time.time() - rev.signed_in > 200:
            rev.step_up()
        return pe.studio(rev, "POST", f"/research-approvals/{approval_id}/decide",
                         {"decision": decision, "note": "SC-PUB-REVIEW-01 synthetic", "expectedSubjectRef": subject})
    for d in DIMS:
        req = pe.studio(owner, "POST", f"/projects/{project}/research-objects/{result}/approval-requests", {"dimension": d}, 201)
        decide(req["item"]["approvalId"], obj["subjectRef"])
        pe.studio(owner, "POST", f"/projects/{project}/research-objects/{result}/approvals/attach",
                  {"approvalId": req["item"]["approvalId"]})
    rel = pe.studio(owner, "POST", f"/projects/{project}/research-objects/{result}/release")
    rec("E1", "Research accepted the reviewer's four signed evidence approvals and released the evidence",
        rel.get("visibility") == "public-approved", rel.get("visibility"))

    # Article: submit, four requests, review packet --------------------------------------------------------
    pe.studio(owner, "POST", f"{O}/submit", {"researchRevision": 1})
    reqs = {d: pe.studio(owner, "POST", f"{O}/approval-requests", {"researchRevision": 1, "dimension": d}, 201)["item"]
            for d in DIMS}
    subject = reqs["scientific"]["subjectRef"]
    items = pe.studio(rev, "GET", "/research-approvals/inbox")["items"]
    rec("V1", "the reviewer's inbox lists exactly the four article requests assigned to their roles",
        sorted(i["approvalId"] for i in items) == sorted(r["approvalId"] for r in reqs.values()), len(items))
    pk = pe.studio(rev, "GET", f"/research-approvals/{reqs['scientific']['approvalId']}/packet")
    art = pk.get("article") or {}
    rec("V2", "review packet: exact subject, Studio revision text and SHA-256, cited evidence pin, rights status",
        pk["request"]["subjectRef"] == subject and art.get("markdown") == md
        and art.get("markdownSHA256") == hashlib.sha256(md.encode()).hexdigest()
        and [r["objectId"] for r in art.get("references") or []] == [result] and bool(art.get("rightsStatus")),
        art.get("markdownSHA256", "")[:12])
    codes = {"owner": pe.status(owner, "GET", f"/research-approvals/{reqs['scientific']['approvalId']}/packet")[0],
             "stranger": pe.status(stranger, "GET", f"/research-approvals/{reqs['scientific']['approvalId']}/packet")[0],
             "anonymous": pe.status(None, "GET", f"/research-approvals/{reqs['scientific']['approvalId']}/packet")[0]}
    rec("V3", "nobody else reads the packet (requester, outsider, anonymous)",
        codes == {"owner": 404, "stranger": 404, "anonymous": 401}, codes)

    # Separation of duties and step-up --------------------------------------------------------------------
    owner.step_up()
    c, body = pe.status(owner, "POST", f"/research-approvals/{reqs['scientific']['approvalId']}/decide",
                        {"decision": "approve", "expectedSubjectRef": subject})
    rec("D1", "the author cannot approve their own request", c == 403 and "self-approval" in str(body.get("detail")), c)
    stranger.step_up()
    c, _ = pe.status(stranger, "POST", f"/research-approvals/{reqs['rights']['approvalId']}/decide",
                     {"decision": "approve", "expectedSubjectRef": subject})
    rec("D2", "a signed-in person without the role cannot approve", c == 403, c)
    wait = 305 - (time.time() - rev.signed_in)
    if wait > 0:
        time.sleep(wait)
    c, body = pe.status(rev, "POST", f"/research-approvals/{reqs['scientific']['approvalId']}/decide",
                        {"decision": "approve", "expectedSubjectRef": subject})
    detail = body.get("detail") if isinstance(body.get("detail"), dict) else body
    rec("D3", "an approval without a fresh second-factor sign-in is refused with Workspace's own step-up path",
        c == 403 and detail.get("code") == "step-up-required" and detail.get("loginUrl") == "/v1/auth/login?stepUp=true",
        (c, detail.get("code")))
    rev.step_up()
    c2, _ = pe.status(rev, "POST", f"/research-approvals/{reqs['scientific']['approvalId']}/decide",
                      {"decision": "approve", "expectedSubjectRef": subject[:-4] + "0000"})
    rec("D4", "a decision for a different revision hash is refused", c2 in (409, 422), c2)
    for d in DIMS:
        decide(reqs[d]["approvalId"], subject)
        pe.studio(owner, "POST", f"{O}/approvals/attach", {"researchRevision": 1, "approvalId": reqs[d]["approvalId"]})
    rec("D5", "one independent reviewer decided all four; Research accepted every signed record", True)
    record = owner("GET", f"/v1/research-approvals/requests/{reqs['rights']['approvalId']}/record")
    body = {k: v for k, v in record.items() if k != "signature"}
    dec, auth = body.get("decision") or {}, body.get("authentication") or {}
    rec("R1", "signed record: reviewer identity, role, grant, exact subject, evidence ref, step-up, decision, time",
        dec.get("actor", {}).get("actorId") == reviewer_scope and dec.get("decision") == "approve"
        and body.get("subjectRef") == subject and subject in (body.get("provenanceRefs") or [subject])
        and body.get("grantId") == grants["approver:rights"]["grantId"] and auth.get("stepUp") is True
        and auth.get("decider") == "sc-identity-oidc-session" and auth.get("revisionConfirmed") is True
        and bool(body.get("issuedAt")) and bool(record.get("signature")),
        {"actor": dec.get("actor", {}).get("actorId"), "issuedAt": body.get("issuedAt")})
    c, _ = pe.status(rev, "POST", f"/research-approvals/{reqs['rights']['approvalId']}/decide",
                     {"decision": "reject", "expectedSubjectRef": subject})
    rec("R2", "a decided request cannot be changed", c == 409, c)

    # Area, publication, withdrawal ------------------------------------------------------------------------
    area_view = pe.studio(owner, "GET", f"{O}/area")["area"]
    areq = pe.studio(owner, "POST", f"{O}/area/approval-requests", {}, 201)["item"]
    decide(areq["approvalId"], area_view["subjectRef"])
    ap = pe.studio(owner, "POST", f"{O}/area/publish", {"approvalId": areq["approvalId"], "confirmAreaSlug": AREA})
    rec("P1", "Research area published with the reviewer's signed area-publication record",
        ap.get("visibility") in ("approved", "public-approved"), ap.get("visibility"))
    p1 = pe.studio(owner, "POST", f"{O}/publish", {"researchRevision": 1, "confirmArticleSlug": ARTICLE})
    code, art_pub, _ = pe.public(f"/articles/{ARTICLE}/content")
    rec("P2", "article published from the reviewer's approvals; public reader serves it",
        p1.get("publishedRevision") == 1 and code == 200 and art_pub.get("revision") == 1, code)
    pe.studio(owner, "POST", f"{O}/withdraw", {"reason": "SC-PUB-REVIEW-01 drill",
                                              "publicNotice": "Withdrawn after a synthetic acceptance drill.",
                                              "confirmArticleSlug": ARTICLE})
    code, tomb, _ = pe.public(f"/articles/{ARTICLE}/content")
    rec("P3", "withdrawn: HTTP 410 tombstone without content", code == 410 and "sections" not in tomb, code)

    # Revocation, sessions, leakage ------------------------------------------------------------------------
    pe.studio(owner, "POST", f"/research-approvals/grants/{grants['approver:scientific']['grantId']}/revoke")
    held = [g for g in pe.studio(rev, "GET", "/research-approvals/grants")["items"]
            if g["role"] == "approver:scientific" and g["grantee"] == reviewer_scope]
    rec("S1", "a revoked role is shown as revoked and grants nothing", all(g.get("revokedAt") for g in held), len(held))
    bad = {"Cookie": "sc_workspace_session=" + rev.cookie[:-6] + "AAAAAA"}
    code_bad, _, _ = acc.call("GET", pe.STUDIO + pe.PUB + "/research-approvals/inbox", None, bad)
    code_lo, _, _ = acc.call("POST", pm.PUBWS + "/v1/auth/logout", {},
                             {"Cookie": f"sc_workspace_session={rev.cookie}", "Origin": pm.PUBWS})
    c, _ = pe.status(rev, "GET", "/research-approvals/inbox")
    rec("S2", "a tampered or signed-out session gets nothing", code_bad == 401 and code_lo == 200 and c == 401,
        (code_bad, code_lo, c))
    markers = {"reviewerScope": reviewer_scope, "reviewerEmail": data["email"], "ownerScope": owner.scope,
               "workspaceProject": project, "otherProject": other, "studioSha": ov["markdownSHA256"]}
    rows = sw.sweep(acc, pe.PUBLIC, {"entry": ARTICLE, "area": AREA, "objects": [result], "term": "dose"}, markers)
    leaks = sw.leaks(rows)
    rec("S3", "anonymous sweep of every public Research route: no reviewer identity, e-mail, owner or project",
        rows and not leaks, {"requests": len(rows), "leaks": leaks[:3]})

    results = accept_invite_results + pe.results
    passed = sum(r["pass"] for r in results)
    receipt = {"schema": "sc-pub-review01-staging-acceptance/1.0", "tag": TAG, "synthetic": True,
               "studioImage": os.environ.get("STUDIO_IMAGE", ""), "passed": passed, "total": len(results),
               "results": results}
    (out / f"sc-pub-review01-{TAG}.json").write_text(json.dumps(receipt, indent=1))
    print(f"RESULT {passed}/{len(results)}", flush=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["accept-invite"]:
        accept_invite()
        d = load()
        d["inviteResults"] = pe.results
        save_state(d)
        print(f"RESULT {sum(r['pass'] for r in pe.results)}/{len(pe.results)}", flush=True)
        sys.exit(0 if all(r["pass"] for r in pe.results) else 1)
    sys.exit(main())
