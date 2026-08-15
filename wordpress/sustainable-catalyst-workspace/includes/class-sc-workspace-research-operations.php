<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Research_Operations {
    const SCHEMA = 'sc-workspace-research-operations/1.0';
    const OPERATION_SCHEMA = 'sc-workspace-research-operation/1.0';
    const RUN_SCHEMA = 'sc-workspace-research-operation-run/1.0';
    const RECEIPT_SCHEMA = 'sc-workspace-research-operation-receipt/1.0';
    const EXPORT_SCHEMA = 'sc-workspace-research-operations-export/1.0';
    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'operationSchema' => self::OPERATION_SCHEMA,
            'runSchema' => self::RUN_SCHEMA,
            'receiptSchema' => self::RECEIPT_SCHEMA,
            'exportSchema' => self::EXPORT_SCHEMA,
            'surface' => 'research/automation',
            'operationTypes' => array('saved-search-refresh','source-update-check','watchlist-review','research-queue-review','citation-verification','provenance-review','evidence-refresh','project-maintenance'),
            'cadences' => array('on-demand','daily','weekly','monthly','quarterly'),
            'plannerStates' => array('ready','due','scheduled','blocked','paused'),
            'runStates' => array('draft','reviewed','dismissed'),
            'legacyResearchAutomationRetained' => true,
            'legacyRoutineImportSupported' => true,
            'legacyRoutineAutoMigration' => false,
            'deterministicDuePlanning' => true,
            'blockedTargetsVisible' => true,
            'explicitRunQueue' => true,
            'manualExecutionOnly' => true,
            'scheduleIsDeclaration' => true,
            'backgroundExecution' => false,
            'automaticNetworkRequest' => false,
            'externalFreshnessRequiresUserAction' => true,
            'automaticCanonicalMutation' => false,
            'automaticTaskCreation' => false,
            'automaticAi' => false,
            'reviewRequired' => true,
            'receiptsMetadataOnly' => true,
            'receiptsContainProjectContent' => false,
            'receiptsContainQueryText' => false,
            'receiptsContainSourceUrls' => false,
            'receiptIntegrityAlgorithm' => 'SHA-256',
            'portableOperationsExport' => true,
            'behavioralTelemetry' => false,
            'queryTelemetry' => false,
            'schemaMigrationRequired' => false,
            'storageSchemaVersion' => 35,
            'projectSchema' => 'sc-workspace-project/20.0',
            'exportSchemaVersion' => 'sc-workspace-project-export/20.0',
        );
    }
}
