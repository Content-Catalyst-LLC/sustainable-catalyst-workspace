<?php
/**
 * Plugin Name: Sustainable Catalyst Workspace
 * Plugin URI: https://sustainablecatalyst.com/platform/
 * Description: Free public research, evidence, analysis, decision, and structured-thinking workspace with traceable provenance, reproducibility records, and local-first persistence.
 * Version: 0.9.0.1
 * Author: Content Catalyst LLC
 * Text Domain: sustainable-catalyst-workspace
 * Requires at least: 6.4
 * Requires PHP: 8.0
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SC_WORKSPACE_VERSION', '0.9.0.1');
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
