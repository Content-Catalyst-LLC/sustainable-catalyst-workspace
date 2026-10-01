from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .multilingual_corpus_runtime import CorpusDocument


RUNTIME_SCHEMA = "sc-workspace-linguistic-annotation-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-linguistic-annotation-runtime-request/1.0"
RESULT_SCHEMA = "sc-workspace-linguistic-annotation-runtime-result/1.0"
ANNOTATION_SCHEMA = "sc-workspace-linguistic-annotation/1.0"
LAYER_SCHEMA = "sc-workspace-linguistic-annotation-layer/1.0"
STRUCTURE_NODE_SCHEMA = "sc-workspace-corpus-structure-node/1.0"
DOCUMENT_STRUCTURE_SCHEMA = "sc-workspace-document-structure/1.0"
CORPUS_STRUCTURE_SCHEMA = "sc-workspace-corpus-structure-profile/1.0"
ANNOTATION_LINEAGE_SCHEMA = "sc-workspace-linguistic-annotation-lineage/1.0"

OFFSET_UNIT = "unicode-code-point"
MAX_ANNOTATIONS = 20_000
MAX_LAYERS = 200
MAX_STRUCTURE_NODES = 20_000

OPERATIONS = (
    "workspace.linguistics.annotation-validate",
    "workspace.linguistics.annotation-span-index",
    "workspace.linguistics.annotation-layer-profile",
    "workspace.linguistics.document-structure",
    "workspace.linguistics.corpus-structure",
    "workspace.linguistics.annotation-lineage",
)

ANNOTATION_METHODS = {"human", "rule", "model", "imported", "other"}
STRUCTURE_NODE_TYPES = {"document", "section", "paragraph", "sentence", "token", "custom"}


class LinguisticAnnotation(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    annotation_id: str = Field(alias="annotationId", min_length=1, max_length=200)
    document_id: str = Field(alias="documentId", min_length=1, max_length=200)
    layer_id: str = Field(alias="layerId", min_length=1, max_length=200)
    annotation_type: str = Field(alias="annotationType", min_length=1, max_length=100)
    start_offset: int = Field(alias="startOffset", ge=0)
    end_offset: int = Field(alias="endOffset", ge=0)
    offset_unit: Literal["unicode-code-point"] = Field(default=OFFSET_UNIT, alias="offsetUnit")
    label: str | None = Field(default=None, max_length=300)
    value: Any = None
    features: dict[str, Any] = Field(default_factory=dict)
    method: Literal["human", "rule", "model", "imported", "other"] = "human"
    annotator: str | None = Field(default=None, max_length=300)
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)
    derived_from_annotation_ids: list[str] = Field(
        default_factory=list,
        alias="derivedFromAnnotationIds",
        max_length=100,
    )


class AnnotationLayer(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    layer_id: str = Field(alias="layerId", min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=300)
    annotation_type: str = Field(alias="annotationType", min_length=1, max_length=100)
    schema_ref: str | None = Field(default=None, alias="schemaRef", max_length=500)
    description: str | None = Field(default=None, max_length=2000)
    annotation_ids: list[str] = Field(default_factory=list, alias="annotationIds", max_length=MAX_ANNOTATIONS)


class CorpusStructureNode(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    node_id: str = Field(alias="nodeId", min_length=1, max_length=200)
    document_id: str = Field(alias="documentId", min_length=1, max_length=200)
    node_type: Literal["document", "section", "paragraph", "sentence", "token", "custom"] = Field(alias="nodeType")
    parent_id: str | None = Field(default=None, alias="parentId", max_length=200)
    order: int = Field(default=0, ge=0)
    start_offset: int = Field(alias="startOffset", ge=0)
    end_offset: int = Field(alias="endOffset", ge=0)
    offset_unit: Literal["unicode-code-point"] = Field(default=OFFSET_UNIT, alias="offsetUnit")
    label: str | None = Field(default=None, max_length=300)
    attributes: dict[str, Any] = Field(default_factory=dict)
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)


class LinguisticAnnotationRuntimeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_: str = Field(default=REQUEST_SCHEMA, alias="schema")
    operation: str
    documents: list[CorpusDocument] = Field(default_factory=list, max_length=100)
    layers: list[AnnotationLayer] = Field(default_factory=list, max_length=MAX_LAYERS)
    annotations: list[LinguisticAnnotation] = Field(default_factory=list, max_length=MAX_ANNOTATIONS)
    structure_nodes: list[CorpusStructureNode] = Field(
        default_factory=list,
        alias="structureNodes",
        max_length=MAX_STRUCTURE_NODES,
    )
    target_document_id: str | None = Field(default=None, alias="targetDocumentId", max_length=200)
    target_layer_id: str | None = Field(default=None, alias="targetLayerId", max_length=200)


def operation_catalog() -> list[dict[str, Any]]:
    outputs = (
        "sc-workspace-linguistic-annotation-validation/1.0",
        "sc-workspace-linguistic-annotation-span-index/1.0",
        "sc-workspace-linguistic-annotation-layer-profile/1.0",
        DOCUMENT_STRUCTURE_SCHEMA,
        CORPUS_STRUCTURE_SCHEMA,
        ANNOTATION_LINEAGE_SCHEMA,
    )
    return [
        {
            "operation": operation,
            "input": REQUEST_SCHEMA,
            "output": outputs[index],
            "bounded": True,
        }
        for index, operation in enumerate(OPERATIONS)
    ]


def profile() -> dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "version": "3.48.0",
        "title": "Linguistic Annotation & Corpus Structure Runtime",
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "offsetUnit": OFFSET_UNIT,
        "originalLanguageFirst": True,
        "automaticLanguageDetectionEnabled": False,
        "automaticTranslationEnabled": False,
        "arbitraryCodeExecution": False,
        "limits": {
            "maxAnnotations": MAX_ANNOTATIONS,
            "maxLayers": MAX_LAYERS,
            "maxStructureNodes": MAX_STRUCTURE_NODES,
        },
        "schemas": {
            "request": REQUEST_SCHEMA,
            "result": RESULT_SCHEMA,
            "annotation": ANNOTATION_SCHEMA,
            "layer": LAYER_SCHEMA,
            "structureNode": STRUCTURE_NODE_SCHEMA,
            "documentStructure": DOCUMENT_STRUCTURE_SCHEMA,
            "corpusStructure": CORPUS_STRUCTURE_SCHEMA,
            "annotationLineage": ANNOTATION_LINEAGE_SCHEMA,
        },
    }


