(function (root, factory) {
  'use strict';

  const api = factory();

  if (typeof module === 'object' && module.exports) {
    module.exports = api;
    return;
  }

  root.SCWorkspaceOriginalLanguageCorpusWorkspaceFactory = api;
  root.SCWorkspaceOriginalLanguageCorpusWorkspace = api.create({
    apiClient: root.SCWorkspaceDecoupledApiClient || null
  });
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-original-language-corpus-workspace/1.0';
  const VERSION = '3.47.0';
  const REQUEST_SCHEMA = 'sc-workspace-multilingual-text-corpus-runtime-request/1.0';
  const TEXT_SCHEMA = 'sc-workspace-original-language-text/1.0';
  const CORPUS_SCHEMA = 'sc-workspace-original-language-corpus/1.0';
  const DERIVATION_SCHEMA = 'sc-workspace-derived-language-representation/1.0';
  const BACKEND_PROFILE_PATH = '/v1/original-language-corpus-workspace';
  const BACKEND_EXECUTE_PATH = '/v1/multilingual-text-corpus-runtime/execute';

  const OPERATIONS = Object.freeze({
    textIdentity: 'workspace.linguistics.text-identity',
    textNormalize: 'workspace.linguistics.text-normalize',
    textSegment: 'workspace.linguistics.text-segment',
    corpusProfile: 'workspace.linguistics.corpus-profile',
    corpusSegmentIndex: 'workspace.linguistics.corpus-segment-index',
    corpusLineage: 'workspace.linguistics.corpus-lineage'
  });

  const TRANSFORMATIONS = Object.freeze([
    'translation',
    'transliteration',
    'normalization',
    'transcription',
    'annotation',
    'ocr',
    'htr',
    'other'
  ]);

  const LANGUAGE_TAG_RE = /^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$/;
  const SCRIPT_RE = /^[A-Za-z]{4}$/;

  function clean(value) {
    return String(value == null ? '' : value).trim();
  }

  function requiredLanguageTag(value) {
    const tag = clean(value);
    if (!LANGUAGE_TAG_RE.test(tag)) {
      throw new Error('languageTag must be explicit; automatic language detection is disabled');
    }
    return tag;
  }

  function optionalScript(value) {
    const script = clean(value);
    if (!script) return null;
    if (!SCRIPT_RE.test(script)) throw new Error('script must be an explicit four-letter ISO 15924-like code');
    return script;
  }

  function objectId(prefix) {
    const random = Math.random().toString(36).slice(2, 10);
    return `${prefix}-${Date.now().toString(36)}-${random}`;
  }

  function baseText(input) {
    const source = input && typeof input === 'object' ? input : {};
    return {
      id: clean(source.id) || objectId('text'),
      text: String(source.text == null ? '' : source.text),
      languageTag: requiredLanguageTag(source.languageTag),
      script: optionalScript(source.script),
      sourceRef: clean(source.sourceRef) || null
    };
  }

  function createOriginalText(input) {
    const value = baseText(input);
    const source = input && typeof input === 'object' ? input : {};
    if (source.derivedFromId || source.transformation) {
      throw new Error('original-language text cannot declare derivedFromId or transformation');
    }

    return Object.freeze({
      schema: TEXT_SCHEMA,
      version: VERSION,
      id: value.id,
      text: value.text,
      languageTag: value.languageTag,
      script: value.script,
      representation: 'original',
      derivedFromId: null,
      transformation: null,
      sourceRef: value.sourceRef,
      originalLanguageFirst: true
    });
  }

  function createDerivedRepresentation(input) {
    const value = baseText(input);
    const source = input && typeof input === 'object' ? input : {};
    const derivedFromId = clean(source.derivedFromId);
    const transformation = clean(source.transformation).toLowerCase();

    if (!derivedFromId) throw new Error('derived representations require derivedFromId');
    if (!TRANSFORMATIONS.includes(transformation)) {
      throw new Error('derived representations require an explicit supported transformation');
    }

    return Object.freeze({
      schema: DERIVATION_SCHEMA,
      version: VERSION,
      id: value.id,
      text: value.text,
      languageTag: value.languageTag,
      script: value.script,
      representation: 'derived',
      derivedFromId,
      transformation,
      sourceRef: value.sourceRef,
      originalLanguageFirst: true,
      automaticTransformationApplied: false
    });
  }

  function validateDocument(document) {
    if (!document || typeof document !== 'object') throw new Error('corpus documents must be Workspace text objects');
    requiredLanguageTag(document.languageTag);

    if (document.representation === 'original') {
      if (document.derivedFromId || document.transformation) {
        throw new Error('original corpus documents cannot carry derivation metadata');
      }
      return document;
    }

    if (document.representation === 'derived') {
      if (!clean(document.derivedFromId)) throw new Error('derived corpus documents require derivedFromId');
      if (!TRANSFORMATIONS.includes(clean(document.transformation).toLowerCase())) {
        throw new Error('derived corpus documents require an explicit transformation');
      }
      return document;
    }

    throw new Error('corpus document representation must be original or derived');
  }

  function createCorpus(input) {
    const source = input && typeof input === 'object' ? input : {};
    const documents = Array.isArray(source.documents) ? source.documents.map(validateDocument) : [];
    if (!documents.length) throw new Error('corpus requires at least one document');
    if (documents.length > 100) throw new Error('corpus exceeds the bounded maximum of 100 documents');

    const ids = new Set();
    documents.forEach((document) => {
      const id = clean(document.id);
      if (!id) throw new Error('corpus documents require IDs');
      if (ids.has(id)) throw new Error('corpus document IDs must be unique');
      ids.add(id);
    });

    return Object.freeze({
      schema: CORPUS_SCHEMA,
      version: VERSION,
      id: clean(source.id) || objectId('corpus'),
      title: clean(source.title) || 'Untitled corpus',
      documents: Object.freeze([...documents]),
      originalLanguageFirst: true,
      translationIsDerivedRepresentation: true,
      transliterationIsDerivedRepresentation: true,
      automaticLanguageDetectionEnabled: false,
      automaticTranslationEnabled: false,
      automaticTransliterationEnabled: false
    });
  }

  function backendDocument(document) {
    validateDocument(document);
    const payload = {
      documentId: clean(document.id),
      text: String(document.text == null ? '' : document.text),
      languageTag: requiredLanguageTag(document.languageTag),
      representation: document.representation
    };
    if (document.script) payload.script = optionalScript(document.script);
    if (document.derivedFromId) payload.derivedFromId = clean(document.derivedFromId);
    if (document.transformation) payload.transformation = clean(document.transformation).toLowerCase();
    if (document.sourceRef) payload.sourceRef = clean(document.sourceRef);
    return payload;
  }

  function request(operation, payload) {
    if (!Object.values(OPERATIONS).includes(operation)) {
      throw new Error('unsupported Workspace linguistics operation');
    }

    const source = payload && typeof payload === 'object' ? payload : {};
    const body = {
      schema: REQUEST_SCHEMA,
      operation
    };

    if (source.text !== undefined) body.text = String(source.text);
    if (source.languageTag !== undefined) body.languageTag = requiredLanguageTag(source.languageTag);
    if (source.script) body.script = optionalScript(source.script);
    if (source.normalizationForm) body.normalizationForm = String(source.normalizationForm);
    if (source.segmentMode) body.segmentMode = String(source.segmentMode);
    if (Array.isArray(source.documents)) body.documents = source.documents.map(backendDocument);

    return body;
  }

  function create(options) {
    const source = options && typeof options === 'object' ? options : {};
    const apiClient = source.apiClient || null;

    async function execute(operation, payload, requestOptions) {
      if (!apiClient || typeof apiClient.post !== 'function') {
        throw new Error('Original-language Workspace requires the decoupled Workspace API client');
      }
      return apiClient.post(BACKEND_EXECUTE_PATH, request(operation, payload), requestOptions);
    }

    async function profile(requestOptions) {
      if (!apiClient || typeof apiClient.get !== 'function') {
        throw new Error('Original-language Workspace requires the decoupled Workspace API client');
      }
      return apiClient.get(BACKEND_PROFILE_PATH, requestOptions);
    }

    function textPayload(textObject, extras) {
      const text = validateDocument(textObject);
      return Object.assign({
        text: text.text,
        languageTag: text.languageTag,
        script: text.script || undefined
      }, extras || {});
    }

    function corpusPayload(corpus) {
      if (!corpus || corpus.schema !== CORPUS_SCHEMA) throw new Error('expected a Workspace original-language corpus');
      return { documents: corpus.documents };
    }

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      title: 'Original-Language Text & Corpus Workspace',
      capabilities: Object.freeze([
        'workspace.linguistics.original-language',
        'workspace.linguistics.corpus',
        'workspace.linguistics.transformation-provenance',
        'workspace.linguistics.backend-runtime'
      ]),
      backendRuntimeSchema: 'sc-workspace-multilingual-text-corpus-runtime/1.0',
      backendProfilePath: BACKEND_PROFILE_PATH,
      backendExecutePath: BACKEND_EXECUTE_PATH,
      operations: OPERATIONS,
      transformations: TRANSFORMATIONS,
      createOriginalText,
      createDerivedRepresentation,
      createCorpus,
      request,
      execute,
      profile,
      textIdentity(textObject, options) {
        return execute(OPERATIONS.textIdentity, textPayload(textObject), options);
      },
      normalizeText(textObject, normalizationForm, options) {
        return execute(
          OPERATIONS.textNormalize,
          textPayload(textObject, { normalizationForm: normalizationForm || 'NFC' }),
          options
        );
      },
      segmentText(textObject, segmentMode, options) {
        return execute(
          OPERATIONS.textSegment,
          textPayload(textObject, { segmentMode: segmentMode || 'paragraph' }),
          options
        );
      },
      profileCorpus(corpus, options) {
        return execute(OPERATIONS.corpusProfile, corpusPayload(corpus), options);
      },
      indexCorpusSegments(corpus, segmentMode, options) {
        return execute(
          OPERATIONS.corpusSegmentIndex,
          Object.assign(corpusPayload(corpus), { segmentMode: segmentMode || 'paragraph' }),
          options
        );
      },
      traceCorpusLineage(corpus, options) {
        return execute(OPERATIONS.corpusLineage, corpusPayload(corpus), options);
      },
      inspect() {
        return Object.freeze({
          schema: 'sc-workspace-original-language-corpus-workspace-state/1.0',
          version: VERSION,
          apiClientAvailable: Boolean(apiClient && typeof apiClient.post === 'function'),
          originalLanguageFirst: true,
          translationIsDerivedRepresentation: true,
          transliterationIsDerivedRepresentation: true,
          automaticLanguageDetectionEnabled: false,
          automaticTranslationEnabled: false,
          automaticTransliterationEnabled: false,
          boundedBackendOperations: 6,
          wordpressRequired: false
        });
      }
    });
  }

  return Object.freeze({
    schema: SCHEMA,
    version: VERSION,
    create,
    createOriginalText,
    createDerivedRepresentation,
    createCorpus,
    request,
    operations: OPERATIONS,
    transformations: TRANSFORMATIONS
  });
});
