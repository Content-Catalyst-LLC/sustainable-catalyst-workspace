"""UVR-01.3.9: real native private-report save/reopen with a synthetic Workbench figure."""
import hashlib
from copy import deepcopy
from fastapi import HTTPException
from test_research_reporting import setup, stage, save, url, REPORTING, ORIGIN
from app.reporting_workbench_bridge import adapt_workbench_handoff

SVG='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="550" viewBox="0 0 900 550"><polyline fill="none" stroke="#000" points="74,280 826,280"/></svg>'
def package(svg=SVG):
    raw=svg.encode()
    return {"manifest":{
        "schema":"sc-workbench-report-figure-handoff/1.0",
        "representation":"svg", "persistence":"not-performed",
        "source":{"projectId":"workbench-p","graphId":"graph-1","graphRevision":"revision-2",
            "graphObjectHash":"graph-hash","renderHash":"render-hash","viewSpecSha256":"view-sha"},
        "destination":{"adapter":"research-reporting-adapter-v1","projectId":"workbench-p","reportId":"report-1"},
        "figure":{"caption":"Synthetic identity graph","sourceRefs":["synthetic"]},
        "svgSha256":hashlib.sha256(raw).hexdigest(),"svgBytes":len(raw)}, "svg":svg}

def test_save_reopen_and_original_coordinates(setup):
    client,_,_,pid=setup
    ref,_=stage(setup,package())
    report=save(client,pid,ref)
    opened=client.get(url(pid,report))
    assert opened.status_code==200,opened.text
    view=opened.json()["view"]
    assert view["source"]["owner_module"]=="workbench"
    assert view["source"]["source_identity"]["graph_id"]=="graph-1"
    assert "74,280 826,280" in view["svg"]
    assert view["source"]["source_fingerprint_verified"] is True
    assert "Synthetic identity graph" == view["source"]["source_provenance"]["caption"]

def test_invalid_svg_digest_rejected_without_revision_write(setup):
    client,_,_,pid=setup
    invalid=package()
    invalid["svg"]=invalid["svg"].replace("826,280","826,100")
    ref,_=stage(setup,invalid)
    response=client.post(f"{REPORTING}/projects/{pid}/reports",json=ref,headers=ORIGIN)
    assert response.status_code==409,response.text

def test_active_svg_payload_rejected():
    for active in ['<script xmlns="http://www.w3.org/2000/svg"/>',
                   '<image xmlns="http://www.w3.org/2000/svg" href="https://bad.example/"/>']:
        svg=SVG.replace("</svg>",active+"</svg>")
        try:
            adapt_workbench_handoff(package(svg))
            assert False,"active SVG should be rejected"
        except HTTPException as exc:
            assert exc.status_code==422

def test_tampered_metadata_or_missing_lineage_rejected():
    obj=package()
    obj["manifest"]["source"]["renderHash"]=""
    try:
        adapt_workbench_handoff(obj)
        assert False
    except HTTPException as exc:
        assert exc.status_code==422
