'use strict';

const assert = require('assert');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const factory = require(path.join(root, 'app/linguistics/workspace-linguistic-annotation-corpus-structure-v3480.js'));

(async () => {
  const requests = [];
  const apiClient = {
    async get(path) {
      requests.push({ method: 'GET', path });
      return { schema: 'sc-workspace-linguistic-annotation-corpus-structure-workspace/1.0', version: '3.48.0' };
    },
    async post(path, body) {
      requests.push({ method: 'POST', path, body });
      return { ok: true, operation: body.operation };
    }
  };

  const originalLanguageWorkspace = { schema: 'sc-workspace-original-language-corpus-workspace/1.0' };
  const workspace = factory.create({ apiClient, originalLanguageWorkspace });

  const document = {
    id: 'doc-ar',
    text: 'مرحبا بالعالم',
    languageTag: 'ar',
    script: 'Arab',
    representation: 'original',
    sourceRef: 'source:arabic'
  };

  const token = workspace.createAnnotation({
    id: 'ann-token-1',
    documentId: 'doc-ar',
    layerId: 'tokens',
    annotationType: 'token',
    startOffset: 0,
    endOffset: 5,
    label: 'TOKEN',
    method: 'human',
    annotator: 'reviewer-1'
  });

  const entity = workspace.createAnnotation({
    id: 'ann-entity-1',
    documentId: 'doc-ar',
    layerId: 'entities',
    annotationType: 'entity',
    startOffset: 0,
    endOffset: 5,
    label: 'GREETING',
    method: 'model',
    confidence: 0.94,
    derivedFromAnnotationIds: ['ann-token-1']
  });

  const tokenLayer = workspace.createAnnotationLayer({
    id: 'tokens',
    title: 'Tokens',
    annotationType: 'token',
    annotations: [token]
  });

  const entityLayer = workspace.createAnnotationLayer({
    id: 'entities',
    title: 'Entities',
    annotationType: 'entity',
    annotations: [entity]
  });

  const rootNode = workspace.createStructureNode({
    id: 'node-document',
    documentId: 'doc-ar',
    nodeType: 'document',
    order: 0,
    startOffset: 0,
    endOffset: factory.codePointLength(document.text)
  });

  const sentenceNode = workspace.createStructureNode({
    id: 'node-sentence-1',
    documentId: 'doc-ar',
    nodeType: 'sentence',
    parentId: 'node-document',
    order: 0,
    startOffset: 0,
    endOffset: factory.codePointLength(document.text)
  });

  const structure = workspace.createCorpusStructure({
    id: 'structure-1',
    title: 'Arabic sample structure',
    nodes: [rootNode, sentenceNode]
  });

  assert.equal(workspace.inspect().offsetUnit, 'unicode-code-point');
  assert.equal(workspace.inspect().wordpressRequired, false);
  assert.equal(workspace.inspect().automaticLanguageDetectionEnabled, false);
  assert.equal(structure.nodes.length, 2);

  const input = {
    documents: [document],
    layers: [tokenLayer, entityLayer],
    annotations: [token, entity],
    structureNodes: structure.nodes,
    targetDocumentId: 'doc-ar'
  };

  workspace.validateLocalOffsets(input.documents, input.annotations, input.structureNodes);

  await workspace.validateAnnotations(input);
  await workspace.annotationSpanIndex(input);
  await workspace.annotationLayerProfile(input);
  await workspace.documentStructure(input);
  await workspace.corpusStructure(input);
  await workspace.annotationLineage(input);
  await workspace.profile();

  assert.equal(requests[0].body.operation, 'workspace.linguistics.annotation-validate');
  assert.equal(requests[1].body.operation, 'workspace.linguistics.annotation-span-index');
  assert.equal(requests[2].body.operation, 'workspace.linguistics.annotation-layer-profile');
  assert.equal(requests[3].body.operation, 'workspace.linguistics.document-structure');
  assert.equal(requests[4].body.operation, 'workspace.linguistics.corpus-structure');
  assert.equal(requests[5].body.operation, 'workspace.linguistics.annotation-lineage');
  assert.equal(requests[6].path, '/v1/linguistic-annotation-corpus-structure-workspace');
  assert.equal(requests[0].body.annotations[0].offsetUnit, 'unicode-code-point');

  assert.throws(() => workspace.createAnnotation({
    documentId: 'doc-ar',
    layerId: 'tokens',
    annotationType: 'token',
    startOffset: 6,
    endOffset: 2
  }), /endOffset must be/);

  assert.throws(() => workspace.createStructureNode({
    documentId: 'doc-ar',
    nodeType: 'unknown',
    startOffset: 0,
    endOffset: 1
  }), /nodeType is unsupported/);

  console.log('WORKSPACE_V3480_ANNOTATION_OBJECTS=PASS');
  console.log('WORKSPACE_V3480_ANNOTATION_LAYERS=PASS');
  console.log('WORKSPACE_V3480_CORPUS_STRUCTURE=PASS');
  console.log('WORKSPACE_V3480_UNICODE_CODE_POINT_OFFSETS=PASS');
  console.log('WORKSPACE_V3480_ANNOTATION_LINEAGE=PASS');
  console.log('WORKSPACE_V3480_BACKEND_RUNTIME_BRIDGE=PASS');
})();
