(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
    return;
  }
  root.SCWorkspaceTranslationTransliterationParallelAlignmentFactory = api;
  root.SCWorkspaceTranslationTransliterationParallelAlignment = api.create({
    apiClient: root.SCWorkspaceDecoupledApiClient || null,
    originalLanguageWorkspace: root.SCWorkspaceOriginalLanguageCorpusWorkspace || null,
    annotationWorkspace: root.SCWorkspaceLinguisticAnnotationCorpusStructureWorkspace || null
  });
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-translation-transliteration-parallel-alignment-workspace/1.0';
  const VERSION = '3.49.0';
  const TRANSFORMATION_SCHEMA = 'sc-workspace-language-transformation/1.0';
  const SEGMENT_SCHEMA = 'sc-workspace-parallel-text-segment/1.0';
  const ALIGNMENT_SCHEMA = 'sc-workspace-parallel-alignment-group/1.0';
  const PARALLEL_SET_SCHEMA = 'sc-workspace-parallel-text-set/1.0';
  const REQUEST_SCHEMA = 'sc-workspace-translation-alignment-runtime-request/1.0';

  const PROFILE_PATH = '/v1/translation-transliteration-parallel-alignment-workspace';
  const EXECUTE_PATH = '/v1/translation-alignment-runtime/execute';

  const OPERATIONS = Object.freeze({
    validateTransformations: 'workspace.linguistics.transformation-validate',
    validateAlignments: 'workspace.linguistics.parallel-alignment-validate',
    parallelIndex: 'workspace.linguistics.parallel-segment-index',
    alignmentProfile: 'workspace.linguistics.parallel-alignment-profile',
    coverage: 'workspace.linguistics.parallel-alignment-coverage',
    lineage: 'workspace.linguistics.translation-alignment-lineage'
  });

  const TRANSFORMATION_TYPES = Object.freeze(['translation', 'transliteration']);
  const METHODS = Object.freeze(['human', 'rule', 'model', 'imported', 'other']);
  const RELATIONS = Object.freeze(['1:1', '1:n', 'n:1', 'n:m']);

  function clean(value) { return String(value == null ? '' : value).trim(); }
  function objectId(prefix) {
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }
  function languageTag(value, name) {
    const tag = clean(value);
    if (!/^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$/.test(tag)) {
      throw new Error(`${name || 'languageTag'} must be explicit`);
    }
    return tag;
  }
  function script(value) {
    const v = clean(value);
    if (!v) return null;
    if (!/^[A-Za-z]{4}$/.test(v)) throw new Error('script must be a four-letter ISO 15924-like code');
    return v;
  }
  function confidence(value) {
    if (value === undefined || value === null) return null;
    const n = Number(value);
    if (!Number.isFinite(n) || n < 0 || n > 1) throw new Error('confidence must be between 0 and 1');
    return n;
  }
  function uniqueIds(values, name) {
    const ids = Array.isArray(values) ? values.map(clean).filter(Boolean) : [];
    if (!ids.length) throw new Error(`${name} requires at least one ID`);
    if (new Set(ids).size !== ids.length) throw new Error(`${name} IDs must be unique`);
    return Object.freeze(ids);
  }

  function createTransformation(input) {
    const source = input && typeof input === 'object' ? input : {};
    const transformationType = clean(source.transformationType).toLowerCase();
    const method = clean(source.method || 'human').toLowerCase();
    const sourceTextId = clean(source.sourceTextId);
    const derivedTextId = clean(source.derivedTextId);
    const sourceLanguageTag = languageTag(source.sourceLanguageTag, 'sourceLanguageTag');
    const targetLanguageTag = languageTag(source.targetLanguageTag, 'targetLanguageTag');

    if (!TRANSFORMATION_TYPES.includes(transformationType)) {
      throw new Error('transformationType must be translation or transliteration');
    }
    if (!METHODS.includes(method)) throw new Error('transformation method is unsupported');
    if (!sourceTextId || !derivedTextId) throw new Error('sourceTextId and derivedTextId are required');
    if (sourceTextId === derivedTextId) throw new Error('derived text cannot be its own source');
    if (transformationType === 'transliteration' && sourceLanguageTag !== targetLanguageTag) {
      throw new Error('transliteration must preserve language identity');
    }

    return Object.freeze({
      schema: TRANSFORMATION_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('transform'),
      transformationType,
      sourceTextId,
      derivedTextId,
      sourceLanguageTag,
      targetLanguageTag,
      sourceScript: script(source.sourceScript),
      targetScript: script(source.targetScript),
      method,
      agent: clean(source.agent) || null,
      confidence: confidence(source.confidence),
      sourceRef: clean(source.sourceRef) || null,
      createdAt: clean(source.createdAt) || new Date().toISOString(),
      originalLanguageRemainsCanonical: true,
      automaticTransformationApplied: false
    });
  }

  function createParallelSegment(input) {
    const source = input && typeof input === 'object' ? input : {};
    const textId = clean(source.textId);
    if (!textId) throw new Error('parallel segment textId is required');
    return Object.freeze({
      schema: SEGMENT_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('segment'),
      textId,
      languageTag: languageTag(source.languageTag),
      script: script(source.script),
      ordinal: Number.isInteger(Number(source.ordinal)) && Number(source.ordinal) >= 0 ? Number(source.ordinal) : 0,
      text: String(source.text == null ? '' : source.text),
      sourceRef: clean(source.sourceRef) || null
    });
  }

  function createAlignmentGroup(input) {
    const source = input && typeof input === 'object' ? input : {};
    const sourceSegmentIds = uniqueIds(source.sourceSegmentIds, 'sourceSegmentIds');
    const targetSegmentIds = uniqueIds(source.targetSegmentIds, 'targetSegmentIds');
    const relation = clean(source.relation || (
      sourceSegmentIds.length === 1 && targetSegmentIds.length === 1 ? '1:1'
      : sourceSegmentIds.length === 1 ? '1:n'
      : targetSegmentIds.length === 1 ? 'n:1'
      : 'n:m'
    ));
    if (!RELATIONS.includes(relation)) throw new Error('parallel alignment relation is unsupported');

    return Object.freeze({
      schema: ALIGNMENT_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('alignment'),
      sourceSegmentIds,
      targetSegmentIds,
      relation,
      method: METHODS.includes(clean(source.method || 'human').toLowerCase())
        ? clean(source.method || 'human').toLowerCase() : 'other',
      confidence: confidence(source.confidence),
      sourceRef: clean(source.sourceRef) || null,
      notes: clean(source.notes) || null
    });
  }

  function createParallelTextSet(input) {
    const source = input && typeof input === 'object' ? input : {};
    const segments = Array.isArray(source.segments) ? source.segments : [];
    const transformations = Array.isArray(source.transformations) ? source.transformations : [];
    const alignments = Array.isArray(source.alignments) ? source.alignments : [];
    const ids = new Set();

    segments.forEach((segment) => {
      if (!segment || segment.schema !== SEGMENT_SCHEMA) throw new Error('parallel set segments must use the Workspace segment schema');
      if (ids.has(segment.id)) throw new Error('parallel segment IDs must be unique');
      ids.add(segment.id);
    });
    alignments.forEach((alignment) => {
      if (!alignment || alignment.schema !== ALIGNMENT_SCHEMA) throw new Error('parallel set alignments must use the Workspace alignment schema');
      [...alignment.sourceSegmentIds, ...alignment.targetSegmentIds].forEach((id) => {
        if (!ids.has(id)) throw new Error(`alignment references unavailable segment: ${id}`);
      });
    });

    return Object.freeze({
      schema: PARALLEL_SET_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('parallel-set'),
      title: clean(source.title) || 'Parallel text set',
      segments: Object.freeze([...segments]),
      transformations: Object.freeze([...transformations]),
      alignments: Object.freeze([...alignments]),
      originalLanguageFirst: true,
      automaticTranslationEnabled: false,
      automaticTransliterationEnabled: false,
      automaticAlignmentEnabled: false
    });
  }

  function backendTransformation(item) {
    if (!item || item.schema !== TRANSFORMATION_SCHEMA) throw new Error('Workspace transformation is required');
    return {
      transformationId: item.id, transformationType: item.transformationType,
      sourceTextId: item.sourceTextId, derivedTextId: item.derivedTextId,
      sourceLanguageTag: item.sourceLanguageTag, targetLanguageTag: item.targetLanguageTag,
      sourceScript: item.sourceScript, targetScript: item.targetScript,
      method: item.method, agent: item.agent, confidence: item.confidence,
      sourceRef: item.sourceRef, createdAt: item.createdAt
    };
  }
  function backendSegment(item) {
    if (!item || item.schema !== SEGMENT_SCHEMA) throw new Error('Workspace parallel segment is required');
    return {
      segmentId: item.id, textId: item.textId, languageTag: item.languageTag,
      script: item.script, ordinal: item.ordinal, text: item.text, sourceRef: item.sourceRef
    };
  }
  function backendAlignment(item) {
    if (!item || item.schema !== ALIGNMENT_SCHEMA) throw new Error('Workspace alignment group is required');
    return {
      alignmentId: item.id, sourceSegmentIds: [...item.sourceSegmentIds],
      targetSegmentIds: [...item.targetSegmentIds], relation: item.relation,
      method: item.method, confidence: item.confidence, sourceRef: item.sourceRef, notes: item.notes
    };
  }

  function buildRequest(operation, input) {
    if (!Object.values(OPERATIONS).includes(operation)) throw new Error('unsupported translation/alignment operation');
    const source = input && typeof input === 'object' ? input : {};
    return {
      schema: REQUEST_SCHEMA,
      operation,
      transformations: Array.isArray(source.transformations) ? source.transformations.map(backendTransformation) : [],
      segments: Array.isArray(source.segments) ? source.segments.map(backendSegment) : [],
      alignments: Array.isArray(source.alignments) ? source.alignments.map(backendAlignment) : []
    };
  }

  function create(options) {
    const source = options && typeof options === 'object' ? options : {};
    const apiClient = source.apiClient || null;

    async function execute(operation, input, requestOptions) {
      if (!apiClient || typeof apiClient.post !== 'function') {
        throw new Error('Translation/alignment Workspace requires the decoupled Workspace API client');
      }
      return apiClient.post(EXECUTE_PATH, buildRequest(operation, input), requestOptions);
    }
    async function profile(requestOptions) {
      if (!apiClient || typeof apiClient.get !== 'function') {
        throw new Error('Translation/alignment Workspace requires the decoupled Workspace API client');
      }
      return apiClient.get(PROFILE_PATH, requestOptions);
    }

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      title: 'Translation, Transliteration & Parallel Alignment Workspace',
      operations: OPERATIONS,
      createTransformation, createParallelSegment, createAlignmentGroup, createParallelTextSet,
      buildRequest, execute, profile,
      validateTransformations(input, options) { return execute(OPERATIONS.validateTransformations, input, options); },
      validateAlignments(input, options) { return execute(OPERATIONS.validateAlignments, input, options); },
      parallelSegmentIndex(input, options) { return execute(OPERATIONS.parallelIndex, input, options); },
      alignmentProfile(input, options) { return execute(OPERATIONS.alignmentProfile, input, options); },
      alignmentCoverage(input, options) { return execute(OPERATIONS.coverage, input, options); },
      lineage(input, options) { return execute(OPERATIONS.lineage, input, options); },
      inspect() {
        return Object.freeze({
          schema: 'sc-workspace-translation-transliteration-parallel-alignment-state/1.0',
          version: VERSION,
          originalLanguageFirst: true,
          translationIsDerivedRepresentation: true,
          transliterationIsDerivedRepresentation: true,
          automaticLanguageDetectionEnabled: false,
          automaticTranslationEnabled: false,
          automaticTransliterationEnabled: false,
          automaticAlignmentEnabled: false,
          boundedBackendOperations: 6,
          wordpressRequired: false
        });
      }
    });
  }

  return Object.freeze({
    schema: SCHEMA, version: VERSION, operations: OPERATIONS,
    transformationTypes: TRANSFORMATION_TYPES, alignmentRelations: RELATIONS,
    create, createTransformation, createParallelSegment, createAlignmentGroup,
    createParallelTextSet, buildRequest
  });
});
