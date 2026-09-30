import hashlib
import json
import re
import unicodedata
from collections import Counter
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

VERSION = "3.46.0"
RUNTIME_SCHEMA = "sc-workspace-multilingual-text-corpus-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-multilingual-text-corpus-runtime-request/1.0"
RESULT_SCHEMA = "sc-workspace-multilingual-text-corpus-runtime-result/1.0"
TEXT_IDENTITY_SCHEMA = "sc-workspace-multilingual-text-identity/1.0"
SEGMENT_SCHEMA = "sc-workspace-multilingual-text-segment/1.0"
CORPUS_PROFILE_SCHEMA = "sc-workspace-multilingual-corpus-profile/1.0"
TRANSFORMATION_PROVENANCE_SCHEMA = "sc-workspace-text-transformation-provenance/1.0"

MAX_TEXT_CHARS = 200_000
MAX_DOCUMENTS = 100
MAX_DOCUMENT_CHARS = 200_000
MAX_CORPUS_CHARS = 1_000_000
MAX_SEGMENTS = 10_000
MAX_SEGMENT_CHARS = 50_000

OPERATIONS = (
    "workspace.linguistics.text-identity",
    "workspace.linguistics.text-normalize",
    "workspace.linguistics.text-segment",
    "workspace.linguistics.corpus-profile",
    "workspace.linguistics.corpus-segment-index",
    "workspace.linguistics.corpus-lineage",
)

TRANSFORMATIONS = {
    "translation",
    "transliteration",
    "normalization",
    "transcription",
    "annotation",
    "ocr",
    "htr",
    "other",
}
NORMALIZATION_FORMS = {"none", "NFC", "NFD", "NFKC", "NFKD"}
SEGMENT_MODES = {"paragraph", "line", "simple-sentence"}
LANGUAGE_TAG_RE = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")
SCRIPT_RE = re.compile(r"^[A-Za-z]{4}$")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?。！？])\s+")


class CorpusDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    document_id: str = Field(alias="documentId", min_length=1, max_length=200)
    text: str = Field(min_length=0, max_length=MAX_DOCUMENT_CHARS)
    language_tag: str = Field(alias="languageTag", min_length=2, max_length=80)
    script: str | None = Field(default=None, min_length=4, max_length=4)
    representation: Literal["original", "derived"] = "original"
    derived_from_id: str | None = Field(default=None, alias="derivedFromId", max_length=200)
    transformation: str | None = Field(default=None, max_length=40)
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)


class MultilingualCorpusRuntimeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_: str = Field(default=REQUEST_SCHEMA, alias="schema")
    operation: str
    text: str | None = Field(default=None, max_length=MAX_TEXT_CHARS)
    language_tag: str | None = Field(default=None, alias="languageTag", max_length=80)
    script: str | None = Field(default=None, min_length=4, max_length=4)
    normalization_form: str = Field(default="NFC", alias="normalizationForm", max_length=8)
    segment_mode: str = Field(default="paragraph", alias="segmentMode", max_length=32)
    documents: list[CorpusDocument] = Field(default_factory=list, max_length=MAX_DOCUMENTS)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json_sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _language_tag(value: str | None) -> str:
    if not value or not LANGUAGE_TAG_RE.fullmatch(value.strip()):
        raise ValueError("languageTag must be an explicit BCP-47-like language tag; automatic language detection is disabled")
    parts = value.strip().split("-")
    normalized: list[str] = [parts[0].lower()]
    for part in parts[1:]:
        if len(part) == 4 and part.isalpha():
            normalized.append(part.title())
        elif len(part) in (2, 3) and part.isalnum():
            normalized.append(part.upper())
        else:
            normalized.append(part.lower())
    return "-".join(normalized)


