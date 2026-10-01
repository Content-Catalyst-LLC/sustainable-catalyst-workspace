'use strict';

const assert = require('assert');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const factory = require(path.join(root, 'app/linguistics/workspace-original-language-corpus-v3470.js'));

(async () => {
  const requests = [];
  const apiClient = {
    async get(path) {
      requests.push({ method: 'GET', path });
      return { schema: 'sc-workspace-original-language-corpus-workspace/1.0', version: '3.47.0' };
    },
    async post(path, body) {
      requests.push({ method: 'POST', path, body });
      return { ok: true, schema: 'sc-workspace-multilingual-text-corpus-runtime-result/1.0', operation: body.operation };
    }
  };

  const workspace = factory.create({ apiClient });

  const original = workspace.createOriginalText({
    id: 'arabic-source',
    text: 'مرحبا بالعالم',
    languageTag: 'ar',
    script: 'Arab',
    sourceRef: 'source:1'
  });

  const translation = workspace.createDerivedRepresentation({
    id: 'english-translation',
    text: 'Hello world',
    languageTag: 'en',
    script: 'Latn',
    derivedFromId: 'arabic-source',
    transformation: 'translation',
    sourceRef: 'translation:1'
  });

  const corpus = workspace.createCorpus({
    id: 'parallel-corpus',
    title: 'Arabic / English sample',
    documents: [original, translation]
  });

  assert.equal(original.representation, 'original');
  assert.equal(translation.representation, 'derived');
  assert.equal(translation.derivedFromId, original.id);
  assert.equal(corpus.documents.length, 2);
  assert.equal(workspace.inspect().automaticLanguageDetectionEnabled, false);
  assert.equal(workspace.inspect().automaticTranslationEnabled, false);
  assert.equal(workspace.inspect().wordpressRequired, false);

  await workspace.textIdentity(original);
  await workspace.profileCorpus(corpus);
  await workspace.traceCorpusLineage(corpus);
  await workspace.profile();

  assert.equal(requests[0].path, '/v1/multilingual-text-corpus-runtime/execute');
  assert.equal(requests[0].body.operation, 'workspace.linguistics.text-identity');
  assert.equal(requests[0].body.languageTag, 'ar');
  assert.equal(requests[1].body.operation, 'workspace.linguistics.corpus-profile');
  assert.equal(requests[2].body.operation, 'workspace.linguistics.corpus-lineage');
  assert.equal(requests[2].body.documents[1].transformation, 'translation');
  assert.equal(requests[3].path, '/v1/original-language-corpus-workspace');

  assert.throws(
    () => workspace.createOriginalText({ text: 'missing language' }),
    /languageTag must be explicit/
  );

  assert.throws(
    () => workspace.createOriginalText({
      text: 'bad original',
      languageTag: 'en',
      derivedFromId: 'x',
      transformation: 'translation'
    }),
    /original-language text cannot declare/
  );

  assert.throws(
    () => workspace.createDerivedRepresentation({
      text: 'derived without parent',
      languageTag: 'en',
      transformation: 'translation'
    }),
    /derived representations require derivedFromId/
  );

  console.log('WORKSPACE_V3470_ORIGINAL_LANGUAGE_TEXT=PASS');
  console.log('WORKSPACE_V3470_DERIVED_REPRESENTATION=PASS');
  console.log('WORKSPACE_V3470_CORPUS_FOUNDATION=PASS');
  console.log('WORKSPACE_V3470_TRANSFORMATION_LINEAGE=PASS');
  console.log('WORKSPACE_V3470_EXPLICIT_LANGUAGE_METADATA=PASS');
  console.log('WORKSPACE_V3470_NO_AUTOMATIC_TRANSLATION=PASS');
  console.log('WORKSPACE_V3470_BACKEND_RUNTIME_BRIDGE=PASS');
})();