def _documents(request: LinguisticAnnotationRuntimeRequest) -> dict[str, CorpusDocument]:
    docs = {}
    for document in request.documents:
        if document.document_id in docs:
            raise ValueError(f"duplicate documentId: {document.document_id}")
        docs[document.document_id] = document
    return docs


def _layers(request: LinguisticAnnotationRuntimeRequest) -> dict[str, AnnotationLayer]:
    layers = {}
    for layer in request.layers:
        if layer.layer_id in layers:
            raise ValueError(f"duplicate layerId: {layer.layer_id}")
        layers[layer.layer_id] = layer
    return layers


def _annotations(request: LinguisticAnnotationRuntimeRequest) -> dict[str, LinguisticAnnotation]:
    annotations = {}
    for annotation in request.annotations:
        if annotation.annotation_id in annotations:
            raise ValueError(f"duplicate annotationId: {annotation.annotation_id}")
        annotations[annotation.annotation_id] = annotation
    return annotations


def _structure_nodes(request: LinguisticAnnotationRuntimeRequest) -> dict[str, CorpusStructureNode]:
    nodes = {}
    for node in request.structure_nodes:
        if node.node_id in nodes:
            raise ValueError(f"duplicate nodeId: {node.node_id}")
        nodes[node.node_id] = node
    return nodes


