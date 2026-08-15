<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_GA_Stabilization {
    const CONTRACT_SCHEMA = 'sc-workspace-ga-stabilization-contract/1.0';
    const REPORT_SCHEMA = 'sc-workspace-ga-stabilization-report/1.0';
    const GA_CERTIFICATE_SCHEMA = 'sc-workspace-general-availability-certificate/1.0';
    const GA_RELEASE = '1.0.0';
    const PREVIOUS_RELEASE = '1.0.0';
    const ROLLBACK_RELEASE = '1.0.0';
    public static function required_checks() { return array('ga-certificate','production-browser-smoke','cache-coherence','installer-reinstall','accessibility-regression','cross-browser-device-smoke','recovery-rollback','no-known-blocking-defects'); }
    public static function contract() { return array(
        'schema'=>self::CONTRACT_SCHEMA,'report_schema'=>self::REPORT_SCHEMA,'ga_certificate_schema'=>self::GA_CERTIFICATE_SCHEMA,
        'workspace_version'=>SC_WORKSPACE_VERSION,'release'=>'GA Field Stabilization & Production Evidence Closure','post_ga_stabilization'=>true,'stable_release'=>true,
        'lifecycle_state'=>'production','release_channel'=>'stable','canonical_schema_freeze'=>true,'storage_schema_version'=>35,'project_schema'=>'sc-workspace-project/20.0','project_export_schema'=>'sc-workspace-project-export/20.0','schema_migration_required'=>false,
        'ga_release'=>self::GA_RELEASE,'released_ga_certificate_required'=>true,'previous_release'=>self::PREVIOUS_RELEASE,'rollback_release'=>self::ROLLBACK_RELEASE,'rollback_schema_compatible'=>true,
        'required_checks'=>self::required_checks(),'field_evidence_required'=>true,'human_field_attestation_required'=>true,'exportable_stabilization_report'=>true,'local_evidence_record'=>true,
        'automatic_release_certification'=>false,'automatic_cache_purge'=>false,'automatic_rollback'=>false,'automatic_project_migration'=>false,'project_content_in_report'=>false,'project_data_inspected'=>false,'project_data_mutated'=>false,'behavioral_telemetry'=>false,'canonical_mutation'=>false,
    ); }
}
