<?php
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Release-candidate WordPress/deployment guardrails.
 *
 * This class deliberately tracks only release/package metadata. It never reads,
 * writes, migrates, uploads, or deletes browser-local Workspace project data.
 */
final class SC_Workspace_Deployment_Hardening {
    const SCHEMA = 'sc-workspace-deployment-state/1.0';
    const CONTRACT_SCHEMA = 'sc-workspace-wordpress-deployment-hardening-contract/1.0';
    const STATE_OPTION = 'sc_workspace_deployment_state_v1';
    const HISTORY_OPTION = 'sc_workspace_deployment_history_v1';
    const MAX_HISTORY = 12;
    const PREVIOUS_RELEASE = '3.68.0';
    const ROLLBACK_RELEASE = '3.68.0';
    const REQUIRED_WORDPRESS = '6.4';
    const REQUIRED_PHP = '8.0';
    const CANONICAL_PLUGIN_ROOT = 'sustainable-catalyst-workspace';
    const MIN_CURRENT_STYLE_BYTES = 100000;
    const MIN_CURRENT_SCRIPT_BYTES = 5000;
    const MIN_LIFECYCLE_RUNTIME_BYTES = 10000;
    const MIN_APPLICATION_KERNEL_BYTES = 4000;
    const MIN_MODULE_REGISTRY_BYTES = 6000;
    const MIN_STATE_STORE_RUNTIME_BYTES = 1500;
    const MIN_PERSISTENCE_RUNTIME_BYTES = 4500;
    const MIN_PROJECT_RUNTIME_BYTES = 4500;
    const MIN_HOST_ADAPTER_CONTRACT_BYTES = 1500;
    const MIN_HOST_ADAPTER_BYTES = 1500;
    const MIN_TRANSPORT_RUNTIME_BYTES = 2000;
    const MIN_AUTH_CONTEXT_RUNTIME_BYTES = 1200;
    const MIN_API_CLIENT_RUNTIME_BYTES = 1200;
    const MIN_TRANSPORT_ADAPTER_BYTES = 700;
    const MIN_AUTH_ADAPTER_BYTES = 700;
    const MIN_WORDPRESS_THIN_ADAPTER_BYTES = 2500;
    const MIN_RUNTIME_ASSET_MANIFEST_BYTES = 1500;
    const MIN_ORIGINAL_LANGUAGE_CORPUS_WORKSPACE_BYTES = 5000;
    const MIN_LINGUISTIC_ANNOTATION_CORPUS_STRUCTURE_WORKSPACE_BYTES = 6000;
    const MIN_TRANSLATION_PARALLEL_ALIGNMENT_WORKSPACE_BYTES = 6000;
    const MIN_HISTORICAL_LANGUAGE_IDENTITY_WORKSPACE_BYTES = 7000;
    const MIN_DECOUPLED_PRODUCTION_BASELINE_BYTES = 1500;

