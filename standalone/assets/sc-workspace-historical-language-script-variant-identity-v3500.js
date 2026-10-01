(function (root, factory) {
  'use strict';

  const api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
    return;
  }

  root.SCWorkspaceHistoricalLanguageScriptVariantIdentityFactory = api;
  root.SCWorkspaceHistoricalLanguageScriptVariantIdentity = api.create({
    apiClient: root.SCWorkspaceDecoupledApiClient || null,
    originalLanguageWorkspace: root.SCWorkspaceOriginalLanguageCorpusWorkspace || null,
    annotationWorkspace: root.SCWorkspaceLinguisticAnnotationCorpusStructureWorkspace || null,
    alignmentWorkspace: root.SCWorkspaceTranslationTransliterationParallelAlignment || null
  });
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-historical-language-script-variant-identity-workspace/1.0';
  const VERSION = '3.50.0';
  const LANGUAGE_IDENTITY_SCHEMA = 'sc-workspace-historical-language-identity/1.0';
  const SCRIPT_IDENTITY_SCHEMA = 'sc-workspace-script-identity/1.0';
  const VARIANT_SCHEMA = 'sc-workspace-language-variant-identity/1.0';
  const RELATION_SCHEMA = 'sc-workspace-historical-language-identity-relation/1.0';
  const REQUEST_SCHEMA = 'sc-workspace-historical-language-identity-runtime-request/1.0';

  const PROFILE_PATH = '/v1/historical-language-script-variant-identity-workspace';
  const EXECUTE_PATH = '/v1/historical-language-identity-runtime/execute';

  const OPERATIONS = Object.freeze({
    validate: 'workspace.linguistics.historical-identity-validate',
    variantIndex: 'workspace.linguistics.historical-variant-index',
    temporalProfile: 'workspace.linguistics.historical-temporal-profile',
    scriptOrthographyProfile: 'workspace.linguistics.script-orthography-profile',
    relationshipGraph: 'workspace.linguistics.historical-relationship-graph',
    lineage: 'workspace.linguistics.historical-identity-lineage'
  });

  const LANGUAGE_KINDS = Object.freeze([
    'language', 'historical-stage', 'dialect', 'variety', 'register', 'mixed', 'other'
  ]);
  const VARIANT_KINDS = Object.freeze([
    'orthography', 'spelling', 'regional', 'historical', 'scribal', 'print', 'normalized', 'other'
  ]);
  const RELATION_TYPES = Object.freeze([
    'predecessor-of', 'successor-of', 'historical-stage-of', 'dialect-of', 'variety-of',
    'script-variant-of', 'orthographic-variant-of', 'normalized-form-of',
    'modernized-form-of', 'related-to'
  ]);
  const DIRECTIONS = Object.freeze(['ltr', 'rtl', 'ttb', 'btt', 'unknown']);

  function clean(value) {
    return String(value == null ? '' : value).trim();
  }

  function objectId(prefix) {
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function optionalLanguageTag(value) {
    const tag = clean(value);
    if (!tag) return null;
    if (!/^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$/.test(tag)) {
      throw new Error('languageTag must be explicit and BCP-47-like when supplied');
    }
    return tag;
  }

  function optionalScriptCode(value) {
    const code = clean(value);
    if (!code) return null;
    if (!/^[A-Za-z]{4}$/.test(code)) {
      throw new Error('scriptCode must be a four-letter ISO 15924-like code when supplied');
    }
    return code;
  }

  function stringList(value) {
    if (!Array.isArray(value)) return Object.freeze([]);
    return Object.freeze([...new Set(value.map(clean).filter(Boolean))]);
  }

  function externalIdentifiers(value) {
    const source = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
    const out = {};
    Object.keys(source).sort().forEach((key) => {
      const k = clean(key);
      const v = clean(source[key]);
      if (k && v) out[k] = v;
    });
    return Object.freeze(out);
  }

  function temporalScope(value) {
    const source = value && typeof value === 'object' ? value : {};
    const parseYear = (v, name) => {
      if (v === undefined || v === null || v === '') return null;
      const n = Number(v);
      if (!Number.isInteger(n)) throw new Error(`${name} must be a signed integer year`);
      return n;
    };
    const startYear = parseYear(source.startYear, 'startYear');
    const endYear = parseYear(source.endYear, 'endYear');
    if (startYear !== null && endYear !== null && endYear < startYear) {
      throw new Error('temporal scope endYear must be >= startYear');
    }
    return Object.freeze({
      startYear,
      endYear,
      chronologyLabel: clean(source.chronologyLabel) || null,
      approximate: source.approximate === true,
      uncertainty: clean(source.uncertainty) || null
    });
  }

  function confidence(value) {
    if (value === undefined || value === null) return null;
    const n = Number(value);
    if (!Number.isFinite(n) || n < 0 || n > 1) throw new Error('confidence must be between 0 and 1');
    return n;
  }

  function createLanguageIdentity(input) {
    const source = input && typeof input === 'object' ? input : {};
    const label = clean(source.label);
    const kind = clean(source.kind || 'language').toLowerCase();
    if (!label) throw new Error('historical language identity label is required');
    if (!LANGUAGE_KINDS.includes(kind)) throw new Error('historical language identity kind is unsupported');

    return Object.freeze({
      schema: LANGUAGE_IDENTITY_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('language'),
      label,
      kind,
      languageTag: optionalLanguageTag(source.languageTag),
      aliases: stringList(source.aliases),
      externalIdentifiers: externalIdentifiers(source.externalIdentifiers),
      scriptIds: stringList(source.scriptIds),
      regions: stringList(source.regions),
      temporalScope: temporalScope(source.temporalScope),
      parentIdentityId: clean(source.parentIdentityId) || null,
      sourceRef: clean(source.sourceRef) || null,
      notes: clean(source.notes) || null,
      originalHistoricalIdentityPreserved: true,
      automaticModernizationApplied: false
    });
  }

  function createScriptIdentity(input) {
    const source = input && typeof input === 'object' ? input : {};
    const label = clean(source.label);
    const direction = clean(source.direction || 'unknown').toLowerCase();
    if (!label) throw new Error('script identity label is required');
    if (!DIRECTIONS.includes(direction)) throw new Error('script direction is unsupported');

    return Object.freeze({
      schema: SCRIPT_IDENTITY_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('script'),
      label,
      scriptCode: optionalScriptCode(source.scriptCode),
      aliases: stringList(source.aliases),
      direction,
      parentScriptId: clean(source.parentScriptId) || null,
      regions: stringList(source.regions),
      temporalScope: temporalScope(source.temporalScope),
      externalIdentifiers: externalIdentifiers(source.externalIdentifiers),
      sourceRef: clean(source.sourceRef) || null,
      notes: clean(source.notes) || null
    });
  }

  function createVariantIdentity(input) {
    const source = input && typeof input === 'object' ? input : {};
    const label = clean(source.label);
    const kind = clean(source.kind || 'other').toLowerCase();
    const languageIdentityId = clean(source.languageIdentityId);
    if (!label) throw new Error('variant identity label is required');
    if (!languageIdentityId) throw new Error('variant languageIdentityId is required');
    if (!VARIANT_KINDS.includes(kind)) throw new Error('variant kind is unsupported');

    return Object.freeze({
      schema: VARIANT_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('variant'),
      label,
      kind,
      languageIdentityId,
      scriptIdentityId: clean(source.scriptIdentityId) || null,
      aliases: stringList(source.aliases),
      regions: stringList(source.regions),
      temporalScope: temporalScope(source.temporalScope),
      externalIdentifiers: externalIdentifiers(source.externalIdentifiers),
      sourceRef: clean(source.sourceRef) || null,
      notes: clean(source.notes) || null,
      normalizedVariant: kind === 'normalized',
      originalHistoricalIdentityPreserved: true
    });
  }

  function createIdentityRelation(input) {
    const source = input && typeof input === 'object' ? input : {};
    const fromId = clean(source.fromId);
    const toId = clean(source.toId);
    const relationType = clean(source.relationType).toLowerCase();

    if (!fromId || !toId) throw new Error('historical identity relation requires fromId and toId');
    if (fromId === toId) throw new Error('historical identity relation cannot be self-referential');
    if (!RELATION_TYPES.includes(relationType)) throw new Error('historical identity relationType is unsupported');

    return Object.freeze({
      schema: RELATION_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('relation'),
      fromId,
      toId,
      relationType,
      confidence: confidence(source.confidence),
      sourceRef: clean(source.sourceRef) || null,
      notes: clean(source.notes) || null
    });
  }

  function encodeLanguage(item) {
    if (!item || item.schema !== LANGUAGE_IDENTITY_SCHEMA) throw new Error('Workspace historical language identity is required');
    return {
      identityId: item.id,
      label: item.label,
      kind: item.kind,
      languageTag: item.languageTag,
      aliases: [...item.aliases],
      externalIdentifiers: Object.assign({}, item.externalIdentifiers),
      scriptIds: [...item.scriptIds],
      regions: [...item.regions],
      temporalScope: Object.assign({}, item.temporalScope),
      parentIdentityId: item.parentIdentityId,
      sourceRef: item.sourceRef,
      notes: item.notes
    };
  }

  function encodeScript(item) {
    if (!item || item.schema !== SCRIPT_IDENTITY_SCHEMA) throw new Error('Workspace script identity is required');
    return {
      scriptId: item.id,
      label: item.label,
      scriptCode: item.scriptCode,
      aliases: [...item.aliases],
      direction: item.direction,
      parentScriptId: item.parentScriptId,
      regions: [...item.regions],
      temporalScope: Object.assign({}, item.temporalScope),
      externalIdentifiers: Object.assign({}, item.externalIdentifiers),
      sourceRef: item.sourceRef,
      notes: item.notes
    };
  }

  function encodeVariant(item) {
    if (!item || item.schema !== VARIANT_SCHEMA) throw new Error('Workspace language variant identity is required');
    return {
      variantId: item.id,
      label: item.label,
      kind: item.kind,
      languageIdentityId: item.languageIdentityId,
      scriptIdentityId: item.scriptIdentityId,
      aliases: [...item.aliases],
      regions: [...item.regions],
      temporalScope: Object.assign({}, item.temporalScope),
      externalIdentifiers: Object.assign({}, item.externalIdentifiers),
      sourceRef: item.sourceRef,
      notes: item.notes
    };
  }

  function encodeRelation(item) {
    if (!item || item.schema !== RELATION_SCHEMA) throw new Error('Workspace historical identity relation is required');
    return {
      relationId: item.id,
      fromId: item.fromId,
      toId: item.toId,
      relationType: item.relationType,
      confidence: item.confidence,
      sourceRef: item.sourceRef,
      notes: item.notes
    };
  }

  function buildRequest(operation, input) {
    if (!Object.values(OPERATIONS).includes(operation)) throw new Error('unsupported historical identity operation');
    const source = input && typeof input === 'object' ? input : {};
    return {
      schema: REQUEST_SCHEMA,
      operation,
      languageIdentities: Array.isArray(source.languageIdentities) ? source.languageIdentities.map(encodeLanguage) : [],
      scriptIdentities: Array.isArray(source.scriptIdentities) ? source.scriptIdentities.map(encodeScript) : [],
      variants: Array.isArray(source.variants) ? source.variants.map(encodeVariant) : [],
      relations: Array.isArray(source.relations) ? source.relations.map(encodeRelation) : []
    };
  }

  function create(options) {
    const source = options && typeof options === 'object' ? options : {};
    const apiClient = source.apiClient || null;

    async function execute(operation, input, requestOptions) {
      if (!apiClient || typeof apiClient.post !== 'function') {
        throw new Error('Historical language identity Workspace requires the decoupled Workspace API client');
      }
      return apiClient.post(EXECUTE_PATH, buildRequest(operation, input), requestOptions);
    }

    async function profile(requestOptions) {
      if (!apiClient || typeof apiClient.get !== 'function') {
        throw new Error('Historical language identity Workspace requires the decoupled Workspace API client');
      }
      return apiClient.get(PROFILE_PATH, requestOptions);
    }

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      title: 'Historical Language, Script & Variant Identity Workspace',
      operations: OPERATIONS,
      createLanguageIdentity,
      createScriptIdentity,
      createVariantIdentity,
      createIdentityRelation,
      buildRequest,
      execute,
      profile,
      validate(input, options) { return execute(OPERATIONS.validate, input, options); },
      variantIndex(input, options) { return execute(OPERATIONS.variantIndex, input, options); },
      temporalProfile(input, options) { return execute(OPERATIONS.temporalProfile, input, options); },
      scriptOrthographyProfile(input, options) { return execute(OPERATIONS.scriptOrthographyProfile, input, options); },
      relationshipGraph(input, options) { return execute(OPERATIONS.relationshipGraph, input, options); },
      lineage(input, options) { return execute(OPERATIONS.lineage, input, options); },
      inspect() {
        return Object.freeze({
          schema: 'sc-workspace-historical-language-script-variant-identity-state/1.0',
          version: VERSION,
          originalLanguageFirst: true,
          historicalIdentityPreserved: true,
          automaticLanguageDetectionEnabled: false,
          automaticModernizationEnabled: false,
          automaticVariantNormalizationEnabled: false,
          automaticTranslationEnabled: false,
          boundedBackendOperations: 6,
          wordpressRequired: false
        });
      }
    });
  }

  return Object.freeze({
    schema: SCHEMA,
    version: VERSION,
    operations: OPERATIONS,
    languageKinds: LANGUAGE_KINDS,
    variantKinds: VARIANT_KINDS,
    relationTypes: RELATION_TYPES,
    create,
    createLanguageIdentity,
    createScriptIdentity,
    createVariantIdentity,
    createIdentityRelation,
    buildRequest
  });
});