def _script(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    value = value.strip()
    if not SCRIPT_RE.fullmatch(value):
        raise ValueError("script must be a four-letter ISO-15924-like script code")
    return value.title()


def _normalization_form(value: str) -> str:
    form = value.strip()
    if form.lower() == "none":
        return "none"
    form = form.upper()
    if form not in NORMALIZATION_FORMS:
        raise ValueError(f"normalizationForm must be one of {sorted(NORMALIZATION_FORMS)}")
    return form


def _segment_mode(value: str) -> str:
    mode = value.strip().lower()
    if mode not in SEGMENT_MODES:
        raise ValueError(f"segmentMode must be one of {sorted(SEGMENT_MODES)}")
    return mode


def _normalize_text(text: str, form: str) -> str:
    return text if form == "none" else unicodedata.normalize(form, text)


def _segments(text: str, mode: str) -> list[str]:
    if mode == "line":
        values = [line.strip() for line in text.splitlines() if line.strip()]
    elif mode == "paragraph":
        values = [part.strip() for part in re.split(r"\n\s*\n+", text) if part.strip()]
    else:
        values = [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]
    if len(values) > MAX_SEGMENTS:
        raise ValueError(f"segment count exceeds bounded maximum of {MAX_SEGMENTS}")
    if any(len(value) > MAX_SEGMENT_CHARS for value in values):
        raise ValueError(f"segment exceeds bounded maximum of {MAX_SEGMENT_CHARS} characters")
    return values


def _document_payload(document: CorpusDocument) -> dict[str, Any]:
    language_tag = _language_tag(document.language_tag)
    script = _script(document.script)
    return {
        "documentId": document.document_id,
        "languageTag": language_tag,
        "script": script,
        "representation": document.representation,
        "derivedFromId": document.derived_from_id,
        "transformation": document.transformation,
        "sourceRef": document.source_ref,
        "textSha256": _sha256_text(document.text),
        "characterCount": len(document.text),
    }


def _validated_documents(documents: list[CorpusDocument]) -> list[dict[str, Any]]:
    if not documents:
        raise ValueError("documents are required for corpus operations")
    total_chars = sum(len(document.text) for document in documents)
    if total_chars > MAX_CORPUS_CHARS:
        raise ValueError(f"corpus exceeds bounded maximum of {MAX_CORPUS_CHARS} characters")
    ids = [document.document_id for document in documents]
    if len(ids) != len(set(ids)):
        raise ValueError("documentId values must be unique within a corpus request")
    known = set(ids)
    payloads: list[dict[str, Any]] = []
    for document in documents:
        payload = _document_payload(document)
        if document.representation == "original":
            if document.derived_from_id or document.transformation:
                raise ValueError("original-language documents cannot declare derivedFromId or transformation")
        else:
            if not document.derived_from_id:
                raise ValueError("derived documents must declare derivedFromId")
            if document.derived_from_id == document.document_id:
                raise ValueError("derivedFromId cannot reference the document itself")
            if document.derived_from_id not in known:
                raise ValueError("derivedFromId must reference another document in the request")
            if not document.transformation or document.transformation not in TRANSFORMATIONS:
                raise ValueError(f"derived documents require transformation in {sorted(TRANSFORMATIONS)}")
        payloads.append(payload)

    parents = {p["documentId"]: p["derivedFromId"] for p in payloads if p["derivedFromId"]}
    for start in parents:
        seen: set[str] = set()
        cursor: str | None = start
        while cursor in parents:
            if cursor in seen:
                raise ValueError("derived-document lineage must be acyclic")
            seen.add(cursor)
            cursor = parents[cursor]
    return payloads


def operation_catalog() -> list[dict[str, Any]]:
    return [
        {"operation": OPERATIONS[0], "input": "explicit language-tagged text", "output": TEXT_IDENTITY_SCHEMA},
        {"operation": OPERATIONS[1], "input": "explicit language-tagged text", "output": TRANSFORMATION_PROVENANCE_SCHEMA},
        {"operation": OPERATIONS[2], "input": "explicit language-tagged text", "output": SEGMENT_SCHEMA},
        {"operation": OPERATIONS[3], "input": "bounded corpus documents", "output": CORPUS_PROFILE_SCHEMA},
        {"operation": OPERATIONS[4], "input": "bounded corpus documents", "output": SEGMENT_SCHEMA},
        {"operation": OPERATIONS[5], "input": "bounded original/derived corpus documents", "output": TRANSFORMATION_PROVENANCE_SCHEMA},
    ]


def profile() -> dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "version": VERSION,
        "title": "Multilingual Text & Corpus Runtime Foundation",
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "originalLanguageFirst": True,
        "translationIsDerivedRepresentation": True,
        "transliterationIsDerivedRepresentation": True,
        "automaticLanguageDetectionEnabled": False,
        "automaticTranslationEnabled": False,
        "automaticTransliterationEnabled": False,
        "externalNetworkAccessEnabled": False,
        "arbitraryCodeExecution": False,
        "clientSuppliedCodeAllowed": False,
        "sourceTextMutationEnabled": False,
        "languageMetadataRequired": True,
        "supportedNormalizationForms": sorted(NORMALIZATION_FORMS),
        "segmentModes": sorted(SEGMENT_MODES),
        "limits": {
            "maxTextChars": MAX_TEXT_CHARS,
            "maxDocuments": MAX_DOCUMENTS,
            "maxDocumentChars": MAX_DOCUMENT_CHARS,
            "maxCorpusChars": MAX_CORPUS_CHARS,
            "maxSegments": MAX_SEGMENTS,
        },
        "schemas": {
            "request": REQUEST_SCHEMA,
            "result": RESULT_SCHEMA,
            "textIdentity": TEXT_IDENTITY_SCHEMA,
            "segment": SEGMENT_SCHEMA,
            "corpusProfile": CORPUS_PROFILE_SCHEMA,
            "transformationProvenance": TRANSFORMATION_PROVENANCE_SCHEMA,
        },
    }