def _validate(request: LinguisticAnnotationRuntimeRequest) -> dict[str, Any]:
    docs = _documents(request)
    layers = _layers(request)
    annotations = _annotations(request)
    nodes = _structure_nodes(request)

    issues: list[dict[str, Any]] = []

    for annotation in annotations.values():
        document = docs.get(annotation.document_id)
        if document is None:
            issues.append({"code": "annotation-document-missing", "annotationId": annotation.annotation_id})
            continue
        if annotation.layer_id not in layers:
            issues.append({"code": "annotation-layer-missing", "annotationId": annotation.annotation_id})
        if annotation.end_offset < annotation.start_offset:
            issues.append({"code": "annotation-offset-order", "annotationId": annotation.annotation_id})
        if annotation.end_offset > len(document.text):
            issues.append({
                "code": "annotation-offset-out-of-range",
                "annotationId": annotation.annotation_id,
                "documentLength": len(document.text),
            })
        for parent_id in annotation.derived_from_annotation_ids:
            if parent_id not in annotations:
                issues.append({
                    "code": "annotation-lineage-parent-missing",
                    "annotationId": annotation.annotation_id,
                    "parentAnnotationId": parent_id,
                })

    for layer in layers.values():
        for annotation_id in layer.annotation_ids:
            annotation = annotations.get(annotation_id)
            if annotation is None:
                issues.append({
                    "code": "layer-annotation-missing",
                    "layerId": layer.layer_id,
                    "annotationId": annotation_id,
                })
            elif annotation.layer_id != layer.layer_id:
                issues.append({
                    "code": "layer-annotation-mismatch",
                    "layerId": layer.layer_id,
                    "annotationId": annotation_id,
                })

    for node in nodes.values():
        document = docs.get(node.document_id)
        if document is None:
            issues.append({"code": "structure-document-missing", "nodeId": node.node_id})
            continue
        if node.end_offset < node.start_offset:
            issues.append({"code": "structure-offset-order", "nodeId": node.node_id})
        if node.end_offset > len(document.text):
            issues.append({
                "code": "structure-offset-out-of-range",
                "nodeId": node.node_id,
                "documentLength": len(document.text),
            })
        if node.parent_id:
            parent = nodes.get(node.parent_id)
            if parent is None:
                issues.append({"code": "structure-parent-missing", "nodeId": node.node_id, "parentId": node.parent_id})
            elif parent.document_id != node.document_id:
                issues.append({"code": "structure-parent-document-mismatch", "nodeId": node.node_id})
            elif not (parent.start_offset <= node.start_offset and node.end_offset <= parent.end_offset):
                issues.append({"code": "structure-parent-span-mismatch", "nodeId": node.node_id})

    for node in nodes.values():
        seen = {node.node_id}
        parent_id = node.parent_id
        while parent_id:
            if parent_id in seen:
                issues.append({"code": "structure-cycle", "nodeId": node.node_id})
                break
            seen.add(parent_id)
            parent = nodes.get(parent_id)
            parent_id = parent.parent_id if parent else None

    return {
        "schema": "sc-workspace-linguistic-annotation-validation/1.0",
        "valid": not issues,
        "issueCount": len(issues),
        "issues": issues,
        "documentCount": len(docs),
        "layerCount": len(layers),
        "annotationCount": len(annotations),
        "structureNodeCount": len(nodes),
        "offsetUnit": OFFSET_UNIT,
    }


def _require_valid(request: LinguisticAnnotationRuntimeRequest) -> dict[str, Any]:
    validation = _validate(request)
    if not validation["valid"]:
        raise ValueError(f"annotation request failed validation with {validation['issueCount']} issue(s)")
    return validation


def _span_index(request: LinguisticAnnotationRuntimeRequest) -> dict[str, Any]:
    _require_valid(request)
    docs = _documents(request)
    items = []
    for annotation in sorted(
        request.annotations,
        key=lambda item: (item.document_id, item.start_offset, item.end_offset, item.annotation_id),
    ):
        document = docs[annotation.document_id]
        items.append({
            "annotationId": annotation.annotation_id,
            "documentId": annotation.document_id,
            "layerId": annotation.layer_id,
            "annotationType": annotation.annotation_type,
            "startOffset": annotation.start_offset,
            "endOffset": annotation.end_offset,
            "offsetUnit": OFFSET_UNIT,
            "text": document.text[annotation.start_offset:annotation.end_offset],
            "label": annotation.label,
            "method": annotation.method,
            "confidence": annotation.confidence,
        })
    return {
        "schema": "sc-workspace-linguistic-annotation-span-index/1.0",
        "count": len(items),
        "items": items,
        "offsetUnit": OFFSET_UNIT,
    }


def _layer_profile(request: LinguisticAnnotationRuntimeRequest) -> dict[str, Any]:
    _require_valid(request)
    annotations_by_layer: dict[str, list[LinguisticAnnotation]] = defaultdict(list)
    for annotation in request.annotations:
        annotations_by_layer[annotation.layer_id].append(annotation)

    layers = []
    for layer in request.layers:
        annotations = annotations_by_layer.get(layer.layer_id, [])
        labels = Counter((annotation.label or "(unlabeled)") for annotation in annotations)
        methods = Counter(annotation.method for annotation in annotations)
        types = Counter(annotation.annotation_type for annotation in annotations)
        layers.append({
            "layerId": layer.layer_id,
            "title": layer.title,
            "annotationType": layer.annotation_type,
            "annotationCount": len(annotations),
            "labelDistribution": dict(sorted(labels.items())),
            "methodDistribution": dict(sorted(methods.items())),
            "typeDistribution": dict(sorted(types.items())),
        })

    return {
        "schema": "sc-workspace-linguistic-annotation-layer-profile/1.0",
        "layerCount": len(layers),
        "annotationCount": len(request.annotations),
        "layers": layers,
    }


