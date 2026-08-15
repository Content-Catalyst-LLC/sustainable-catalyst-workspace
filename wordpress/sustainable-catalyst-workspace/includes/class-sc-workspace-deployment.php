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
    const PREVIOUS_RELEASE = '1.10.0';
    const ROLLBACK_RELEASE = '1.10.0';
    const REQUIRED_WORDPRESS = '6.4';
    const REQUIRED_PHP = '8.0';

    public static function required_files() {
        return array(
            'registry' => 'includes/class-sc-workspace-registry.php',
            'platform' => 'includes/class-sc-workspace-platform.php',
            'workspace' => 'includes/class-sc-workspace.php',
            'deployment' => 'includes/class-sc-workspace-deployment.php',
            'current_script' => 'assets/js/workspace-v1.11.0.js',
            'current_style' => 'assets/css/workspace-v1.11.0.css',
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
            'workbench_decision_roundtrip_js' => 'assets/js/sc-workspace-workbench-decision-roundtrip-v1.js',
            'lab_integration_runtime' => 'assets/js/sc-workspace-lab-integration-v1.js',
        );
    }

    public static function preflight() {
        $missing = array();
        foreach (self::required_files() as $label => $relative) {
            $path = SC_WORKSPACE_DIR . $relative;
            if (!is_file($path) || !is_readable($path)) {
                $missing[] = $label;
            }
        }
        global $wp_version;
        $wp_ok = !isset($wp_version) || version_compare((string) $wp_version, self::REQUIRED_WORDPRESS, '>=');
        $php_ok = version_compare(PHP_VERSION, self::REQUIRED_PHP, '>=');
        return array(
            'schema' => self::SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'ok' => empty($missing) && $wp_ok && $php_ok,
            'required_file_count' => count(self::required_files()),
            'missing_required_file_count' => count($missing),
            'missing_required_files' => $missing,
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
            'runtime_marker_present' => $marker_version !== '',
            'runtime_marker_version' => $marker_version,
            'runtime_marker_matches' => $marker_matches,
            'previous_observed_version' => isset($state['previous_observed_version']) ? (string) $state['previous_observed_version'] : '',
            'transition_source' => isset($state['source']) ? (string) $state['source'] : '',
            'history_count' => min(count($history), self::MAX_HISTORY),
            'registry_pending' => $registry_pending,
            'wordpress_supported' => !empty($preflight['wordpress_supported']),
            'php_supported' => !empty($preflight['php_supported']),
            'expected_script' => 'workspace-v1.10.0.js',
            'expected_style' => 'workspace-v1.10.0.css',
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
            'mixed_version_browser_detection' => true,
            'versioned_asset_filenames' => true,
            'version_query_required' => true,
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
