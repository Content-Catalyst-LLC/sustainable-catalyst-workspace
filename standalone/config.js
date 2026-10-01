(function (root) {
  'use strict';

  const config = Object.freeze({
    schema: 'sc-workspace-standalone-config/1.0',
    workspaceVersion: '3.48.0',
    host: 'standalone',
    apiBase: 'https://workspace-api.sustainablecatalyst.com',
    assetBase: './assets/',
    storageKey: 'sc_workspace',
    legacyStorageKey: 'sc_workspace_v0_1',
    recoveryStorageKey: 'sc_workspace_recovery_v0_8_2',
    lastGoodStorageKey: 'sc_workspace_last_good_v1',
    optionalModules: [
      {
        id: 'workspace.linguistics.original-language-corpus',
        assetId: 'workspace.linguistics.original-language-corpus',
        version: '3.47.0',
        title: 'Original-Language Text & Corpus Workspace',
        optional: true,
        enabled: true,
        dependsOn: ['core.api'],
        capabilities: [
          'workspace.linguistics.original-language',
          'workspace.linguistics.corpus',
          'workspace.linguistics.transformation-provenance'
        ],
        source: 'workspace',
        global: 'SCWorkspaceOriginalLanguageCorpusWorkspace'
      },
      {
        id: 'workspace.linguistics.annotation-corpus-structure',
        assetId: 'workspace.linguistics.annotation-corpus-structure',
        version: '3.48.0',
        title: 'Linguistic Annotation & Corpus Structure Workspace',
        optional: true,
        enabled: true,
        dependsOn: ['core.api', 'workspace.linguistics.original-language-corpus'],
        capabilities: [
          'workspace.linguistics.annotation',
          'workspace.linguistics.annotation-layers',
          'workspace.linguistics.document-structure',
          'workspace.linguistics.corpus-structure',
          'workspace.linguistics.annotation-lineage'
        ],
        source: 'workspace',
        global: 'SCWorkspaceLinguisticAnnotationCorpusStructureWorkspace'
      }
    ],
    automaticBackendHealthCheck: false,
    wordpressRequired: false
  });

  root.SCWorkspaceStandaloneConfig = config;
  root.SCWorkspaceConfig = config;
})(typeof globalThis !== 'undefined' ? globalThis : this);
