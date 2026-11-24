#!/usr/bin/env python3
"""SC-PUB-ENDTOEND-01 isolated staging acceptance: Workspace Outputs & Publishing -> Research -> public reader.

Runs inside the isolated SC-PUB-M1 staging network beside the existing harness helpers (mounted at /h): synthetic
SC Identity people (password + TOTP, step-up for approvals), a synthetic study and its independent reproduction (seeded
with the existing helpers), and genuine PostgreSQL for both Workspace and Research. Everything under test goes through
the Scientific Publication Studio's Outputs & Publishing routes with the signed-in person's own session; Research is
reached only server-side by the Studio. Prints statuses, counts and short hashes only; writes a JSON receipt.

    python -I sc_pub_e2e01_staging_harness.py     (see the staging runner)
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/h")
import pubm1_harness as pm  # noqa: E402  (Person: SC Identity sign-in and step-up)
import sc_model01_workspace_acceptance as acc  # noqa: E402  (synthetic study builder)
import public_sweep as sw  # noqa: E402  (anonymous sweep of every public route)

STUDIO = os.environ.get("E2E_STUDIO", "http://pub-studio:8089")
ORIGIN = "https://workspace.sustainablecatalyst.com"  # the Studio's write Origin (CSRF); set by browsers, here by hand
PUB = "/v1/private-research/reporting-studio/publication"
PUBLIC = "http://research-api:8000/api/research/v1"
PRIVATE = "http://research-convergence:8000/api/research/v1"
TAG = acc.TAG
AREA = f"sc-pub-e2e01-{TAG}"
ARTICLE = f"sc-pub-e2e01-overview-{TAG}"
SIBLING_MARK = f"PRIVATE-SIBLING-{TAG}"
DIMS = ("scientific", "rights", "ownership", "publication")
DECIDERS = {"scientific": "sci", "rights": "rights", "publication": "pub", "ownership": "editor",
            "area-publication": "area"}
results = []


def rec(check, name, ok, detail=""):
    results.append({"check": check, "name": name, "pass": bool(ok), "detail": str(detail)[:240]})
    print(f"{'PASS' if ok else 'FAIL'} {check} {name} {str(detail)[:240]}", flush=True)


def studio(person, method, path, body=None, expect=200, origin=ORIGIN):
    headers = {"Cookie": f"sc_workspace_session={person.cookie}"} if person else {}
    if method != "GET" and origin:
        headers["Origin"] = origin
    return acc.http(method, STUDIO + PUB + path, body, headers, expect)


def status(person, method, path, body=None, origin=ORIGIN):
    headers = {"Cookie": f"sc_workspace_session={person.cookie}"} if person else {}
    if method != "GET" and origin:
        headers["Origin"] = origin
    code, raw, _ = acc.call(method, STUDIO + PUB + path, body, headers)
    data = json.loads(raw) if raw else {}
    if isinstance(data, dict) and "detail" not in data and "message" in data:
        data["detail"] = data["message"]  # the Workspace error handler flattens HTTPException detail
    return code, data


def public(path):
    code, raw, hdrs = acc.call("GET", PUBLIC + path)
    return code, (json.loads(raw) if raw else {}), hdrs


def main():
    out = Path("/state/out")
    out.mkdir(exist_ok=True)
    st = pm.idh.load_state()
    rx = {"Authorization": "Bearer " + acc.secret("convergence_token")}

    # 0. Gates ------------------------------------------------------------------------------------------------
    c, _ = status(None, "GET", "/projects/x/outputs")
    rec("G1", "Outputs & Publishing refuses anonymous callers", c == 401, c)
    people = {r: pm.Person(r, st) for r in ("owner", "editor", "sci", "rights", "pub", "area", "stranger")}
    owner, stranger = people["owner"], people["stranger"]
    rec("G2", "seven synthetic SC Identity accounts signed in (password + TOTP)", all(p.cookie for p in people.values()))

    # 1. Parent project, synthetic study, independent reproduction (seeding with existing helpers) ------------
    steps = {}
    study = acc.build_owner_study(owner, 1.5, 0.25, steps)
    ing = acc.http("POST", PRIVATE + "/convergence/workspace/execution-runs",
                   {"grant": acc.grant(owner, study["runId"])["grant"], "researchArea": AREA,
                    # The evidence lives in the article's own Research entry; binding adopts that entry.
                    "entrySlug": ARTICLE, "title": "Synthetic dose-response (SC-PUB-E2E-01)"}, rx)
    result = ing["objects"]["output:polyglot-result"]["id"]
    ds_sha = (study["dataset"].get("item") or study["dataset"])["artifactSha256"]
    jrun = acc.new_run(owner, "Julia OLS reproduction", acc.DS, acc.M_J, "workspace.polyglot.julia.quadratic-optimize")
    acc.run_job(owner, jrun, "workspace.polyglot.julia.quadratic-optimize",
                {"datasetInput": acc.dataset_input(1, ds_sha, acc.NORMAL_EQ)})
    rep = acc.http("POST", PRIVATE + "/convergence/workspace/reproductions",
                   {"originalObjectId": result, "grant": acc.grant(owner, jrun)["grant"], "relTol": 1e-8, "absTol": 1e-10}, rx)
    rec("S1", "synthetic study ingested privately and independently reproduced", rep["status"] == "reproduced", rep["status"])
    project = acc.PROJECT

    # 2. Two outputs of the same project: a public overview and a private report ------------------------------
    def save(title, markdown, kind, doc=None, doc_rev=0):
        rev = studio(owner, "GET", f"/projects/{project}/documents")["projectRevision"]
        body = {"title": title, "markdown": markdown, "publicationType": kind, "expectedProjectRevision": rev,
                "expectedDocumentRevision": doc_rev, **({"documentId": doc} if doc else {})}
        return studio(owner, "POST", f"/projects/{project}/documents", body, 201)["document"]

    overview_md = ("# Synthetic dose-response overview\n\n## Summary\n\nA synthetic dose-response fitted in R and "
                   "independently reproduced in Julia. Modelled synthetic values, not measurements.\n\n## Methods\n\n"
                   "Ordinary least squares on a byte-pinned dataset revision.\n")
    ov = save("Synthetic dose-response overview", overview_md, "overview")
    rpt = save("Private scientific report", f"# Private scientific report\n\n{SIBLING_MARK} unreleased findings.\n", "report")
    rec("P1", "two independent outputs saved as immutable Studio revisions",
        ov["revision"] == 1 and rpt["revision"] == 1 and ov["documentId"] != rpt["documentId"],
        ov["markdownSHA256"][:12])
    O = f"/projects/{project}/outputs/{ov['documentId']}"

    listing = studio(owner, "GET", f"/projects/{project}/outputs")
    rec("P2", "dashboard lists both outputs; Research configured; neither bound",
        listing["researchConfigured"] and len(listing["outputs"]) >= 2 and all(o["binding"] is None for o in listing["outputs"]))
    c, _ = status(stranger, "GET", f"/projects/{project}/outputs")
    rec("A1", "another signed-in person cannot see the project's outputs", c == 404, c)
    c, _ = status(owner, "POST", f"{O}/bind", {"areaSlug": AREA, "articleSlug": ARTICLE}, origin="https://evil.example")
    rec("A2", "a write from a foreign Origin is refused (CSRF)", c == 403, c)

    # 3. Bind (idempotent) -----------------------------------------------------------------------------------
    b1 = studio(owner, "POST", f"{O}/bind", {"areaSlug": AREA, "articleSlug": ARTICLE, "title": ov["title"]}, 201)
    b2 = studio(owner, "POST", f"{O}/bind", {"areaSlug": AREA, "articleSlug": ARTICLE}, 200)
    rec("B1", "output bound to a Research article in the owner's scope; re-binding is a no-op",
        b1["created"] and not b2["created"], b1["binding"]["articleSlug"])
    c, _ = status(stranger, "POST", f"{O}/bind", {"areaSlug": AREA, "articleSlug": ARTICLE})
    rec("B2", "another person cannot bind this project's output", c == 404, c)

    # 4. Exact revision with cited evidence (idempotent) ------------------------------------------------------
    push = {"studioRevision": 1, "publicationType": "report", "summary": "Synthetic acceptance only.",
            "references": [{"objectId": result, "role": "result", "caption": "OLS slope and intercept (synthetic)."}]}
    r1 = studio(owner, "POST", f"{O}/research-revisions", push, 201)
    r1b = studio(owner, "POST", f"{O}/research-revisions", push, 200)
    rec("R1", "exact Studio revision sent to Research once; repeat is a no-op",
        r1["created"] and r1["researchRevision"] == 1 and not r1b["created"] and r1b["researchRevision"] == 1,
        r1["documentSha256"][:12])
    view = studio(owner, "GET", f"/projects/{project}/outputs")
    mine = next(o for o in view["outputs"] if o["documentId"] == ov["documentId"])
    hs = mine["research"]["headStudioRevision"]
    rec("R2", "Research revision carries the Studio document id, revision and SHA-256",
        hs["documentId"] == ov["documentId"] and hs["revision"] == 1 and hs["documentSha256"] == ov["markdownSHA256"])

    # 5. Grants, then approvals of the cited evidence through the Studio --------------------------------------
    def give(who, role, proj=project):
        return owner("POST", "/v1/research-approvals/grants", {"granteeUserKey": people[who].user, "role": role,
                                                              "projectId": proj})["item"]
    grants = {d: give(DECIDERS[d], f"approver:{d}") for d in DIMS}
    grants["area-publication"] = give("area", "approver:area-publication", "*")

    def decide(approval_id, subject, who):
        person = people[who]
        person.step_up()
        return studio(person, "POST", f"/research-approvals/{approval_id}/decide",
                      {"decision": "approve", "note": "SC-PUB-E2E-01 synthetic", "expectedSubjectRef": subject})

    c, refused = status(owner, "POST", f"/projects/{project}/research-objects/{result}/release")
    rec("E0", "cited evidence is not released without signed approvals", c == 403, refused.get("detail"))
    obj = studio(owner, "GET", f"/projects/{project}/research-objects/{result}")["object"]
    for d in DIMS:
        req = studio(owner, "POST", f"/projects/{project}/research-objects/{result}/approval-requests", {"dimension": d}, 201)
        decide(req["item"]["approvalId"], obj["subjectRef"], DECIDERS[d])
        studio(owner, "POST", f"/projects/{project}/research-objects/{result}/approvals/attach",
               {"approvalId": req["item"]["approvalId"]})
    rel = studio(owner, "POST", f"/projects/{project}/research-objects/{result}/release")
    rec("E1", "four independent signed approvals recorded; Research released the evidence for citation",
        rel.get("visibility") == "public-approved", rel.get("visibility"))
    code, objs, _ = public("/objects")
    rec("E2", "released evidence is still invisible publicly (article and area unpublished)",
        code == 200 and not any(i.get("id") == result for i in objs.get("items", [])))

    # 6. Submit; article approvals; self-approval and outsider refusals -------------------------------------
    studio(owner, "POST", f"{O}/submit", {"researchRevision": 1})
    subject1 = next(r for r in studio(owner, "GET", f"/projects/{project}/outputs")["outputs"]
                    if r["documentId"] == ov["documentId"])["research"]["revisions"][0]["subjectRef"]
    reqs = {d: studio(owner, "POST", f"{O}/approval-requests", {"researchRevision": 1, "dimension": d}, 201)["item"]
            for d in DIMS}
    owner.step_up()
    c, body = status(owner, "POST", f"/research-approvals/{reqs['scientific']['approvalId']}/decide",
                     {"decision": "approve", "expectedSubjectRef": subject1})
    rec("V1", "the owner cannot approve their own request (self-approval)", c == 403, body.get("detail"))
    stranger.step_up()
    c, _ = status(stranger, "POST", f"/research-approvals/{reqs['rights']['approvalId']}/decide",
                  {"decision": "approve", "expectedSubjectRef": subject1})
    rec("V2", "a person without the grant cannot approve", c == 403, c)
    c, body = status(owner, "POST", f"{O}/publish", {"researchRevision": 1, "confirmArticleSlug": ARTICLE})
    rec("V3", "publication refused while approvals are missing (Research's rule, reported as is)", c in (403, 409), body.get("detail"))
    for d in DIMS:
        decide(reqs[d]["approvalId"], subject1, DECIDERS[d])
        studio(owner, "POST", f"{O}/approvals/attach", {"researchRevision": 1, "approvalId": reqs[d]["approvalId"]})
    # Area: a signed area-publication approval by the area approver, then the steward (owner) publishes it.
    area_view = studio(owner, "GET", f"{O}/area")["area"]
    areq = studio(owner, "POST", f"{O}/area/approval-requests", {}, 201)["item"]
    decide(areq["approvalId"], area_view["subjectRef"], "area")
    c, _ = status(owner, "POST", f"{O}/area/publish", {"approvalId": areq["approvalId"], "confirmAreaSlug": "wrong"})
    rec("V4", "area publication needs typed confirmation", c == 422, c)
    ap = studio(owner, "POST", f"{O}/area/publish", {"approvalId": areq["approvalId"], "confirmAreaSlug": AREA})
    rec("V5", "Research area published with a signed area-publication record", ap.get("visibility") in ("approved", "public-approved"))

    # 7. Publish revision 1 -----------------------------------------------------------------------------------
    c, _ = status(owner, "POST", f"{O}/publish", {"researchRevision": 1, "confirmArticleSlug": "nope"})
    rec("U0", "public release needs typed confirmation", c == 422, c)
    p1 = studio(owner, "POST", f"{O}/publish", {"researchRevision": 1, "confirmArticleSlug": ARTICLE})
    receipt1 = p1.get("receipt") or {}
    rec("U1", "approved revision published; Research issued a release receipt",
        p1.get("publishedRevision") == 1 and receipt1.get("schema") == "sc-research-release-receipt/1.0",
        str(receipt1.get("eventSha256"))[:16])
    code, art, hdrs = public(f"/articles/{ARTICLE}/content")
    rec("U2", "public reader serves revision 1 of the article", code == 200 and art.get("revision") == 1 and art.get("listed") is True)
    code, lst, _ = public("/articles")
    code_q, found, _ = public("/articles?q=dose-response")
    rec("U3", "public listing and search reflect the release",
        any(a["slug"] == ARTICLE for a in lst.get("items", [])) and any(a["slug"] == ARTICLE for a in found.get("items", [])))
    mine = next(o for o in studio(owner, "GET", f"/projects/{project}/outputs")["outputs"] if o["documentId"] == ov["documentId"])
    rec("U4", "dashboard shows Research-confirmed state and public URL",
        mine["research"]["publicationStatus"] == "published" and mine["research"]["publicUrl"].endswith("article=" + ARTICLE)
        and mine["controls"]["unlist"] and mine["controls"]["withdraw"])
    sibling = next(o for o in studio(owner, "GET", f"/projects/{project}/outputs")["outputs"] if o["documentId"] == rpt["documentId"])
    rec("U5", "the sibling report stays private and unbound", sibling["binding"] is None and sibling["research"] is None)

    # 8. Reviewed update: revision 2 publishes without changing revision 1 -------------------------------------
    ov2 = save(ov["title"], overview_md + "\n## Limitations\n\nSynthetic values; no field observation.\n", "overview",
               ov["documentId"], 1)
    r2 = studio(owner, "POST", f"{O}/research-revisions", {**push, "studioRevision": 2}, 201)
    studio(owner, "POST", f"{O}/submit", {"researchRevision": 2})
    revs = next(o for o in studio(owner, "GET", f"/projects/{project}/outputs")["outputs"]
                if o["documentId"] == ov["documentId"])["research"]["revisions"]
    subject2 = revs[1]["subjectRef"]
    code, still, _ = public(f"/articles/{ARTICLE}/content")
    rec("W1", "while revision 2 is in review the public page still serves revision 1", still.get("revision") == 1)
    for d in DIMS:
        req = studio(owner, "POST", f"{O}/approval-requests", {"researchRevision": 2, "dimension": d}, 201)["item"]
        decide(req["approvalId"], subject2, DECIDERS[d])
        studio(owner, "POST", f"{O}/approvals/attach", {"researchRevision": 2, "approvalId": req["approvalId"]})
    p2 = studio(owner, "POST", f"{O}/publish", {"researchRevision": 2, "confirmArticleSlug": ARTICLE})
    code, art2, _ = public(f"/articles/{ARTICLE}/content")
    revs_after = next(o for o in studio(owner, "GET", f"/projects/{project}/outputs")["outputs"]
                      if o["documentId"] == ov["documentId"])["research"]["revisions"]
    rec("W2", "reviewed update published as revision 2; revision 1's document hash unchanged",
        p2.get("publishedRevision") == 2 and art2.get("revision") == 2 and ov2["revision"] == 2
        and revs_after[0]["documentSha256"] == revs[0]["documentSha256"], r2["documentSha256"][:12])

    # 9. Unlist, relist, withdraw ---------------------------------------------------------------------------
    studio(owner, "POST", f"{O}/unlist", {"reason": "SC-PUB-E2E-01 unlist drill"})
    code, direct, hdrs = public(f"/articles/{ARTICLE}/content")
    _, lst, _ = public("/articles")
    rec("L1", "unlisted: reachable by link (noindex), absent from listing",
        code == 200 and direct.get("listed") is False and (hdrs.get("X-Robots-Tag") or "") == "noindex"
        and not any(a["slug"] == ARTICLE for a in lst.get("items", [])))
    studio(owner, "POST", f"{O}/relist", {"reason": "SC-PUB-E2E-01 relist drill"})
    _, lst, _ = public("/articles")
    rec("L2", "relisted: back in the listing", any(a["slug"] == ARTICLE for a in lst.get("items", [])))
    c, _ = status(owner, "POST", f"{O}/withdraw", {"reason": "drill", "publicNotice": "Withdrawn.", "confirmArticleSlug": "x"})
    rec("L3", "withdrawal needs typed confirmation", c == 422, c)
    studio(owner, "POST", f"{O}/withdraw", {"reason": "SC-PUB-E2E-01 withdrawal drill",
                                            "publicNotice": "Withdrawn after a synthetic acceptance drill.",
                                            "confirmArticleSlug": ARTICLE})
    code, tomb, _ = public(f"/articles/{ARTICLE}/content")
    _, lst, _ = public("/articles")
    _, found, _ = public("/articles?q=dose-response")
    rec("L4", "withdrawn: 410 tombstone without content; gone from listing and search",
        code == 410 and tomb.get("status") == "withdrawn" and "sections" not in tomb
        and not any(a["slug"] == ARTICLE for a in lst.get("items", []) + found.get("items", [])))
    mine = next(o for o in studio(owner, "GET", f"/projects/{project}/outputs")["outputs"] if o["documentId"] == ov["documentId"])
    rec("L5", "after withdrawal every release control is disabled",
        mine["research"]["publicationStatus"] == "withdrawn"
        and not any(mine["controls"][k] for k in ("publish", "unlist", "relist", "withdraw", "pushRevision")))
    receipts = studio(owner, "GET", f"{O}/receipts")
    actions = [r.get("action") for r in receipts["research"]]
    rec("L6", "Research holds verifiable receipts for each release action",
        {"article-published", "article-unlisted", "article-relisted", "article-withdrawn"} <= set(actions), actions)

    # 10. Revocation, sign-out, leakage --------------------------------------------------------------------
    owner("POST", f"/v1/research-approvals/grants/{grants['rights']['grantId']}/revoke")
    req = studio(owner, "POST", f"/projects/{project}/research-objects/{result}/approval-requests", {"dimension": "rights"}, 201)
    people["rights"].step_up()
    c, _ = status(people["rights"], "POST", f"/research-approvals/{req['item']['approvalId']}/decide",
                  {"decision": "approve", "expectedSubjectRef": obj["subjectRef"]})
    rec("X1", "a revoked approver grant stops approvals immediately", c == 403, c)
    old = stranger.cookie
    code_lo, _, _ = acc.call("POST", pm.PUBWS + "/v1/auth/logout", {}, {"Cookie": f"sc_workspace_session={old}",
                                                                    "Origin": pm.PUBWS})
    c, _ = status(stranger, "GET", f"/projects/{project}/outputs")
    rec("X2", "a signed-out (revoked) session gets nothing from Outputs & Publishing", code_lo == 200 and c == 401, (code_lo, c))
    markers = {"siblingText": SIBLING_MARK, "siblingDocument": rpt["documentId"], "ownerScope": owner.scope,
               "workspaceProject": project, "studioSha": ov["markdownSHA256"]}
    rows = sw.sweep(acc, PUBLIC, {"entry": ARTICLE, "area": AREA, "objects": [result], "term": "dose"}, markers)
    leaks = sw.leaks(rows)
    rec("X3", "anonymous sweep of every public Research route: no private sibling, owner, project or source hash",
        rows and not leaks, {"requests": len(rows), "leaks": leaks[:3]})

    passed = sum(r["pass"] for r in results)
    receipt = {"schema": "sc-pub-e2e01-staging-acceptance/1.0", "tag": TAG,
               "studioImage": os.environ.get("STUDIO_IMAGE", ""), "researchImage": os.environ.get("RESEARCH_IMAGE", ""),
               "synthetic": True, "postgres": "genuine (Workspace and Research staging databases)",
               "passed": passed, "total": len(results), "results": results,
               "articleReceipts": [hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()[:16]
                                   for r in receipts["research"]]}
    (out / f"sc-pub-e2e01-{TAG}.json").write_text(json.dumps(receipt, indent=1))
    print(f"RESULT {passed}/{len(results)}", flush=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