    public static function required_files() {
        return array(
            'registry' => 'includes/class-sc-workspace-registry.php',
            'platform' => 'includes/class-sc-workspace-platform.php',
            'workspace' => 'includes/class-sc-workspace.php',
            'deployment' => 'includes/class-sc-workspace-deployment.php',
            'backend_bridge' => 'includes/class-sc-workspace-backend.php',
            'current_script' => 'assets/js/workspace-v' . SC_WORKSPACE_VERSION . '.js',
            'current_style' => 'assets/css/workspace-v' . SC_WORKSPACE_VERSION . '.css',
            'typed_client' => 'assets/js/sc-workspace-typed-client-v3100.js',
            'local_compatibility' => 'assets/js/sc-workspace-local-project-compat-v3690.js',
            'host_adapter_contract' => 'assets/js/sc-workspace-host-adapter-contract-v34620.js',
            'application_kernel' => 'assets/js/sc-workspace-application-kernel-v3690.js',
            'wordpress_thin_adapter' => 'assets/js/sc-workspace-wordpress-thin-adapter-v3690.js',
            'runtime_asset_manifest' => 'assets/js/sc-workspace-runtime-asset-manifest-v3690.js',
            'original_language_corpus_workspace' => 'assets/js/sc-workspace-original-language-corpus-v3470.js',
            'linguistic_annotation_corpus_structure_workspace' => 'assets/js/sc-workspace-linguistic-annotation-corpus-structure-v3480.js',
            'translation_parallel_alignment_workspace' => 'assets/js/sc-workspace-translation-transliteration-parallel-alignment-v3490.js',
            'historical_language_identity_workspace' => 'assets/js/sc-workspace-historical-language-script-variant-identity-v3500.js',
            'reproducible_computational_linguistics_workspace' => 'assets/js/sc-workspace-reproducible-computational-linguistics-v3530.js',
            'integrated_global_language_research_workspace' => 'assets/js/sc-workspace-integrated-global-language-research-v3540.js',
            'language_research_production_certification' => 'assets/js/sc-workspace-language-research-production-certification-v3550.js',
            'research_pipeline_composer' => 'assets/js/sc-workspace-research-pipeline-composer-v3560.js',
            'dataset_feature_engineering' => 'assets/js/sc-workspace-dataset-feature-engineering-v3570.js',
            'training_evaluation_experiment' => 'assets/js/sc-workspace-training-evaluation-experiment-v3580.js',
            'model_registry_lineage' => 'assets/js/sc-workspace-model-registry-lineage-v3590.js',
            'assets/js/sc-workspace-agentic-research-workflow-v3600.js',
            'human_governance_approval_intervention' => 'assets/js/sc-workspace-human-governance-approval-intervention-v3610.js',
            'multi_agent_orchestration_specialist_coordination' => 'assets/js/sc-workspace-multi-agent-orchestration-specialist-coordination-v3620.js',
            'reproducible_agentic_research_package' => 'assets/js/sc-workspace-reproducible-agentic-research-package-v3630.js',
            'integrated_research_os' => 'assets/js/sc-workspace-integrated-research-os-v3640.js',
            'production_certification_agentic' => 'assets/js/sc-workspace-production-certification-agentic-v3650.js',
            'unified_research_session' => 'assets/js/sc-workspace-unified-research-session-v3660.js',
            'research_os_runtime_registry' => 'assets/js/sc-workspace-research-os-runtime-registry-v3670.js',
            'cross_product_research_handoff_consolidation' => 'assets/js/sc-workspace-cross-product-research-handoff-consolidation-v3680.js',
            'portable_research_workspace_recovery' => 'assets/js/sc-workspace-portable-research-workspace-recovery-v3690.js',
            'decoupled_production_baseline' => 'assets/js/sc-workspace-decoupled-production-baseline-v346100.js',
            'module_registry' => 'assets/js/sc-workspace-module-registry-v34650.js',
            'state_store_runtime' => 'assets/js/sc-workspace-state-store-v34640.js',
            'persistence_runtime' => 'assets/js/sc-workspace-persistence-runtime-v34640.js',
            'project_runtime' => 'assets/js/sc-workspace-project-runtime-v34630.js',
            'wordpress_host_adapter' => 'assets/js/sc-workspace-wordpress-host-adapter-v34620.js',
            'transport_runtime' => 'assets/js/sc-workspace-transport-v34620.js',
            'auth_context_runtime' => 'assets/js/sc-workspace-auth-context-v34620.js',
            'api_client_runtime' => 'assets/js/sc-workspace-api-client-v34620.js',
            'wordpress_transport_adapter' => 'assets/js/sc-workspace-wordpress-transport-adapter-v34620.js',
            'wordpress_auth_adapter' => 'assets/js/sc-workspace-wordpress-auth-adapter-v34620.js',
            'deployment_runtime' => 'assets/js/sc-workspace-wordpress-deployment-hardening-v1.js',
            'deployment_ui' => 'assets/js/sc-workspace-wordpress-deployment-hardening-ui-v1.js',
            'production_certification' => 'includes/class-sc-workspace-production-certification.php',
            'production_runtime' => 'assets/js/sc-workspace-production-smoke-cache-rollback-v1.js',
            'production_ui' => 'assets/js/sc-workspace-production-smoke-cache-rollback-ui-v1.js',
            'production_signoff' => 'includes/class-sc-workspace-production-signoff.php',
            'production_signoff_runtime' => 'assets/js/sc-workspace-production-signoff-v1.js',
            'production_signoff_ui' => 'assets/js/sc-workspace-production-signoff-ui-v1.js',
            'ga_readiness' => 'includes/class-sc-workspace-ga-readiness.php',
            'ga_readiness_runtime' => 'assets/js/sc-workspace-ga-readiness-v1.js',
            'ga_readiness_ui' => 'assets/js/sc-workspace-ga-readiness-ui-v1.js',
            'general_availability' => 'includes/class-sc-workspace-general-availability.php',
            'general_availability_runtime' => 'assets/js/sc-workspace-general-availability-v1.js',
            'general_availability_ui' => 'assets/js/sc-workspace-general-availability-ui-v1.js',
            'release_candidate_runtime' => 'assets/js/sc-workspace-release-candidate-i-v1.js',
            'workspace_home' => 'includes/class-sc-workspace-home.php',
            'workspace_home_runtime' => 'assets/js/sc-workspace-home-v1.js',
            'universal_search' => 'includes/class-sc-workspace-universal-search.php',
            'universal_search_runtime' => 'assets/js/sc-workspace-universal-search-v1.js',
            'lab_integration' => 'includes/class-sc-workspace-lab-integration.php',
            'workbench_decision_roundtrip' => 'includes/class-sc-workspace-workbench-decision-roundtrip.php',
            'includes/class-sc-workspace-cross-device-production.php',
            'review_rooms' => 'includes/class-sc-workspace-review-rooms.php',
            'review_rooms_runtime' => 'assets/js/sc-workspace-review-rooms-v1.js',
            'review_rooms_ui' => 'assets/js/sc-workspace-review-rooms-ui-v1.js',
            'institutional_audit_studio' => 'includes/class-sc-workspace-institutional-audit-studio.php',
            'institutional_audit_runtime' => 'assets/js/sc-workspace-institutional-audit-studio-v1.js',
            'institutional_audit_ui' => 'assets/js/sc-workspace-institutional-audit-studio-ui-v1.js',
            'research_operations' => 'includes/class-sc-workspace-research-operations.php',
            'research_operations_runtime' => 'assets/js/sc-workspace-research-operations-v1.js',
            'research_operations_ui' => 'assets/js/sc-workspace-research-operations-ui-v1.js',
            'developer_api' => 'includes/class-sc-workspace-developer-api.php',
            'developer_sdk' => 'assets/js/sc-workspace-developer-sdk-v1.js',
            'developer_api_ui' => 'assets/js/sc-workspace-developer-api-ui-v1.js',
            'institutional_scale_hardening' => 'includes/class-sc-workspace-institutional-scale-hardening.php',
            'institutional_scale_runtime' => 'assets/js/sc-workspace-institutional-scale-hardening-v1.js',
            'institutional_scale_ui' => 'assets/js/sc-workspace-institutional-scale-hardening-ui-v1.js',
            'connected_intelligence' => 'includes/class-sc-workspace-connected-intelligence.php',
            'connected_intelligence_runtime' => 'assets/js/sc-workspace-connected-intelligence-v1.js',
            'connected_intelligence_ui' => 'assets/js/sc-workspace-connected-intelligence-ui-v1.js',
            'public_research_packages' => 'includes/class-sc-workspace-public-research-packages.php',
            'public_research_packages_runtime' => 'assets/js/sc-workspace-public-research-packages-v1.js',
            'public_research_packages_ui' => 'assets/js/sc-workspace-public-research-packages-ui-v1.js',
            'product_maturity' => 'includes/class-sc-workspace-product-maturity.php',
            'product_maturity_runtime' => 'assets/js/sc-workspace-product-maturity-v1.js',
            'product_maturity_ui' => 'assets/js/sc-workspace-product-maturity-ui-v1.js',
            'connected_knowledge' => 'includes/class-sc-workspace-connected-knowledge.php',
            'connected_knowledge_runtime' => 'assets/js/sc-workspace-connected-knowledge-v2.js',
            'connected_knowledge_ui' => 'assets/js/sc-workspace-connected-knowledge-ui-v2.js',
            'work_mode_cards' => 'includes/class-sc-workspace-work-mode-cards.php',
            'root_scope' => 'includes/class-sc-workspace-root-scope.php',
            'visual_regression' => 'includes/class-sc-workspace-visual-regression.php',
            'workbench_decision_roundtrip_js' => 'assets/js/sc-workspace-workbench-decision-roundtrip-v1.js',
            'lab_integration_runtime' => 'assets/js/sc-workspace-lab-integration-v1.js',
        );
    }

public static function preflight() {
    clearstatcache();
    $missing = array();
    foreach (self::required_files() as $label => $relative) {
        $path = SC_WORKSPACE_DIR . $relative;
        if (!is_file($path) || !is_readable($path)) {
            $missing[] = $label;
        }
    }
    $canonical_root = basename(rtrim(SC_WORKSPACE_DIR, '/\\')) === self::CANONICAL_PLUGIN_ROOT;
    $current_style = SC_WORKSPACE_DIR . 'assets/css/workspace-v' . SC_WORKSPACE_VERSION . '.css';
    $current_script = SC_WORKSPACE_DIR . 'assets/js/workspace-v' . SC_WORKSPACE_VERSION . '.js';
    $style_bytes = (is_file($current_style) && is_readable($current_style)) ? (int) filesize($current_style) : 0;
    $script_bytes = (is_file($current_script) && is_readable($current_script)) ? (int) filesize($current_script) : 0;
    $lifecycle_runtime = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-local-project-compat-v3690.js';
    $lifecycle_runtime_bytes = (is_file($lifecycle_runtime) && is_readable($lifecycle_runtime)) ? (int) filesize($lifecycle_runtime) : 0;
    $lifecycle_runtime_ok = $lifecycle_runtime_bytes >= self::MIN_LIFECYCLE_RUNTIME_BYTES;
    $application_kernel = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-application-kernel-v3690.js';
    $host_adapter_contract = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-host-adapter-contract-v34620.js';
    $wordpress_host_adapter = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-wordpress-host-adapter-v34620.js';
    $application_kernel_bytes = (is_file($application_kernel) && is_readable($application_kernel)) ? (int) filesize($application_kernel) : 0;
    $host_adapter_contract_bytes = (is_file($host_adapter_contract) && is_readable($host_adapter_contract)) ? (int) filesize($host_adapter_contract) : 0;
    $wordpress_host_adapter_bytes = (is_file($wordpress_host_adapter) && is_readable($wordpress_host_adapter)) ? (int) filesize($wordpress_host_adapter) : 0;
    $application_kernel_ok = $application_kernel_bytes >= self::MIN_APPLICATION_KERNEL_BYTES;
    $wordpress_thin_adapter = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-wordpress-thin-adapter-v3690.js';
    $wordpress_thin_adapter_bytes = (is_file($wordpress_thin_adapter) && is_readable($wordpress_thin_adapter)) ? (int) filesize($wordpress_thin_adapter) : 0;
    $wordpress_thin_adapter_ok = $wordpress_thin_adapter_bytes >= self::MIN_WORDPRESS_THIN_ADAPTER_BYTES;
    $runtime_asset_manifest = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-runtime-asset-manifest-v3690.js';
    $runtime_asset_manifest_bytes = (is_file($runtime_asset_manifest) && is_readable($runtime_asset_manifest)) ? (int) filesize($runtime_asset_manifest) : 0;
    $runtime_asset_manifest_ok = $runtime_asset_manifest_bytes >= self::MIN_RUNTIME_ASSET_MANIFEST_BYTES;
    $original_language_corpus_workspace = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-original-language-corpus-v3470.js';
    $original_language_corpus_workspace_bytes = (is_file($original_language_corpus_workspace) && is_readable($original_language_corpus_workspace)) ? (int) filesize($original_language_corpus_workspace) : 0;
    $original_language_corpus_workspace_ok = $original_language_corpus_workspace_bytes >= self::MIN_ORIGINAL_LANGUAGE_CORPUS_WORKSPACE_BYTES;
    $linguistic_annotation_corpus_structure_workspace = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-linguistic-annotation-corpus-structure-v3480.js';
    $linguistic_annotation_corpus_structure_workspace_bytes = (is_file($linguistic_annotation_corpus_structure_workspace) && is_readable($linguistic_annotation_corpus_structure_workspace)) ? (int) filesize($linguistic_annotation_corpus_structure_workspace) : 0;
    $linguistic_annotation_corpus_structure_workspace_ok = $linguistic_annotation_corpus_structure_workspace_bytes >= self::MIN_LINGUISTIC_ANNOTATION_CORPUS_STRUCTURE_WORKSPACE_BYTES;
    $translation_parallel_alignment_workspace = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-translation-transliteration-parallel-alignment-v3490.js';
    $translation_parallel_alignment_workspace_bytes = (is_file($translation_parallel_alignment_workspace) && is_readable($translation_parallel_alignment_workspace)) ? (int) filesize($translation_parallel_alignment_workspace) : 0;
    $translation_parallel_alignment_workspace_ok = $translation_parallel_alignment_workspace_bytes >= self::MIN_TRANSLATION_PARALLEL_ALIGNMENT_WORKSPACE_BYTES;
    $historical_language_identity_workspace = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-historical-language-script-variant-identity-v3500.js';
    $historical_language_identity_workspace_bytes = (is_file($historical_language_identity_workspace) && is_readable($historical_language_identity_workspace)) ? (int) filesize($historical_language_identity_workspace) : 0;
    $historical_language_identity_workspace_ok = $historical_language_identity_workspace_bytes >= self::MIN_HISTORICAL_LANGUAGE_IDENTITY_WORKSPACE_BYTES;
    $decoupled_production_baseline = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-decoupled-production-baseline-v346100.js';
    $decoupled_production_baseline_bytes = (is_file($decoupled_production_baseline) && is_readable($decoupled_production_baseline)) ? (int) filesize($decoupled_production_baseline) : 0;
    $decoupled_production_baseline_ok = $decoupled_production_baseline_bytes >= self::MIN_DECOUPLED_PRODUCTION_BASELINE_BYTES;
    $module_registry = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-module-registry-v34650.js';
    $module_registry_bytes = (is_file($module_registry) && is_readable($module_registry)) ? (int) filesize($module_registry) : 0;
    $module_registry_ok = $module_registry_bytes >= self::MIN_MODULE_REGISTRY_BYTES;
    $state_store_runtime = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-state-store-v34640.js';
    $persistence_runtime = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-persistence-runtime-v34640.js';
    $state_store_runtime_bytes = (is_file($state_store_runtime) && is_readable($state_store_runtime)) ? (int) filesize($state_store_runtime) : 0;
    $persistence_runtime_bytes = (is_file($persistence_runtime) && is_readable($persistence_runtime)) ? (int) filesize($persistence_runtime) : 0;
    $state_persistence_boundary_ok = $state_store_runtime_bytes >= self::MIN_STATE_STORE_RUNTIME_BYTES && $persistence_runtime_bytes >= self::MIN_PERSISTENCE_RUNTIME_BYTES;
    $project_runtime = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-project-runtime-v34630.js';
    $project_runtime_bytes = (is_file($project_runtime) && is_readable($project_runtime)) ? (int) filesize($project_runtime) : 0;
    $project_runtime_ok = $project_runtime_bytes >= self::MIN_PROJECT_RUNTIME_BYTES;
    $host_boundary_ok = $host_adapter_contract_bytes >= self::MIN_HOST_ADAPTER_CONTRACT_BYTES && $wordpress_host_adapter_bytes >= self::MIN_HOST_ADAPTER_BYTES;
    $transport_runtime = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-transport-v34620.js';
    $auth_context_runtime = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-auth-context-v34620.js';
    $api_client_runtime = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-api-client-v34620.js';
    $wordpress_transport_adapter = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-wordpress-transport-adapter-v34620.js';
    $wordpress_auth_adapter = SC_WORKSPACE_DIR . 'assets/js/sc-workspace-wordpress-auth-adapter-v34620.js';
    $transport_runtime_bytes = (is_file($transport_runtime) && is_readable($transport_runtime)) ? (int) filesize($transport_runtime) : 0;
    $auth_context_runtime_bytes = (is_file($auth_context_runtime) && is_readable($auth_context_runtime)) ? (int) filesize($auth_context_runtime) : 0;
    $api_client_runtime_bytes = (is_file($api_client_runtime) && is_readable($api_client_runtime)) ? (int) filesize($api_client_runtime) : 0;
    $wordpress_transport_adapter_bytes = (is_file($wordpress_transport_adapter) && is_readable($wordpress_transport_adapter)) ? (int) filesize($wordpress_transport_adapter) : 0;
    $wordpress_auth_adapter_bytes = (is_file($wordpress_auth_adapter) && is_readable($wordpress_auth_adapter)) ? (int) filesize($wordpress_auth_adapter) : 0;
    $transport_auth_api_boundary_ok = $transport_runtime_bytes >= self::MIN_TRANSPORT_RUNTIME_BYTES && $auth_context_runtime_bytes >= self::MIN_AUTH_CONTEXT_RUNTIME_BYTES && $api_client_runtime_bytes >= self::MIN_API_CLIENT_RUNTIME_BYTES && $wordpress_transport_adapter_bytes >= self::MIN_TRANSPORT_ADAPTER_BYTES && $wordpress_auth_adapter_bytes >= self::MIN_AUTH_ADAPTER_BYTES;
    $asset_continuity_ok = $style_bytes >= self::MIN_CURRENT_STYLE_BYTES && $script_bytes >= self::MIN_CURRENT_SCRIPT_BYTES;
    $previous_style = SC_WORKSPACE_DIR . 'assets/css/workspace-v' . self::PREVIOUS_RELEASE . '.css';
    $previous_script = SC_WORKSPACE_DIR . 'assets/js/workspace-v' . self::PREVIOUS_RELEASE . '.js';
    $previous_style_bytes = (is_file($previous_style) && is_readable($previous_style)) ? (int) filesize($previous_style) : 0;
    $previous_script_bytes = (is_file($previous_script) && is_readable($previous_script)) ? (int) filesize($previous_script) : 0;
    $previous_asset_continuity_ok = $previous_style_bytes >= self::MIN_CURRENT_STYLE_BYTES && $previous_script_bytes >= self::MIN_CURRENT_SCRIPT_BYTES;
    global $wp_version;
    $wp_ok = !isset($wp_version) || version_compare((string) $wp_version, self::REQUIRED_WORDPRESS, '>=');
    $php_ok = version_compare(PHP_VERSION, self::REQUIRED_PHP, '>=');
    return array(
        'schema' => self::SCHEMA,
        'workspace_version' => SC_WORKSPACE_VERSION,
        'ok' => empty($missing) && $wp_ok && $php_ok && $canonical_root && $asset_continuity_ok && $previous_asset_continuity_ok && $lifecycle_runtime_ok && $application_kernel_ok && $wordpress_thin_adapter_ok && $runtime_asset_manifest_ok && $original_language_corpus_workspace_ok && $linguistic_annotation_corpus_structure_workspace_ok && $translation_parallel_alignment_workspace_ok && $historical_language_identity_workspace_ok && $decoupled_production_baseline_ok && $module_registry_ok && $project_runtime_ok && $state_persistence_boundary_ok && $host_boundary_ok && $transport_auth_api_boundary_ok,
        'required_file_count' => count(self::required_files()),
        'missing_required_file_count' => count($missing),
        'missing_required_files' => $missing,
        'canonical_plugin_root' => $canonical_root,
        'canonical_plugin_root_expected' => self::CANONICAL_PLUGIN_ROOT,
        'current_style_bytes' => $style_bytes,
        'current_script_bytes' => $script_bytes,
        'minimum_current_style_bytes' => self::MIN_CURRENT_STYLE_BYTES,
        'minimum_current_script_bytes' => self::MIN_CURRENT_SCRIPT_BYTES,
        'lifecycle_runtime_bytes' => $lifecycle_runtime_bytes,
        'minimum_lifecycle_runtime_bytes' => self::MIN_LIFECYCLE_RUNTIME_BYTES,
        'lifecycle_runtime_ok' => $lifecycle_runtime_ok,
        'application_kernel_bytes' => $application_kernel_bytes,
        'application_kernel_ok' => $application_kernel_ok,
        'wordpress_thin_adapter_bytes' => $wordpress_thin_adapter_bytes,
        'wordpress_thin_adapter_ok' => $wordpress_thin_adapter_ok,
        'runtime_asset_manifest_bytes' => $runtime_asset_manifest_bytes,
        'runtime_asset_manifest_ok' => $runtime_asset_manifest_ok,
        'original_language_corpus_workspace_bytes' => $original_language_corpus_workspace_bytes,
        'original_language_corpus_workspace_ok' => $original_language_corpus_workspace_ok,
        'linguistic_annotation_corpus_structure_workspace_bytes' => $linguistic_annotation_corpus_structure_workspace_bytes,
        'linguistic_annotation_corpus_structure_workspace_ok' => $linguistic_annotation_corpus_structure_workspace_ok,
        'translation_parallel_alignment_workspace_bytes' => $translation_parallel_alignment_workspace_bytes,
        'translation_parallel_alignment_workspace_ok' => $translation_parallel_alignment_workspace_ok,
        'historical_language_identity_workspace_bytes' => $historical_language_identity_workspace_bytes,
        'historical_language_identity_workspace_ok' => $historical_language_identity_workspace_ok,
        'decoupled_production_baseline_bytes' => $decoupled_production_baseline_bytes,
        'decoupled_production_baseline_ok' => $decoupled_production_baseline_ok,
        'module_registry_bytes' => $module_registry_bytes,
        'module_registry_ok' => $module_registry_ok,
        'state_store_runtime_bytes' => $state_store_runtime_bytes,
        'persistence_runtime_bytes' => $persistence_runtime_bytes,
        'state_persistence_boundary_ok' => $state_persistence_boundary_ok,
        'project_runtime_bytes' => $project_runtime_bytes,
        'minimum_project_runtime_bytes' => self::MIN_PROJECT_RUNTIME_BYTES,
        'project_runtime_ok' => $project_runtime_ok,
        'host_adapter_contract_bytes' => $host_adapter_contract_bytes,
        'wordpress_host_adapter_bytes' => $wordpress_host_adapter_bytes,
        'host_boundary_ok' => $host_boundary_ok,
        'transport_runtime_bytes' => $transport_runtime_bytes,
        'auth_context_runtime_bytes' => $auth_context_runtime_bytes,
        'api_client_runtime_bytes' => $api_client_runtime_bytes,
        'wordpress_transport_adapter_bytes' => $wordpress_transport_adapter_bytes,
        'wordpress_auth_adapter_bytes' => $wordpress_auth_adapter_bytes,
        'transport_auth_api_boundary_ok' => $transport_auth_api_boundary_ok,
        'asset_continuity_ok' => $asset_continuity_ok,
        'previous_release' => self::PREVIOUS_RELEASE,
        'previous_style_bytes' => $previous_style_bytes,
        'previous_script_bytes' => $previous_script_bytes,
        'previous_asset_continuity_ok' => $previous_asset_continuity_ok,
        'wordpress_supported' => $wp_ok,
        'php_supported' => $php_ok,
        'project_data_inspected' => false,
        'project_data_mutated' => false,
    );
}

