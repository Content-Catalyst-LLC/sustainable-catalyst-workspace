<?php
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Release-candidate production smoke/cache/rollback certification metadata.
 *
 * This helper never reads or mutates browser-local Workspace projects. Live
 * public-page, cache/CDN, preservation, and rollback outcomes remain explicit
 * field checks rather than being inferred by the server.
 */
final class SC_Workspace_Production_Certification {
    const CONTRACT_SCHEMA = 'sc-workspace-production-certification-contract/1.0';
    const REPORT_SCHEMA = 'sc-workspace-production-certification-report/1.0';
    const CHECKLIST_SCHEMA = 'sc-workspace-production-certification-checklist/1.0';
    const PREVIOUS_RELEASE = '1.7.0';
    const ROLLBACK_RELEASE = '1.7.0';

    public static function snapshot() {
        $deployment = class_exists('SC_Workspace_Deployment_Hardening')
            ? SC_Workspace_Deployment_Hardening::diagnostics()
            : array();
        $server_ready = !empty($deployment['server_ready']);
        return array(
            'schema' => self::REPORT_SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release_stage' => 'release-candidate',
            'package_automated_gate' => $server_ready,
            'deployment_server_ready' => $server_ready,
            'expected_script' => 'workspace-v1.8.0.js',
            'expected_style' => 'workspace-v1.8.0.css',
            'asset_cache_strategy' => 'versioned-filename-plus-version-query',
            'rollback_release' => self::ROLLBACK_RELEASE,
            'rollback_schema_compatible' => true,
            'rollback_artifact_required' => true,
            'live_public_page_smoke' => 'manual-pending',
            'live_rest_identity_smoke' => 'manual-pending',
            'live_cache_coherence' => 'manual-pending',
            'live_project_preservation' => 'manual-pending',
            'live_rollback_rehearsal' => 'manual-pending',
            'production_certified' => false,
            'automatic_cache_purge' => false,
            'automatic_rollback' => false,
            'automatic_project_migration' => false,
            'project_data_inspected' => false,
            'project_data_mutated' => false,
            'telemetry' => false,
        );
    }

    public static function contract() {
        return array(
            'schema' => self::CONTRACT_SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Production Smoke, Cache & Rollback Certification',
            'release_candidate' => true,
            'feature_freeze' => true,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'project_export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'package_smoke_gate' => true,
            'cache_version_coherence_gate' => true,
            'rollback_rehearsal_tooling' => true,
            'rollback_release' => self::ROLLBACK_RELEASE,
            'rollback_schema_compatible' => true,
            'rollback_artifact_required' => true,
            'production_smoke_script_required' => true,
            'live_production_checks_manual' => true,
            'production_certification_requires_live_field_checks' => true,
            'automatic_cache_purge' => false,
            'automatic_rollback' => false,
            'automatic_project_migration' => false,
            'canonical_mutation' => false,
            'project_data_inspected' => false,
            'telemetry' => false,
        );
    }
}
