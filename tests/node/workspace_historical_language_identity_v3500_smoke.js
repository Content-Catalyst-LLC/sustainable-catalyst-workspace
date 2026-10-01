'use strict';

const assert = require('assert');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const factory = require(path.join(root, 'app/linguistics/workspace-historical-language-script-variant-identity-v3500.js'));

(async () => {
  const requests = [];
  const apiClient = {
    async get(path) {
      requests.push({ method: 'GET', path });
      return { schema: 'sc-workspace-historical-language-script-variant-identity-workspace/1.0', version: '3.50.0' };
    },
    async post(path, body) {
      requests.push({ method: 'POST', path, body });
      return { ok: true, operation: body.operation };
    }
  };

  const w = factory.create({ apiClient });

  const latin = w.createScriptIdentity({
    id: 'script-latn',
    label: 'Latin script',
    scriptCode: 'Latn',
    direction: 'ltr'
  });

  const middleEnglish = w.createLanguageIdentity({
    id: 'lang-enm',
    label: 'Middle English',
    kind: 'historical-stage',
    languageTag: 'enm',
    scriptIds: ['script-latn'],
    regions: ['England'],
    temporalScope: { startYear: 1100, endYear: 1500, approximate: true },
    externalIdentifiers: { lexvo: 'enm' }
  });

  const lateMiddleEnglish = w.createVariantIdentity({
    id: 'variant-enm-late',
    label: 'Late Middle English orthographic variety',
    kind: 'orthography',
    languageIdentityId: 'lang-enm',
    scriptIdentityId: 'script-latn',
    temporalScope: { startYear: 1350, endYear: 1500, approximate: true }
  });

  const modernEnglish = w.createLanguageIdentity({
    id: 'lang-en-modern',
    label: 'Modern English',
    kind: 'language',
    languageTag: 'en',
    scriptIds: ['script-latn'],
    temporalScope: { startYear: 1500, approximate: true }
  });

  const relation = w.createIdentityRelation({
    id: 'rel-enm-modern',
    fromId: 'lang-enm',
    toId: 'lang-en-modern',
    relationType: 'predecessor-of',
    confidence: 0.95,
    sourceRef: 'source:historical-linguistics'
  });

  const input = {
    languageIdentities: [middleEnglish, modernEnglish],
    scriptIdentities: [latin],
    variants: [lateMiddleEnglish],
    relations: [relation]
  };

  await w.validate(input);
  await w.variantIndex(input);
  await w.temporalProfile(input);
  await w.scriptOrthographyProfile(input);
  await w.relationshipGraph(input);
  await w.lineage(input);
  await w.profile();

  assert.equal(w.inspect().historicalIdentityPreserved, true);
  assert.equal(w.inspect().automaticModernizationEnabled, false);
  assert.equal(w.inspect().automaticVariantNormalizationEnabled, false);
  assert.equal(w.inspect().wordpressRequired, false);
  assert.equal(requests[0].body.operation, 'workspace.linguistics.historical-identity-validate');
  assert.equal(requests[5].body.operation, 'workspace.linguistics.historical-identity-lineage');

  assert.throws(() => w.createLanguageIdentity({
    label: 'Bad scope',
    temporalScope: { startYear: 1500, endYear: 1200 }
  }), /endYear must be/);

  console.log('WORKSPACE_V3500_HISTORICAL_LANGUAGE_IDENTITY=PASS');
  console.log('WORKSPACE_V3500_SCRIPT_IDENTITY=PASS');
  console.log('WORKSPACE_V3500_VARIANT_IDENTITY=PASS');
  console.log('WORKSPACE_V3500_TEMPORAL_SCOPE=PASS');
  console.log('WORKSPACE_V3500_RELATIONSHIP_GRAPH=PASS');
  console.log('WORKSPACE_V3500_IDENTITY_LINEAGE=PASS');
  console.log('WORKSPACE_V3500_NO_AUTOMATIC_MODERNIZATION=PASS');
})();
