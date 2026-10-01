(function (root, factory) {
  'use strict';

  const api = factory();

  if (typeof module === 'object' && module.exports) {
    module.exports = api;
    return;
  }

  root.SCWorkspaceLinguisticAnnotationCorpusStructureWorkspaceFactory = api;
  root.SCWorkspaceLinguisticAnnotationCorpusStructureWorkspace = api.create({
    apiClient: root.SCWorkspaceDecoupledApiClient || null,
    originalLanguageWorkspace: root.SCWorkspaceOriginalLanguageCorpusWorkspace || null
  });
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-linguistic-annotation-corpus-structure-workspace/1.0';
  const VERSION = '3.48.0';
  const ANNOTATION_SCHEMA = 'sc-workspace-linguistic-annotation/1.0';
  const LAYER_SCHEMA = 'sc-workspace-linguistic-annotation-layer/1.0';
  const STRUCTURE_NODE_SCHEMA = 'sc-workspace-corpus-structure-node/1.0';
  const STRUCTURE_SCHEMA = 'sc-workspace-corpus-structure/1.0';
  const REQUEST_SCHEMA = 'sc-workspace-linguistic-annotation-runtime-request/1.0';
  const OFFSET_UNIT = 'unicode-code-point';

  const PROFILE_PATH = '/v1/linguistic-annotation-corpus-structure-workspace';
  const EXECUTE_PATH = '/v1/linguistic-annotation-runtime/execute';

  const OPERATIONS = Object.freeze({
    validateAnnotations: 'workspace.linguistics.annotation-validate',
    spanIndex: 'workspace.linguistics.annotation-span-index',
    layerProfile: 'workspace.linguistics.annotation-layer-profile',
    documentStructure: 'workspace.linguistics.document-structure',
    corpusStructure: 'workspace.linguistics.corpus-structure',
    annotationLineage: 'workspace.linguistics.annotation-lineage'
  });

  const ANNOTATION_METHODS = Object.freeze(['human', 'rule', 'model', 'imported', 'other']);
  const STRUCTURE_NODE_TYPES = Object.freeze(['document', 'section', 'paragraph', 'sentence', 'token', 'custom']);

  function clean(value) {
    return String(value == null ? '' : value).trim();
  }

  function objectId(prefix) {
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function codePointLength(text) {
    return Array.from(String(text == null ? '' : text)).length;
  }

  function finiteInteger(value, name, minimum) {
    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed < minimum) {
      throw new Error(`${name} must be an integer >= ${minimum}`);
    }
    return parsed;
  }

  function createAnnotation(input) {
    const source = input && typeof input === 'object' ? input : {};
    const documentId = clean(source.documentId);
    const layerId = clean(source.layerId);
    const annotationType = clean(source.annotationType);
    const startOffset = finiteInteger(source.startOffset, 'startOffset', 0);
    const endOffset = finiteInteger(source.endOffset, 'endOffset', 0);
    const method = clean(source.method || 'human').toLowerCase();

    if (!documentId) throw new Error('annotation documentId is required');
    if (!layerId) throw new Error('annotation layerId is required');
    if (!annotationType) throw new Error('annotationType is required');
    if (endOffset < startOffset) throw new Error('endOffset must be >= startOffset');
    if (!ANNOTATION_METHODS.includes(method)) throw new Error('annotation method is unsupported');

    let confidence = source.confidence;
    if (confidence !== undefined && confidence !== null) {
      confidence = Number(confidence);
      if (!Number.isFinite(confidence) || confidence < 0 || confidence > 1) {
        throw new Error('annotation confidence must be between 0 and 1');
      }
    } else {
      confidence = null;
    }

    const derivedFromAnnotationIds = Array.isArray(source.derivedFromAnnotationIds)
      ? source.derivedFromAnnotationIds.map(clean).filter(Boolean)
      : [];

    return Object.freeze({
      schema: ANNOTATION_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('annotation'),
      documentId,
      layerId,
      annotationType,
      startOffset,
      endOffset,
      offsetUnit: OFFSET_UNIT,
      label: clean(source.label) || null,
      value: source.value === undefined ? null : source.value,
      features: Object.freeze(Object.assign({}, source.features || {})),
      method,
      annotator: clean(source.annotator) || null,
      confidence,
      sourceRef: clean(source.sourceRef) || null,
      derivedFromAnnotationIds: Object.freeze(derivedFromAnnotationIds)
    });
  }

  function createAnnotationLayer(input) {
    const source = input && typeof input === 'object' ? input : {};
    const id = clean(source.id) || objectId('layer');
    const title = clean(source.title) || id;
    const annotationType = clean(source.annotationType);
    if (!annotationType) throw new Error('annotation layer annotationType is required');

    const annotations = Array.isArray(source.annotations)
      ? source.annotations.map((item) => {
          if (!item || item.schema !== ANNOTATION_SCHEMA) throw new Error('layer annotations must use the Workspace annotation schema');
          if (item.layerId !== id) throw new Error('annotation layerId must match its containing layer');
          return item;
        })
      : [];

    return Object.freeze({
      schema: LAYER_SCHEMA,
      version: VERSION,
      id,
      title,
      annotationType,
      schemaRef: clean(source.schemaRef) || null,
      description: clean(source.description) || null,
      annotations: Object.freeze(annotations),
      offsetUnit: OFFSET_UNIT,
      originalLanguageFirst: true
    });
  }

  function createStructureNode(input) {
    const source = input && typeof input === 'object' ? input : {};
    const documentId = clean(source.documentId);
    const nodeType = clean(source.nodeType).toLowerCase();
    const startOffset = finiteInteger(source.startOffset, 'startOffset', 0);
    const endOffset = finiteInteger(source.endOffset, 'endOffset', 0);
    const order = finiteInteger(source.order == null ? 0 : source.order, 'order', 0);

    if (!documentId) throw new Error('structure node documentId is required');
    if (!STRUCTURE_NODE_TYPES.includes(nodeType)) throw new Error('structure nodeType is unsupported');
    if (endOffset < startOffset) throw new Error('structure node endOffset must be >= startOffset');

    return Object.freeze({
      schema: STRUCTURE_NODE_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('structure'),
      documentId,
      nodeType,
      parentId: clean(source.parentId) || null,
      order,
      startOffset,
      endOffset,
      offsetUnit: OFFSET_UNIT,
      label: clean(source.label) || null,
      attributes: Object.freeze(Object.assign({}, source.attributes || {})),
      sourceRef: clean(source.sourceRef) || null
    });
  }

  function createCorpusStructure(input) {
    const source = input && typeof input === 'object' ? input : {};
    const nodes = Array.isArray(source.nodes) ? source.nodes : [];
    const ids = new Set();

    nodes.forEach((node) => {
      if (!node || node.schema !== STRUCTURE_NODE_SCHEMA) {
        throw new Error('corpus structure nodes must use the Workspace structure-node schema');
      }
      if (ids.has(node.id)) throw new Error('corpus structure node IDs must be unique');
      ids.add(node.id);
    });

    nodes.forEach((node) => {
      if (node.parentId && !ids.has(node.parentId)) {
        throw new Error(`structure node parentId is unavailable: ${node.parentId}`);
      }
    });

    return Object.freeze({
      schema: STRUCTURE_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('corpus-structure'),
      title: clean(source.title) || 'Corpus structure',
      nodes: Object.freeze([...nodes]),
      offsetUnit: OFFSET_UNIT,
      originalLanguageFirst: true
    });
  }

  function backendDocument(document) {
    if (!document || typeof document !== 'object') throw new Error('Workspace corpus document is required');
    const payload = {
      documentId: clean(document.id || document.documentId),
      text: String(document.text == null ? '' : document.text),
      languageTag: clean(document.languageTag),
      representation: clean(document.representation || 'original')
    };
    if (!payload.documentId) throw new Error('document ID is required');
    if (!payload.languageTag) throw new Error('document languageTag is required');
    if (document.script) payload.script = clean(document.script);
    if (document.derivedFromId) payload.derivedFromId = clean(document.derivedFromId);
    if (document.transformation) payload.transformation = clean(document.transformation);
    if (document.sourceRef) payload.sourceRef = clean(document.sourceRef);
    return payload;
  }

  function backendAnnotation(annotation) {
    if (!annotation || annotation.schema !== ANNOTATION_SCHEMA) throw new Error('Workspace annotation is required');
    return {
      annotationId: annotation.id,
      documentId: annotation.documentId,
      layerId: annotation.layerId,
      annotationType: annotation.annotationType,
      startOffset: annotation.startOffset,
      endOffset: annotation.endOffset,
      offsetUnit: OFFSET_UNIT,
      label: annotation.label,
      value: annotation.value,
      features: Object.assign({}, annotation.features || {}),
      method: annotation.method,
      annotator: annotation.annotator,
      confidence: annotation.confidence,
      sourceRef: annotation.sourceRef,
      derivedFromAnnotationIds: [...(annotation.derivedFromAnnotationIds || [])]
    };
  }

  function backendLayer(layer) {
    if (!layer || layer.schema !== LAYER_SCHEMA) throw new Error('Workspace annotation layer is required');
    return {
      layerId: layer.id,
      title: layer.title,
      annotationType: layer.annotationType,
      schemaRef: layer.schemaRef,
      description: layer.description,
      annotationIds: layer.annotations.map((annotation) => annotation.id)
    };
  }

  function backendNode(node) {
    if (!node || node.schema !== STRUCTURE_NODE_SCHEMA) throw new Error('Workspace structure node is required');
    return {
      nodeId: node.id,
      documentId: node.documentId,
      nodeType: node.nodeType,
      parentId: node.parentId,
      order: node.order,
      startOffset: node.startOffset,
      endOffset: node.endOffset,
      offsetUnit: OFFSET_UNIT,
      label: node.label,
      attributes: Object.assign({}, node.attributes || {}),
      sourceRef: node.sourceRef
    };
  }

  function buildRequest(operation, input) {
    if (!Object.values(OPERATIONS).includes(operation)) {
      throw new Error('unsupported linguistic annotation operation');
    }
    const source = input && typeof input === 'object' ? input : {};
    return {
      schema: REQUEST_SCHEMA,
      operation,
      documents: Array.isArray(source.documents) ? source.documents.map(backendDocument) : [],
      layers: Array.isArray(source.layers) ? source.layers.map(backendLayer) : [],
      annotations: Array.isArray(source.annotations) ? source.annotations.map(backendAnnotation) : [],
      structureNodes: Array.isArray(source.structureNodes) ? source.structureNodes.map(backendNode) : [],
      targetDocumentId: clean(source.targetDocumentId) || null,
      targetLayerId: clean(source.targetLayerId) || null
    };
  }

  function validateLocalOffsets(documents, annotations, structureNodes) {
    const lengths = new Map();
    (documents || []).forEach((document) => {
      const id = clean(document.id || document.documentId);
      lengths.set(id, codePointLength(document.text));
    });

    [...(annotations || []), ...(structureNodes || [])].forEach((item) => {
      const length = lengths.get(item.documentId);
      if (length === undefined) return;
      if (item.endOffset > length) {
        throw new Error(`${item.id} exceeds document Unicode code-point length`);
      }
    });

    return true;
  }

  function create(options) {
    const source = options && typeof options === 'object' ? options : {};
    const apiClient = source.apiClient || null;
    const originalLanguageWorkspace = source.originalLanguageWorkspace || null;

    async function execute(operation, input, requestOptions) {
      if (!apiClient || typeof apiClient.post !== 'function') {
        throw new Error('Linguistic annotation Workspace requires the decoupled Workspace API client');
      }
      const sourceInput = input && typeof input === 'object' ? input : {};
      validateLocalOffsets(sourceInput.documents, sourceInput.annotations, sourceInput.structureNodes);
      return apiClient.post(EXECUTE_PATH, buildRequest(operation, sourceInput), requestOptions);
    }

    async function profile(requestOptions) {
      if (!apiClient || typeof apiClient.get !== 'function') {
        throw new Error('Linguistic annotation Workspace requires the decoupled Workspace API client');
      }
      return apiClient.get(PROFILE_PATH, requestOptions);
    }

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      title: 'Linguistic Annotation & Corpus Structure Workspace',
      capabilities: Object.freeze([
        'workspace.linguistics.annotation',
        'workspace.linguistics.span-index',
        'workspace.linguistics.annotation-layers',
        'workspace.linguistics.document-structure',
        'workspace.linguistics.corpus-structure',
        'workspace.linguistics.annotation-lineage'
      ]),
      originalLanguageWorkspaceAvailable: Boolean(originalLanguageWorkspace),
      offsetUnit: OFFSET_UNIT,
      operations: OPERATIONS,
      createAnnotation,
      createAnnotationLayer,
      createStructureNode,
      createCorpusStructure,
      buildRequest,
      validateLocalOffsets,
      execute,
      profile,
      validateAnnotations(input, options) {
        return execute(OPERATIONS.validateAnnotations, input, options);
      },
      annotationSpanIndex(input, options) {
        return execute(OPERATIONS.spanIndex, input, options);
      },
      annotationLayerProfile(input, options) {
        return execute(OPERATIONS.layerProfile, input, options);
      },
      documentStructure(input, options) {
        return execute(OPERATIONS.documentStructure, input, options);
      },
      corpusStructure(input, options) {
        return execute(OPERATIONS.corpusStructure, input, options);
      },
      annotationLineage(input, options) {
        return execute(OPERATIONS.annotationLineage, input, options);
      },
      inspect() {
        return Object.freeze({
          schema: 'sc-workspace-linguistic-annotation-corpus-structure-state/1.0',
          version: VERSION,
          originalLanguageWorkspaceAvailable: Boolean(originalLanguageWorkspace),
          originalLanguageFirst: true,
          offsetUnit: OFFSET_UNIT,
          boundedBackendOperations: 6,
          automaticLanguageDetectionEnabled: false,
          automaticTranslationEnabled: false,
          wordpressRequired: false
        });
      }
    });
  }

  return Object.freeze({
    schema: SCHEMA,
    version: VERSION,
    offsetUnit: OFFSET_UNIT,
    operations: OPERATIONS,
    annotationMethods: ANNOTATION_METHODS,
    structureNodeTypes: STRUCTURE_NODE_TYPES,
    create,
    createAnnotation,
    createAnnotationLayer,
    createStructureNode,
    createCorpusStructure,
    buildRequest,
    codePointLength
  });
});
