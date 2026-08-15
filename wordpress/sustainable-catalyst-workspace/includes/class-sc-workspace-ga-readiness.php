<?php
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Pre-1.0 general-availability readiness metadata.
 *
 * This contract records release-control requirements only. It does not inspect
 * project content, infer production sign-off, auto-promote a release to 1.0,
 * purge caches, or perform rollback.
 */
final class SC_Workspace_GA_Readiness {
    const CONTRACT_SCHEMA = 'sc-workspace-ga-readiness-contract/1.0';
    const DOSSIER_SCHEMA = 'sc-workspace-ga-readiness-dossier/1.0';
    const PRODUCTION_SIGNOFF_SCHEMA = 'sc-workspace-production-signoff-certificate/1.0';
    const PRODUCTION_SIGNOFF_RELEASE = '0.83.0';
    const PREVIOUS_RELEASE = '0.83.0';
    const ROLLBACK_RELEASE = '0.83.0';

    public static function required_checks() {
        return array(
            'production-signoff-certificate',
            'current-release-identity',
            'release-lineage',
            'package-integrity',
            'rollback-artifact',
            'current-wordpress-smoke',
            'release-notes-review',
            'support-recovery-review',
            'no-known-blocking-defects',
        );
    }

    public static function contract() {
        return array(
            'schema' => self::CONTRACT_SCHEMA,
            'dossier_schema' => self::DOSSIER_SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Production Sign-Off Closure & 1.0 Release Readiness',
            'release_candidate' => true,
            'feature_freeze' => true,
            'canonical_schema_freeze' => true,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'project_export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'production_signoff_release' => self::PRODUCTION_SIGNOFF_RELEASE,
            'required_production_signoff_schema' => self::PRODUCTION_SIGNOFF_SCHEMA,
            'signed_production_certificate_required' => true,
            'previous_release' => self::PREVIOUS_RELEASE,
            'rollback_release' => self::ROLLBACK_RELEASE,
            'rollback_schema_compatible' => true,
            'required_checks' => self::required_checks(),
            'human_readiness_attestation_required' => true,
            'release_owner_user_supplied' => true,
            'production_url_user_supplied' => true,
            'all_checks_required_for_ready_status' => true,
            'exportable_readiness_dossier' => true,
            'automatic_promotion_to_1_0' => false,
            'automatic_production_certification' => false,
            'automatic_cache_purge' => false,
            'automatic_rollback' => false,
            'automatic_project_migration' => false,
            'project_content_in_dossier' => false,
            'project_data_inspected' => false,
            'project_data_mutated' => false,
            'telemetry' => false,
            'canonical_mutation' => false,
        );
    }
}