def _require_text(request: MultilingualCorpusRuntimeRequest) -> tuple[str, str, str | None, str]:
    if request.text is None:
        raise ValueError("text is required for text operations")
    language_tag = _language_tag(request.language_tag)
    script = _script(request.script)
    form = _normalization_form(request.normalization_form)
    return request.text, language_tag, script, form


def _text_identity(request: MultilingualCorpusRuntimeRequest) -> dict[str, Any]:
    text, language_tag, script, form = _require_text(request)
    normalized = _normalize_text(text, form)
    return {
        "schema": TEXT_IDENTITY_SCHEMA,
        "languageTag": language_tag,
        "script": script,
        "characterCount": len(text),
        "utf8ByteCount": len(text.encode("utf-8")),
        "sourceSha256": _sha256_text(text),
        "normalizationForm": form,
        "normalizedSha256": _sha256_text(normalized),
        "normalizationChangedText": normalized != text,
        "languageWasDetected": False,
    }


def _text_normalize(request: MultilingualCorpusRuntimeRequest) -> dict[str, Any]:
    text, language_tag, script, form = _require_text(request)
    normalized = _normalize_text(text, form)
    return {
        "schema": TRANSFORMATION_PROVENANCE_SCHEMA,
        "transformation": "normalization",
        "languageTag": language_tag,
        "script": script,
        "normalizationForm": form,
        "sourceSha256": _sha256_text(text),
        "resultSha256": _sha256_text(normalized),
        "changed": normalized != text,
        "resultText": normalized,
        "sourcePreserved": True,
        "derivedRepresentation": True,
    }


def _text_segment(request: MultilingualCorpusRuntimeRequest) -> dict[str, Any]:
    text, language_tag, script, form = _require_text(request)
    mode = _segment_mode(request.segment_mode)
    normalized = _normalize_text(text, form)
    segments = _segments(normalized, mode)
    return {
        "schema": SEGMENT_SCHEMA,
        "languageTag": language_tag,
        "script": script,
        "normalizationForm": form,
        "segmentMode": mode,
        "sourceSha256": _sha256_text(text),
        "normalizedSha256": _sha256_text(normalized),
        "segments": [
            {
                "segmentIndex": index,
                "segmentId": f"seg-{_sha256_text(f'{index}:{value}')[:20]}",
                "text": value,
                "textSha256": _sha256_text(value),
                "characterCount": len(value),
            }
            for index, value in enumerate(segments)
        ],
        "segmentCount": len(segments),
        "linguisticAnnotationApplied": False,
    }


def _corpus_profile(request: MultilingualCorpusRuntimeRequest) -> dict[str, Any]:
    payloads = _validated_documents(request.documents)
    language_counts = Counter(p["languageTag"] for p in payloads)
    script_counts = Counter((p["script"] or "undetermined") for p in payloads)
    representation_counts = Counter(p["representation"] for p in payloads)
    fingerprint_source = [
        {
            "documentId": p["documentId"],
            "textSha256": p["textSha256"],
            "languageTag": p["languageTag"],
            "script": p["script"],
            "representation": p["representation"],
            "derivedFromId": p["derivedFromId"],
            "transformation": p["transformation"],
        }
        for p in sorted(payloads, key=lambda value: value["documentId"])
    ]
    return {
        "schema": CORPUS_PROFILE_SCHEMA,
        "documentCount": len(payloads),
        "characterCount": sum(p["characterCount"] for p in payloads),
        "languageDistribution": dict(sorted(language_counts.items())),
        "scriptDistribution": dict(sorted(script_counts.items())),
        "representationDistribution": dict(sorted(representation_counts.items())),
        "originalDocumentCount": representation_counts.get("original", 0),
        "derivedDocumentCount": representation_counts.get("derived", 0),
        "corpusFingerprintSha256": _canonical_json_sha256(fingerprint_source),
        "documents": payloads,
        "automaticLanguageDetectionApplied": False,
    }


