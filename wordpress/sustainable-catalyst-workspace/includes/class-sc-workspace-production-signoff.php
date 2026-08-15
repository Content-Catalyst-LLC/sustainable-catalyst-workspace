<?php
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Human-controlled live-production release sign-off metadata.
 *
 * This class exposes the field-validation contract only. It does not inspect
 * browser-local projects, infer that checks passed, purge caches, perform a
 * rollback, or certify production automatically.
 */
final class SC_Workspace_Production_Signoff {
    const CONTRACT_SCHEMA = 'sc-workspace-production-signoff-contract/1.0';
    const CERTIFICATE_SCHEMA = 'sc-workspace-production-signoff-certificate/1.0';
    const SIGNOFF_RELEASE = '0.83.0';
    const PREVIOUS_RELEASE = '0.82.1';
    const ROLLBACK_RELEASE = '0.82.1';

    public static function required_checks() {
        return array(
            'public-page-smoke',
            'rest-identity',
            'anonymous-use',
            'authenticated-use',
            'cache-coherence',
            'project-preservation',
            'rollback-rehearsal',
            'reinstall-current-release',
            'assistive-technology',
            'zoom-reflow-touch',
            'long-session-large-project',
            'two-device-continuity',
            'shared-review-handoff',
            'institutional-handoff',
        );
    }

    public static function contract() {
        return array(
            'schema' => self::CONTRACT_SCHEMA,
            'certificate_schema' => self::CERTIFICATE_SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'signoff_release' => self::SIGNOFF_RELEASE,
            'release' => 'Live Production Certification & Release Sign-Off',
            'historical_release_evidence' => true,
            'release_candidate' => true,
            'feature_freeze' => true,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'project_export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'previous_release' => self::PREVIOUS_RELEASE,
            'rollback_release' => self::ROLLBACK_RELEASE,
            'rollback_schema_compatible' => true,
            'required_checks' => self::required_checks(),
            'human_attestation_required' => true,
            'reviewer_label_user_supplied' => true,
            'production_url_user_supplied' => true,
            'all_checks_required_for_signoff' => true,
            'exportable_certificate' => true,
            'certificate_contains_project_content' => false,
            'automatic_production_certification' => false,
            'automatic_signoff' => false,
            'automatic_cache_purge' => false,
            'automatic_rollback' => false,
            'automatic_project_migration' => false,
            'project_data_inspected' => false,
            'project_data_mutated' => false,
            'telemetry' => false,
            'canonical_mutation' => false,
        );
    }
}
