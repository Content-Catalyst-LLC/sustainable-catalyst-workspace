"""Adapt an existing Workbench SVG handoff as a private Reporting Studio source.
The Workspace artifact store remains the persistence/ownership authority.
"""
import hashlib
from xml.etree import ElementTree as ET
from fastapi import HTTPException

SCHEMA = "sc-workbench-report-figure-handoff/1.0"
SVG_NS = "{http://www.w3.org/2000/svg}"
FORBIDDEN = {"script", "foreignObject", "iframe", "image", "use", "animate", "set", "animateMotion", "animateTransform"}

def adapt_workbench_handoff(obj):
    manifest = obj.get("manifest")
    svg = obj.get("svg")
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA or not isinstance(svg, str):
        raise HTTPException(422, "Unsupported Workbench handoff package.")
    source = manifest.get("source")
    destination = manifest.get("destination")
    figure = manifest.get("figure")
    if not all(isinstance(v, dict) for v in (source, destination, figure)):
        raise HTTPException(422, "Incomplete Workbench figure lineage.")
    if manifest.get("persistence") != "not-performed":
        raise HTTPException(422, "Expected an unpersisted Workbench handoff.")
    if not all(isinstance(source.get(k), str) and source[k] for k in ("projectId","graphId","graphObjectHash","renderHash","viewSpecSha256")):
        raise HTTPException(422, "Missing Workbench provenance.")
    if not isinstance(destination.get("reportId"), str) or not destination["reportId"]:
        raise HTTPException(422, "Missing destination report identity.")
    encoded = svg.encode("utf-8")
    if (hashlib.sha256(encoded).hexdigest() != manifest.get("svgSha256")
            or len(encoded) != manifest.get("svgBytes")):
        raise HTTPException(409, "Workbench SVG bytes failed SHA256 verification.")
    if len(encoded) > 1_000_000:
        raise HTTPException(413, "Workbench SVG is too large.")
    try:
        tree = ET.fromstring(svg)
    except ET.ParseError as exc:
        raise HTTPException(422, "Malformed Workbench SVG.") from exc
    if tree.tag != SVG_NS + "svg":
        raise HTTPException(422, "Expected SVG root.")
    for element in tree.iter():
        local = element.tag.rsplit("}", 1)[-1]
        if local in FORBIDDEN:
            raise HTTPException(422, "Active SVG elements are unsupported.")
        for key, value in element.attrib.items():
            attr = key.rsplit("}", 1)[-1].lower()
            if attr.startswith("on") or attr == "href" or "url(" in value.lower():
                raise HTTPException(422, "Active SVG references are unsupported.")
    return svg, {
        "owner_module": "workbench",
        "source_schema": SCHEMA,
        "source_identity": {"graph_id": source["graphId"], "graph_revision": source.get("graphRevision"),
            "graph_hash": source["graphObjectHash"], "render_hash": source["renderHash"],
            "view_spec_sha256": source["viewSpecSha256"], "svg_sha256": manifest["svgSha256"]},
        "source_provenance": {"workbench_project_id": source["projectId"],
            "research_session_id": source.get("researchSessionId"),
            "destination_report_id": destination["reportId"], "source_refs": figure.get("sourceRefs", []),
            "caption": figure.get("caption", ""), "figure_number": figure.get("figureNumber")},
        "scientific_status": "not-asserted",
        "uncertainty": "undeclared",
        "render_type": "workbench-graph",
        "source_fingerprint_verified": True,
        "projection": None,
    }