    public static function observe($source = 'runtime') {
        if (!function_exists('get_option') || !function_exists('update_option')) {
            return array();
        }
        $state = get_option(self::STATE_OPTION, array());
        if (!is_array($state)) {
            $state = array();
        }
        if (isset($state['workspace_version']) && (string) $state['workspace_version'] === SC_WORKSPACE_VERSION) {
            return $state;
        }
        $previous = isset($state['workspace_version']) ? (string) $state['workspace_version'] : '';
        $entry = array(
            'schema' => self::SCHEMA,
            'from_version' => $previous,
            'to_version' => SC_WORKSPACE_VERSION,
            'source' => sanitize_key((string) $source),
            'observed_at' => gmdate('c'),
        );
        $history = get_option(self::HISTORY_OPTION, array());
        if (!is_array($history)) {
            $history = array();
        }
        $history[] = $entry;
        if (count($history) > self::MAX_HISTORY) {
            $history = array_slice($history, -self::MAX_HISTORY);
        }
        update_option(self::HISTORY_OPTION, $history, false);
        $next = array(
            'schema' => self::SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'previous_observed_version' => $previous,
            'source' => $entry['source'],
            'first_seen_at' => $entry['observed_at'],
            'history_count' => count($history),
        );
        update_option(self::STATE_OPTION, $next, false);
        return $next;
    }