def _document_structure(request: LinguisticAnnotationRuntimeRequest) -> dict[str, Any]:
    _require_valid(request)
    target = request.target_document_id
    if not target:
        raise ValueError("targetDocumentId is required for document-structure")
    docs = _documents(request)
    if target not in docs:
        raise ValueError(f"targetDocumentId is unavailable: {target}")

    nodes = [node for node in request.structure_nodes if node.document_id == target]
    by_parent: dict[str | None, list[CorpusStructureNode]] = defaultdict(list)
    for node in nodes:
        by_parent[node.parent_id].append(node)

    for values in by_parent.values():
        values.sort(key=lambda item: (item.order, item.start_offset, item.end_offset, item.node_id))

    def encode(node: CorpusStructureNode) -> dict[str, Any]:
        return {
            "nodeId": node.node_id,
            "documentId": node.document_id,
            "nodeType": node.node_type,
            "parentId": node.parent_id,
            "order": node.order,
            "startOffset": node.start_offset,
            "endOffset": node.end_offset,
            "offsetUnit": OFFSET_UNIT,
            "label": node.label,
            "attributes": node.attributes,
            "children": [encode(child) for child in by_parent.get(node.node_id, [])],
        }

    roots = [encode(node) for node in by_parent.get(None, [])]
    return {
        "schema": DOCUMENT_STRUCTURE_SCHEMA,
        "documentId": target,
        "languageTag": docs[target].language_tag,
        "nodeCount": len(nodes),
        "roots": roots,
        "offsetUnit": OFFSET_UNIT,
    }


def _corpus_structure(request: LinguisticAnnotationRuntimeRequest) -> dict[str, Any]:
    _require_valid(request)
    docs = _documents(request)
    node_type_counts = Counter(node.node_type for node in request.structure_nodes)
    nodes_by_document = Counter(node.document_id for node in request.structure_nodes)
    annotations_by_document = Counter(annotation.document_id for annotation in request.annotations)
    languages = Counter(document.language_tag for document in docs.values())
    representations = Counter(document.representation for document in docs.values())

    documents = []
    for document_id, document in sorted(docs.items()):
        documents.append({
            "documentId": document_id,
            "languageTag": document.language_tag,
            "representation": document.representation,
            "structureNodeCount": nodes_by_document.get(document_id, 0),
            "annotationCount": annotations_by_document.get(document_id, 0),
            "characterCount": len(document.text),
        })

    return {
        "schema": CORPUS_STRUCTURE_SCHEMA,
        "documentCount": len(docs),
        "structureNodeCount": len(request.structure_nodes),
        "annotationCount": len(request.annotations),
        "layerCount": len(request.layers),
        "nodeTypeDistribution": dict(sorted(node_type_counts.items())),
        "languageDistribution": dict(sorted(languages.items())),
        "representationDistribution": dict(sorted(representations.items())),
        "documents": documents,
        "originalLanguageFirst": True,
    }


def _annotation_lineage(request: LinguisticAnnotationRuntimeRequest) -> dict[str, Any]:
    _require_valid(request)
    edges = []
    roots = []
    derived = []

    for annotation in request.annotations:
        if annotation.derived_from_annotation_ids:
            derived.append(annotation.annotation_id)
            for parent_id in annotation.derived_from_annotation_ids:
                edges.append({
                    "fromAnnotationId": parent_id,
                    "toAnnotationId": annotation.annotation_id,
                    "relation": "derived-annotation",
                    "method": annotation.method,
                    "sourceRef": annotation.source_ref,
                })
        else:
            roots.append(annotation.annotation_id)

    return {
        "schema": ANNOTATION_LINEAGE_SCHEMA,
        "annotationCount": len(request.annotations),
        "rootAnnotationIds": sorted(roots),
        "derivedAnnotationIds": sorted(derived),
        "edgeCount": len(edges),
        "edges": edges,
        "provenancePreserved": True,
    }


_EXECUTORS = {
    OPERATIONS[0]: _validate,
    OPERATIONS[1]: _span_index,
    OPERATIONS[2]: _layer_profile,
    OPERATIONS[3]: _document_structure,
    OPERATIONS[4]: _corpus_structure,
    OPERATIONS[5]: _annotation_lineage,
}


def execute(request: LinguisticAnnotationRuntimeRequest) -> dict[str, Any]:
    if request.schema_ != REQUEST_SCHEMA:
        raise ValueError(f"schema must be {REQUEST_SCHEMA}")
    executor = _EXECUTORS.get(request.operation)
    if executor is None:
        raise ValueError(f"unsupported bounded operation: {request.operation}")

    result = executor(request)
    return {
        "schema": RESULT_SCHEMA,
        "version": "3.48.0",
        "operation": request.operation,
        "result": result,
        "policy": {
            "originalLanguageFirst": True,
            "offsetUnit": OFFSET_UNIT,
            "automaticLanguageDetectionEnabled": False,
            "automaticTranslationEnabled": False,
            "arbitraryCodeExecution": False,
        },
    }
