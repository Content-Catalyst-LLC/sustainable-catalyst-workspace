<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Developer_API {
    const SCHEMA = 'sc-workspace-developer-api/1.0';
    const SDK_SCHEMA = 'sc-workspace-sdk-contract/1.0';
    const MANIFEST_SCHEMA = 'sc-workspace-extension-manifest/1.0';
    const GRANT_SCHEMA = 'sc-workspace-extension-capability-grant/1.0';
    const EVENT_SCHEMA = 'sc-workspace-extension-event-envelope/1.0';
    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'sdkSchema' => self::SDK_SCHEMA,
            'extensionManifestSchema' => self::MANIFEST_SCHEMA,
            'capabilityGrantSchema' => self::GRANT_SCHEMA,
            'eventEnvelopeSchema' => self::EVENT_SCHEMA,
            'surface' => 'exchange/api-embed',
            'apiNamespace' => 'sc-workspace/v1',
            'compatibilityPolicy' => 'additive-within-v1-breaking-changes-require-new-major',
            'stableContractFamilies' => array('workspace-objects','universal-search','library-continuity','knowledge-graph','lab-handoff','workbench-decision-roundtrip','cross-device-continuity','review-rooms','institutional-audit','research-operations'),
            'defaultCapabilityMode' => 'read-only-descriptive',
            'capabilities' => array('project-summary:read','workspace-objects:read','universal-search:read','library-pointers:read','knowledge-graph:read','handoff-context:read','review-room:read','audit-dossier:read','research-operations:read','portable-envelope:write'),
            'extensionManifestRequired' => true,
            'capabilityGrantRequired' => true,
            'grantsAreExplicit' => true,
            'grantsArePortableRecords' => true,
            'grantIsAuthenticationCredential' => false,
            'mutatingRestEndpoints' => false,
            'arbitraryCodeExecution' => false,
            'dynamicPluginInstallation' => false,
            'remoteExtensionLoading' => false,
            'automaticNetworkRequest' => false,
            'automaticCanonicalMutation' => false,
            'automaticAi' => false,
            'behavioralTelemetry' => false,
            'queryTelemetry' => false,
            'secretsInManifest' => false,
            'tokensInUrls' => false,
            'browserLocalSdk' => true,
            'schemaMigrationRequired' => false,
            'storageSchemaVersion' => 35,
            'projectSchema' => 'sc-workspace-project/20.0',
            'exportSchema' => 'sc-workspace-project-export/20.0',
            'previousRelease' => '1.10.0',
            'rollbackRelease' => '1.10.0',
        );
    }
}