    public static function activation_preflight() {
        return self::preflight();
    }

    public static function activate() {
        $preflight = self::activation_preflight();
        if (empty($preflight['ok'])) {
            return $preflight;
        }
        self::observe('activation');
        return $preflight;
    }

    public static function diagnostics() {
        $preflight = self::preflight();
        $state = function_exists('get_option') ? get_option(self::STATE_OPTION, array()) : array();
        if (!is_array($state)) {
            $state = array();
        }
        $history = function_exists('get_option') ? get_option(self::HISTORY_OPTION, array()) : array();
        if (!is_array($history)) {
            $history = array();
        }
        $marker_version = isset($state['workspace_version']) ? (string) $state['workspace_version'] : '';
        $marker_matches = $marker_version === SC_WORKSPACE_VERSION;
        $registry_pending = false;
        if (class_exists('SC_Workspace_Registry') && function_exists('get_option')) {
            $registry_pending = get_option(SC_Workspace_Registry::PENDING_KEY, '') === '1';
        }
        $ready = !empty($preflight['ok']) && $marker_matches && !$registry_pending;
        return array(
            'schema' => self::SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release_stage' => 'stable-product',
            'previous_release' => self::PREVIOUS_RELEASE,
            'state' => $ready ? 'server-ready' : 'attention',
            'server_ready' => $ready,
            'required_files_complete' => empty($preflight['missing_required_file_count']),
            'missing_required_file_count' => (int) $preflight['missing_required_file_count'],
            'missing_required_files' => $preflight['missing_required_files'],
            'canonical_plugin_root' => !empty($preflight['canonical_plugin_root']),
            'canonical_plugin_root_expected' => isset($preflight['canonical_plugin_root_expected']) ? (string) $preflight['canonical_plugin_root_expected'] : self::CANONICAL_PLUGIN_ROOT,
            'asset_continuity_ok' => !empty($preflight['asset_continuity_ok']),
            'current_style_bytes' => isset($preflight['current_style_bytes']) ? (int) $preflight['current_style_bytes'] : 0,
            'current_script_bytes' => isset($preflight['current_script_bytes']) ? (int) $preflight['current_script_bytes'] : 0,
            'previous_asset_continuity_ok' => !empty($preflight['previous_asset_continuity_ok']),
            'previous_style_bytes' => isset($preflight['previous_style_bytes']) ? (int) $preflight['previous_style_bytes'] : 0,
            'previous_script_bytes' => isset($preflight['previous_script_bytes']) ? (int) $preflight['previous_script_bytes'] : 0,
            'runtime_marker_present' => $marker_version !== '',
            'runtime_marker_version' => $marker_version,
            'runtime_marker_matches' => $marker_matches,
            'previous_observed_version' => isset($state['previous_observed_version']) ? (string) $state['previous_observed_version'] : '',
            'transition_source' => isset($state['source']) ? (string) $state['source'] : '',
            'history_count' => min(count($history), self::MAX_HISTORY),
            'registry_pending' => $registry_pending,
            'wordpress_supported' => !empty($preflight['wordpress_supported']),
            'php_supported' => !empty($preflight['php_supported']),
            'expected_script' => 'workspace-v' . SC_WORKSPACE_VERSION . '.js',
            'expected_style' => 'workspace-v' . SC_WORKSPACE_VERSION . '.css',
            'asset_cache_strategy' => 'versioned-filename-plus-version-query',
            'rollback_release' => self::ROLLBACK_RELEASE,
            'rollback_schema_compatible' => true,
            'automatic_cache_purge' => false,
            'automatic_rollback' => false,
            'project_data_inspected' => false,
            'project_data_mutated' => false,
        );
    }

