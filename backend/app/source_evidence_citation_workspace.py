from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from . import investigation_source_integrity_workspace as source_integrity
from . import investigative_research_workspace as investigative

SCHEMA = "sc-workspace-source-evidence-citation/1.0"
CITATION_SCHEMA = "sc-workspace-citation-reference/1.0"

def profile() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": "3.75.0",
        "release": "Source, Evidence & Citation Workspace",
        "backendAuthoritative": True,
        "referenceFirst": True,
        "projectScoped": True,
        "sourceAuthority": "source-reliability-provenance-evidence-integrity-workspace",
        "evidenceAuthority": "claims-evidence-investigative-research-workspace",
        "derivedCitationReferences": True,
        "locatorPreserving": True,
        "fingerprintPinning": True,
        "provenancePreserved": True,
        "automaticEvidenceRanking": False,
        "automaticCredibilityScoring": False,
        "automaticTruthDetermination": False,
        "databaseMigrationRequired": False,
    }

def _citation(link: dict[str, Any], sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ref = str(link.get("evidenceRef") or link.get("targetRef") or "")
    source_id = str(link.get("sourceId") or "")
    if not source_id and ref.startswith("source:"):
        source_id = ref.split(":", 1)[1]
    if not source_id and ref.startswith("workspace:source:"):
        source_id = ref.split(":", 2)[2]
    source = sources.get(source_id) or {}
    return {
        "schema": CITATION_SCHEMA,
        "citationId": "citation:" + str(link.get("evidenceLinkId") or link.get("bindingId") or ref),
        "projectId": str(link.get("projectId") or ""),
        "sourceId": source_id,
        "statementId": str(link.get("statementId") or ""),
        "targetRef": ref,
        "relation": str(link.get("relation") or ""),
        "locator": link.get("locator") or link.get("locatorRef"),
        "sourceFingerprint": link.get("sourceFingerprint") or source.get("contentFingerprint"),
        "title": source.get("title"),
        "publisher": source.get("publisher"),
        "publishedAt": source.get("publishedAt"),
        "retrievedAt": source.get("retrievedAt"),
        "humanAsserted": bool(link.get("humanAsserted", True)),
        "derivedReference": True,
        "createdAt": link.get("createdAt"),
    }

def project_workspace(db: Session, user_key: str, project_id: str) -> dict[str, Any]:
    sources = source_integrity.list_sources(db, user_key, project_id, None, 5000)
    source_map = {str(x.get("sourceId")): x for x in sources}
    source_bindings = source_integrity.list_evidence_bindings(db, user_key, project_id, None, None, 10000)
    statements = investigative.list_statements(db, user_key, project_id, None, 5000)
    evidence_links = investigative.list_evidence_links(db, user_key, project_id, None, 10000)
    citations = [_citation(x, source_map) for x in evidence_links]
    citations.extend(_citation(x, source_map) for x in source_bindings)
    diagnostics = source_integrity.source_integrity_diagnostics(db, user_key, project_id)
    return {
        "schema": SCHEMA,
        "version": "3.75.0",
        "projectId": project_id,
        "sources": sources,
        "statements": statements,
        "evidenceLinks": evidence_links,
        "sourceEvidenceBindings": source_bindings,
        "citations": citations,
        "counts": {
            "sources": len(sources),
            "statements": len(statements),
            "evidenceLinks": len(evidence_links),
            "sourceEvidenceBindings": len(source_bindings),
            "citations": len(citations),
        },
        "diagnostics": diagnostics,
        "automaticEvidenceRanking": False,
        "automaticTruthDetermination": False,
    }
