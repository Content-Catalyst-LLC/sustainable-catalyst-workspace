<?php
error_reporting(E_ALL);
define('ABSPATH', __DIR__);
define('SC_WORKSPACE_VERSION', '0.1.0');
$GLOBALS['scw_options'] = array();
$GLOBALS['scw_actions'] = array();
function get_option($key, $default = false) { return array_key_exists($key, $GLOBALS['scw_options']) ? $GLOBALS['scw_options'][$key] : $default; }
function update_option($key, $value, $autoload = null) { $GLOBALS['scw_options'][$key] = $value; return true; }
function add_option($key, $value, $deprecated = '', $autoload = 'yes') { if (array_key_exists($key, $GLOBALS['scw_options'])) return false; $GLOBALS['scw_options'][$key] = $value; return true; }
function delete_option($key) { unset($GLOBALS['scw_options'][$key]); return true; }
function do_action($name, ...$args) { $GLOBALS['scw_actions'][] = array($name, $args); }
require dirname(__DIR__) . '/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php';

function assert_true($condition, $message) { if (!$condition) { fwrite(STDERR, "FAIL: $message\n"); exit(1); } }

// Direct associative registry: preserve existing products and add Workspace.
$GLOBALS['scw_options'] = array(
    SC_Workspace_Registry::OPTION_KEY => array(
        'catalyst-intelligence' => array('canonical_id' => 'catalyst-intelligence', 'name' => 'Catalyst Intelligence Platform', 'display_order' => 410),
    ),
);
assert_true(SC_Workspace_Registry::register_product(), 'direct registry registration');
$r = get_option(SC_Workspace_Registry::OPTION_KEY);
assert_true(isset($r['catalyst-intelligence']), 'existing commercial record preserved');
assert_true(isset($r['sustainable-catalyst-workspace']), 'Workspace added to direct registry');
assert_true($r['sustainable-catalyst-workspace']['family'] === 'commercial', 'Workspace commercial family');
assert_true($r['sustainable-catalyst-workspace']['display_order'] === 400, 'Workspace ordered before Catalyst Intelligence');
assert_true($r['sustainable-catalyst-workspace']['public_version'] === '0.1.0', 'Workspace version');
assert_true($r['sustainable-catalyst-workspace']['commercial'] === '1', 'Commercial release true');
assert_true($r['sustainable-catalyst-workspace']['public_interest'] === '1', 'Free/public-interest flag true');

// Wrapper/list registry: preserve wrapper metadata and append Workspace exactly once.
$GLOBALS['scw_options'] = array(
    SC_Workspace_Registry::OPTION_KEY => array(
        'schema' => 'scfs-canonical-product-registry/2.1',
        'products' => array(array('canonical_id' => 'catalyst-intelligence', 'display_order' => 410)),
    ),
);
assert_true(SC_Workspace_Registry::register_product(), 'list registry registration');
assert_true(SC_Workspace_Registry::register_product(), 'list registry idempotent update');
$r = get_option(SC_Workspace_Registry::OPTION_KEY);
assert_true($r['schema'] === 'scfs-canonical-product-registry/2.1', 'wrapper schema preserved');
$count = 0;
foreach ($r['products'] as $product) { if (($product['canonical_id'] ?? '') === 'sustainable-catalyst-workspace') $count++; }
assert_true($count === 1, 'Workspace appears exactly once');

// Missing registry: fail closed and leave a pending registration marker.
$GLOBALS['scw_options'] = array();
assert_true(SC_Workspace_Registry::register_product() === false, 'missing registry does not fabricate a catalog');
assert_true(get_option(SC_Workspace_Registry::PENDING_KEY) === '1', 'pending marker is set');

echo "PASS - Workspace registry runtime migration\n";