    public static function admin_notice() {
        if (!function_exists('current_user_can') || !current_user_can('manage_options')) {
            return;
        }
        $diagnostics = self::diagnostics();
        if (!empty($diagnostics['server_ready'])) {
            return;
        }
        $missing = (int) $diagnostics['missing_required_file_count'];
        $message = 'Sustainable Catalyst Workspace deployment warning: the active release does not pass the current stable server package check.';
        if ($missing > 0) {
            $message .= ' ' . $missing . ' required release file(s) are missing or unreadable.';
        }
        if (empty($diagnostics['canonical_plugin_root'])) {
            $message .= ' The plugin directory is not the canonical sustainable-catalyst-workspace root.';
        }
        if (empty($diagnostics['asset_continuity_ok'])) {
            $message .= ' Current versioned frontend assets are missing or below continuity thresholds.';
        }
        if (empty($diagnostics['previous_asset_continuity_ok'])) {
            $message .= ' Previous-release frontend continuity assets are missing or below thresholds.';
        }
        if (!empty($diagnostics['registry_pending'])) {
            $message .= ' Product Registry registration is still pending.';
        }
        echo '<div class="notice notice-error"><p><strong>' . esc_html($message) . '</strong> Verify the release package before continuing upgrades. Browser-local projects are not modified by this check.</p></div>';
    }