def _corpus_segment_index(request: MultilingualCorpusRuntimeRequest) -> dict[str, Any]:
    payloads = _validated_documents(request.documents)
    by_id = {document.document_id: document for document in request.documents}
    mode = _segment_mode(request.segment_mode)
    form = _normalization_form(request.normalization_form)
    items: list[dict[str, Any]] = []
    for payload in payloads:
        document = by_id[payload["documentId"]]
        normalized = _normalize_text(document.text, form)
        for index, value in enumerate(_segments(normalized, mode)):
            items.append({
                "schema": SEGMENT_SCHEMA,
                "segmentId": f"seg-{_sha256_text(f'{document.document_id}:{index}:{value}')[:20]}",
                "documentId": document.document_id,
                "segmentIndex": index,
                "languageTag": payload["languageTag"],
                "script": payload["script"],
                "representation": payload["representation"],
                "derivedFromId": payload["derivedFromId"],
                "transformation": payload["transformation"],
                "text": value,
                "textSha256": _sha256_text(value),
            })
            if len(items) > MAX_SEGMENTS:
                raise ValueError(f"corpus segment count exceeds bounded maximum of {MAX_SEGMENTS}")
    return {
        "schema": "sc-workspace-multilingual-corpus-segment-index/1.0",
        "segmentMode": mode,
        "normalizationForm": form,
        "segmentCount": len(items),
        "segments": items,
        "alignmentApplied": False,
        "annotationApplied": False,
    }


def _corpus_lineage(request: MultilingualCorpusRuntimeRequest) -> dict[str, Any]:
    payloads = _validated_documents(request.documents)
    ordered = sorted(payloads, key=lambda value: value["documentId"])
    nodes = [
        {
            "documentId": p["documentId"],
            "languageTag": p["languageTag"],
            "script": p["script"],
            "representation": p["representation"],
            "textSha256": p["textSha256"],
            "sourceRef": p["sourceRef"],
        }
        for p in ordered
    ]
    edges = [
        {
            "sourceDocumentId": p["derivedFromId"],
            "derivedDocumentId": p["documentId"],
            "transformation": p["transformation"],
            "derivedLanguageTag": p["languageTag"],
            "derivedScript": p["script"],
        }
        for p in ordered
        if p["representation"] == "derived"
    ]
    return {
        "schema": TRANSFORMATION_PROVENANCE_SCHEMA,
        "nodes": nodes,
        "edges": edges,
        "edgeCount": len(edges),
        "originalLanguageFirst": True,
        "translationIsDerivedRepresentation": True,
        "automaticTransformationApplied": False,
        "lineageFingerprintSha256": _canonical_json_sha256({"nodes": nodes, "edges": edges}),
    }


_EXECUTORS = {
    OPERATIONS[0]: _text_identity,
    OPERATIONS[1]: _text_normalize,
    OPERATIONS[2]: _text_segment,
    OPERATIONS[3]: _corpus_profile,
    OPERATIONS[4]: _corpus_segment_index,
    OPERATIONS[5]: _corpus_lineage,
}


def execute(request: MultilingualCorpusRuntimeRequest) -> dict[str, Any]:
    if request.schema_ != REQUEST_SCHEMA:
        raise ValueError(f"schema must be {REQUEST_SCHEMA}")
    executor = _EXECUTORS.get(request.operation)
    if executor is None:
        raise ValueError(f"unsupported bounded operation: {request.operation}")
    result = executor(request)
    return {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "operation": request.operation,
        "result": result,
        "guardrails": {
            "originalLanguageFirst": True,
            "automaticLanguageDetectionEnabled": False,
            "automaticTranslationEnabled": False,
            "arbitraryCodeExecution": False,
            "externalNetworkAccessEnabled": False,
        },
    }
