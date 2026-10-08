from __future__ import annotations
from typing import Any
from urllib.parse import urlparse

SCHEMA = "sc-workspace-library-research-object-bridge/1.0"
OBJECT_SCHEMA = "sc-workspace-library-reference/1.0"
VERSION = "3.83.0"
RELEASE = "Library Bridge + Public Surface Consolidation"
ALLOWED_KINDS = {"publication","document","archive-record","source","dataset","citation","collection","research-object","primary-source"}

def profile() -> dict[str, Any]:
    return {"schema":SCHEMA,"version":VERSION,"release":RELEASE,"mode":"reference-first","libraryAuthorityPreserved":True,"workspaceProjectAuthorityPreserved":True,"contentReplication":False,"automaticImport":False,"automaticProjectMutation":False,"automaticEvidenceRanking":False,"automaticTruthPromotion":False,"userAcceptanceRequired":True,"databaseMigrationRequired":False,"acceptedKinds":sorted(ALLOWED_KINDS)}

def _clean(value: Any, limit: int=1000) -> str:
    return str(value or "").strip()[:limit]

def _safe_url(value: Any) -> str:
    raw=_clean(value,2000)
    if not raw: return ""
    p=urlparse(raw)
    return raw if p.scheme in {"http","https"} else ""

def reference(*, library_id:str, kind:str="research-object", title:str="", citation:str="", canonical_url:str="", fingerprint:str="", revision:str="", source_authority:str="library", locator:str="", provenance_url:str="") -> dict[str,Any]:
    oid=_clean(library_id,240)
    if not oid: raise ValueError("library_id is required")
    k=_clean(kind,120) or "research-object"
    if k not in ALLOWED_KINDS: k="research-object"
    return {"schema":OBJECT_SCHEMA,"version":VERSION,"sourceProduct":"library","sourceAuthority":_clean(source_authority,120) or "library","libraryObjectId":oid,"kind":k,"title":_clean(title,500),"citation":_clean(citation,3000),"canonicalUrl":_safe_url(canonical_url),"provenanceUrl":_safe_url(provenance_url),"locator":_clean(locator,1000),"fingerprint":_clean(fingerprint,256),"revision":_clean(revision,240),"authoritative":False,"referenceOnly":True,"contentReplicated":False,"acceptedIntoProject":False,"mutationRequested":False}

def handoff_context(*, project_id:str="", return_url:str="", **kwargs:Any) -> dict[str,Any]:
    return {"schema":"sc-workspace-library-handoff-context/1.0","version":VERSION,"projectId":_clean(project_id,240),"returnUrl":_safe_url(return_url),"libraryReference":reference(**kwargs),"acceptanceRequired":True,"automaticImport":False,"automaticProjectMutation":False}
