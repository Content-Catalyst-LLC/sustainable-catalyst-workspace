<?php
/**
 * Plugin Name: Sustainable Catalyst Workspace
 * Plugin URI: https://sustainablecatalyst.com/platform/
 * Version: 0.73.0
 * Author: Content Catalyst LLC
 * Text Domain: sustainable-catalyst-workspace
 * Requires at least: 6.4
 * Requires PHP: 8.0
 * Description: Free public local-first workspace for research, evidence, analysis, decisions, knowledge, interoperability, and explicit Sustainable Catalyst tool handoffs.
 */


if (!defined('ABSPATH')) {
    exit;
}

define('SC_WORKSPACE_VERSION', '0.73.0');
define('SC_WORKSPACE_FILE', __FILE__);
define('SC_WORKSPACE_DIR', plugin_dir_path(__FILE__));
define('SC_WORKSPACE_URL', plugin_dir_url(__FILE__));

require_once SC_WORKSPACE_DIR . 'includes/class-sc-workspace-registry.php';
require_once SC_WORKSPACE_DIR . 'includes/class-sc-workspace-platform.php';
require_once SC_WORKSPACE_DIR . 'includes/class-sc-workspace.php';

register_activation_hook(__FILE__, array('SC_Workspace_Registry', 'activate'));

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
