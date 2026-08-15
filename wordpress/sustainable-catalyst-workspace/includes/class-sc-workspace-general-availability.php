<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_General_Availability {
    const CONTRACT_SCHEMA = 'sc-workspace-general-availability-contract/1.0';
    const CERTIFICATE_SCHEMA = 'sc-workspace-general-availability-certificate/1.0';
    const READINESS_SCHEMA = 'sc-workspace-ga-readiness-dossier/1.0';
    const READINESS_RELEASE = '0.84.0';
    const PREVIOUS_RELEASE = '0.84.0';
    const ROLLBACK_RELEASE = '0.84.0';
    public static function required_checks() { return array('readiness-dossier','release-identity','package-integrity','rollback-artifact','live-wordpress-smoke','support-recovery','public-version-semantics','no-known-blocking-defects'); }
    public static function contract() { return array(
        'schema'=>self::CONTRACT_SCHEMA,'certificate_schema'=>self::CERTIFICATE_SCHEMA,'readiness_schema'=>self::READINESS_SCHEMA,
        'workspace_version'=>SC_WORKSPACE_VERSION,'release'=>'General Availability','general_availability'=>true,'stable_release'=>true,
        'lifecycle_state'=>'production','release_channel'=>'stable','feature_freeze'=>true,'canonical_schema_freeze'=>true,
        'storage_schema_version'=>35,'project_schema'=>'sc-workspace-project/20.0','project_export_schema'=>'sc-workspace-project-export/20.0','schema_migration_required'=>false,
        'readiness_release'=>self::READINESS_RELEASE,'valid_readiness_dossier_required'=>true,'previous_release'=>self::PREVIOUS_RELEASE,'rollback_release'=>self::ROLLBACK_RELEASE,'rollback_schema_compatible'=>true,
        'required_checks'=>self::required_checks(),'human_release_attestation_required'=>true,'release_operator_user_supplied'=>true,'production_url_user_supplied'=>true,'all_checks_required_for_released_status'=>true,'exportable_ga_certificate'=>true,
        'automatic_release_certification'=>false,'automatic_cache_purge'=>false,'automatic_rollback'=>false,'automatic_project_migration'=>false,'project_content_in_certificate'=>false,'project_data_inspected'=>false,'project_data_mutated'=>false,'telemetry'=>false,'canonical_mutation'=>false,
    ); }
}
