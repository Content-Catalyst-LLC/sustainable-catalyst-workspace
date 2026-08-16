<?php
/**
 * Plugin Name: Sustainable Catalyst Workspace
 * Plugin URI: https://sustainablecatalyst.com/platform/
 * Version: 2.0.1
 * Author: Content Catalyst LLC
 * Text Domain: sustainable-catalyst-workspace
 * Requires at least: 6.4
 * Requires PHP: 8.0
 * Description: Free public local-first workspace for research, evidence, analysis, decisions, knowledge, interoperability, and explicit Sustainable Catalyst tool handoffs.
 */


if (!defined('ABSPATH')) {
    exit;
}

define('SC_WORKSPACE_VERSION', '2.0.1');
define('SC_WORKSPACE_FILE', __FILE__);
define('SC_WORKSPACE_DIR', plugin_dir_path(__FILE__));
define('SC_WORKSPACE_URL', plugin_dir_url(__FILE__));

/**
 * Fail closed when an uploaded/replaced plugin is incomplete. Missing bootstrap
 * files must not become a site-wide fatal error.
 */
function sc_workspace_bootstrap_failure($missing_files) {
    $GLOBALS['sc_workspace_bootstrap_failure_files'] = array_values((array) $missing_files);
    add_action('admin_notices', function () {
        if (!current_user_can('manage_options')) {
            return;
        }
        $count = count(isset($GLOBALS['sc_workspace_bootstrap_failure_files']) ? $GLOBALS['sc_workspace_bootstrap_failure_files'] : array());
        echo '<div class="notice notice-error"><p><strong>Sustainable Catalyst Workspace bootstrap warning:</strong> the v2.0.1 plugin package is incomplete (' . esc_html((string) $count) . ' required core file(s) unavailable). Workspace was not bootstrapped. Reinstall the complete release package; browser-local projects were not touched.</p></div>';
    });
}

$sc_workspace_bootstrap_files = array(
    'deployment' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-deployment.php',
    'production_certification' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-production-certification.php',
    'production_signoff' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-production-signoff.php',
    'ga_readiness' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-ga-readiness.php',
    'general_availability' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-general-availability.php',
    'ga_stabilization' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-ga-stabilization.php',
    'workspace_home' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-home.php',
    'universal_search' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-universal-search.php',
    'library_continuity' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-library-continuity.php',
    'knowledge_graph_explorer' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-knowledge-graph-explorer.php',
    'lab_integration' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-lab-integration.php',
    'workbench_decision_roundtrip' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-workbench-decision-roundtrip.php',
    'cross_device_production' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-cross-device-production.php',
    'review_rooms' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-review-rooms.php',
    'institutional_audit_studio' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-institutional-audit-studio.php',
    'research_operations' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-research-operations.php',
    'developer_api' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-developer-api.php',
    'institutional_scale_hardening' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-institutional-scale-hardening.php',
    'connected_intelligence' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-connected-intelligence.php',
    'public_research_packages' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-public-research-packages.php',
    'product_maturity' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-product-maturity.php',
    'connected_knowledge' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-connected-knowledge.php',
    'button_system' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-button-system.php',
    'registry' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-registry.php',
    'platform' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace-platform.php',
    'workspace' => SC_WORKSPACE_DIR . 'includes/class-sc-workspace.php',
);
$sc_workspace_bootstrap_missing = array();
foreach ($sc_workspace_bootstrap_files as $sc_workspace_label => $sc_workspace_file) {
    if (!is_file($sc_workspace_file) || !is_readable($sc_workspace_file)) {
        $sc_workspace_bootstrap_missing[] = $sc_workspace_label;
    }
}
if ($sc_workspace_bootstrap_missing) {
    sc_workspace_bootstrap_failure($sc_workspace_bootstrap_missing);
    return;
}

require_once $sc_workspace_bootstrap_files['deployment'];
require_once $sc_workspace_bootstrap_files['production_certification'];
require_once $sc_workspace_bootstrap_files['production_signoff'];
require_once $sc_workspace_bootstrap_files['ga_readiness'];
require_once $sc_workspace_bootstrap_files['general_availability'];
require_once $sc_workspace_bootstrap_files['ga_stabilization'];
require_once $sc_workspace_bootstrap_files['workspace_home'];
require_once $sc_workspace_bootstrap_files['universal_search'];
require_once $sc_workspace_bootstrap_files['library_continuity'];
require_once $sc_workspace_bootstrap_files['knowledge_graph_explorer'];
require_once $sc_workspace_bootstrap_files['lab_integration'];
require_once $sc_workspace_bootstrap_files['workbench_decision_roundtrip'];
require_once $sc_workspace_bootstrap_files['cross_device_production'];
require_once $sc_workspace_bootstrap_files['review_rooms'];
require_once $sc_workspace_bootstrap_files['institutional_audit_studio'];
require_once $sc_workspace_bootstrap_files['research_operations'];
require_once $sc_workspace_bootstrap_files['developer_api'];
require_once $sc_workspace_bootstrap_files['institutional_scale_hardening'];
require_once $sc_workspace_bootstrap_files['connected_intelligence'];
require_once $sc_workspace_bootstrap_files['public_research_packages'];
require_once $sc_workspace_bootstrap_files['product_maturity'];
require_once $sc_workspace_bootstrap_files['connected_knowledge'];
require_once $sc_workspace_bootstrap_files['button_system'];
require_once $sc_workspace_bootstrap_files['registry'];
require_once $sc_workspace_bootstrap_files['platform'];
require_once $sc_workspace_bootstrap_files['workspace'];

function sc_workspace_activate() {
    $preflight = SC_Workspace_Deployment_Hardening::activate();
    if (empty($preflight['ok'])) {
        if (function_exists('deactivate_plugins')) {
            deactivate_plugins(plugin_basename(__FILE__));
        }
        $reason = !empty($preflight['missing_required_file_count'])
            ? ((int) $preflight['missing_required_file_count']) . ' required release file(s) are missing or unreadable.'
            : 'The declared WordPress/PHP runtime requirements are not satisfied.';
        wp_die(esc_html('Sustainable Catalyst Workspace v2.0.1 activation preflight failed: ' . $reason));
    }
    SC_Workspace_Registry::activate();
}
register_activation_hook(__FILE__, 'sc_workspace_activate');

SC_Workspace_Deployment_Hardening::observe('runtime');
add_action('admin_notices', array('SC_Workspace_Deployment_Hardening', 'admin_notice'));
SC_Workspace_Platform::instance();
SC_Workspace::instance();

/** Public producer helper URL for compatible Sustainable Catalyst tools. */
function sc_workspace_return_adapter_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-return-adapter-v1.js';
}

/** Public Responsible AI adapter helper URL for compatible same-origin tools. */
function sc_workspace_ai_adapter_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-ai-adapter-v1.js';
}

/** Public Source Capture adapter helper URL for compatible same-origin research surfaces. */
function sc_workspace_source_capture_adapter_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-source-capture-v1.js';
}

/** Public Grounded Notebook Assistance adapter helper URL for compatible same-origin research surfaces. */
function sc_workspace_notebook_assistance_adapter_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-notebook-assistance-adapter-v1.js';
}

/** Public read-only static embed renderer URL for explicitly disclosed Workspace projections. */
function sc_workspace_api_embed_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-api-embed-v1.js';
}

/** Public browser-local Developer SDK helper URL for explicitly granted extensions. */
function sc_workspace_developer_sdk_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-developer-sdk-v1.js';
}