    public static function contract() {
        return array(
            'schema' => self::CONTRACT_SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'WordPress & Deployment Hardening',
            'release_candidate' => true,
            'feature_freeze' => true,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'project_export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'safe_bootstrap_guard' => true,
            'activation_preflight' => true,
            'bounded_deployment_history' => true,
            'deployment_history_limit' => self::MAX_HISTORY,
            'server_package_integrity_check' => true,
            'canonical_plugin_root_required' => true,
            'frontend_asset_continuity_check' => true,
            'previous_release_asset_continuity_required' => true,
            'previous_release_asset_version' => self::PREVIOUS_RELEASE,
            'minimum_current_style_bytes' => self::MIN_CURRENT_STYLE_BYTES,
            'minimum_current_script_bytes' => self::MIN_CURRENT_SCRIPT_BYTES,
            'mixed_version_browser_detection' => true,
            'versioned_asset_filenames' => true,
            'version_query_required' => true,
            'project_lifecycle_runtime_release_specific' => true,
            'project_lifecycle_runtime_cache_busted' => true,
            'application_kernel_required' => true,
            'project_runtime_extracted' => true,
            'project_runtime_host_neutral' => true,
            'compatibility_bundle_owns_project_lifecycle' => false,
            'host_adapter_contract_required' => true,
            'wordpress_required_for_application_kernel' => false,
            'core_wordpress_imports' => 0,
            'transport_decoupled_from_host_adapter' => true,
            'authentication_decoupled_from_transport' => true,
            'api_client_host_neutral' => true,
            'standalone_direct_transport' => true,
            'wordpress_proxy_transport_adapter' => true,
            'project_lifecycle_runtime_minimum_bytes' => self::MIN_LIFECYCLE_RUNTIME_BYTES,
            'registry_pending_detection' => true,
            'rollback_release' => self::ROLLBACK_RELEASE,
            'rollback_schema_compatible' => true,
            'rollback_artifact_required' => true,
            'automatic_cache_purge' => false,
            'automatic_rollback' => false,
            'automatic_project_migration' => false,
            'canonical_mutation' => false,
            'project_data_inspected' => false,
            'telemetry' => false,
        );
    }
}
