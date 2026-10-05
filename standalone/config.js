(function (root) {
  'use strict';

  const config = Object.freeze({
    schema: 'sc-workspace-standalone-config/1.0',
    workspaceVersion: '3.74.0',
    host: 'standalone',
    apiBase: 'https://workspace-api.sustainablecatalyst.com',
    sessionEndpoint: '/v1/session',
    authenticationMode: 'signed-http-only-session-cookie',
    serverProjectBootstrapEndpoint: '/v1/user-workspace/bootstrap',
    signedInProjectAuthority: 'workspace-backend-postgresql',
    navigationEndpoint: '/v1/workspace-navigation',
    recentWorkspaceEndpoint: '/v1/workspace-navigation/recent',
    commandPaletteShortcut: 'Mod+K',
    researchObjectBrowserEndpoint: '/v1/research-objects',
    researchObjectBrowserProfileEndpoint: '/v1/research-objects/profile',
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
      },
      {
        id: 'workspace.linguistics.translation-parallel-alignment',
        assetId: 'workspace.linguistics.translation-parallel-alignment',
        version: '3.49.0',
        title: 'Translation, Transliteration & Parallel Alignment Workspace',
        optional: true,
        enabled: true,
        dependsOn: ['core.api', 'workspace.linguistics.original-language-corpus', 'workspace.linguistics.annotation-corpus-structure'],
        capabilities: ['workspace.linguistics.translation-provenance','workspace.linguistics.transliteration-provenance','workspace.linguistics.parallel-text','workspace.linguistics.parallel-alignment'],
        source: 'workspace',
        global: 'SCWorkspaceTranslationTransliterationParallelAlignment'
      },
      {
        id: 'workspace.linguistics.historical-language-identity',
        assetId: 'workspace.linguistics.historical-language-identity',
        version: '3.51.0',
        title: 'Historical Language, Script & Variant Identity Workspace',
        optional: true,
        enabled: true,
        dependsOn: ['core.api', 'workspace.linguistics.original-language-corpus', 'workspace.linguistics.annotation-corpus-structure', 'workspace.linguistics.translation-parallel-alignment'],
        capabilities: [
          'workspace.linguistics.historical-language-identity',
          'workspace.linguistics.script-identity',
          'workspace.linguistics.variant-identity',
          'workspace.linguistics.temporal-language-profile',
          'workspace.linguistics.identity-lineage'
        ],
        source: 'workspace',
        global: 'SCWorkspaceHistoricalLanguageScriptVariantIdentity'
      }
,
      {
        id: 'workspace.linguistics.cross-language-entity-resolution',
        version: '3.51.0',
        schema: 'sc-workspace-cross-language-entity-toponym-resolution-workspace/1.0',
        assetId: 'workspace.linguistics.cross-language-entity-resolution',
        autoload: false
      }
    ],
    automaticBackendHealthCheck: false,
    wordpressRequired: false
  });

  root.SCWorkspaceStandaloneConfig = config;
  root.SCWorkspaceConfig = config;
})(typeof globalThis !== 'undefined' ? globalThis : this);
