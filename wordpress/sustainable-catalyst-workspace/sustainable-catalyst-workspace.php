<?php
/**
 * Plugin Name: Sustainable Catalyst Workspace
 * Plugin URI: https://sustainablecatalyst.com/platform/workspace/
 * Description: Free public workspace shell connecting Sustainable Catalyst research, analysis, decision, and creation tools.
 * Version: 0.1.0
 * Author: Content Catalyst LLC
 * Text Domain: sustainable-catalyst-workspace
 * Requires at least: 6.4
 * Requires PHP: 8.0
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SC_WORKSPACE_VERSION', '0.1.0');
define('SC_WORKSPACE_FILE', __FILE__);
define('SC_WORKSPACE_DIR', plugin_dir_path(__FILE__));
define('SC_WORKSPACE_URL', plugin_dir_url(__FILE__));

require_once SC_WORKSPACE_DIR . 'includes/class-sc-workspace-registry.php';
require_once SC_WORKSPACE_DIR . 'includes/class-sc-workspace.php';

register_activation_hook(__FILE__, array('SC_Workspace_Registry', 'activate'));

SC_Workspace::instance();
