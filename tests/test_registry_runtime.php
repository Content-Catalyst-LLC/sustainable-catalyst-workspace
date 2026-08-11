<?php
error_reporting(E_ALL);
define('ABSPATH', __DIR__);
define('SC_WORKSPACE_VERSION', '0.61.0');
$GLOBALS['scw_options'] = array();
$GLOBALS['scw_actions'] = array();
function get_option($key, $default = false) { return array_key_exists($key, $GLOBALS['scw_options']) ? $GLOBALS['scw_options'][$key] : $default; }
function update_option($key, $value, $autoload = null) { $GLOBALS['scw_options'][$key] = $value; return true; }
function add_option($key, $value, $deprecated = '', $autoload = 'yes') { if (array_key_exists($key, $GLOBALS['scw_options'])) return false; $GLOBALS['scw_options'][$key] = $value; return true; }
function delete_option($key) { unset($GLOBALS['scw_options'][$key]); return true; }
function do_action($name, ...$args) { $GLOBALS['scw_actions'][] = array($name, $args); }
require dirname(__DIR__) . '/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php';

function assert_true($condition, $message) { if (!$condition) { fwrite(STDERR, "FAIL: $message\n"); exit(1); } }

$before = array(
    'catalyst-intelligence' => array('canonical_id' => 'catalyst-intelligence', 'name' => 'Catalyst Intelligence Platform', 'display_order' => 410),
    'sustainable-catalyst-workspace' => array('canonical_id' => 'sustainable-catalyst-workspace', 'public_version' => '0.8.0', 'custom_preserved' => 'yes'),
);
$GLOBALS['scw_options'] = array(SC_Workspace_Registry::OPTION_KEY => $before);
assert_true(SC_Workspace_Registry::register_product(), 'direct registry registration');
$r = get_option(SC_Workspace_Registry::OPTION_KEY);
assert_true(isset($r['catalyst-intelligence']), 'existing commercial record preserved');
assert_true(isset($r['sustainable-catalyst-workspace']), 'Workspace exists in direct registry');
assert_true($r['sustainable-catalyst-workspace']['public_version'] === '0.61.0', 'Workspace version updated');
assert_true($r['sustainable-catalyst-workspace']['previous_version'] === '0.60.0', 'previous version recorded');
assert_true($r['sustainable-catalyst-workspace']['display_order'] === 400, 'Workspace remains before Catalyst Intelligence');
assert_true($r['sustainable-catalyst-workspace']['custom_preserved'] === 'yes', 'unknown existing fields preserved');
assert_true(get_option(SC_Workspace_Registry::BACKUP_KEY) === $before, 'pre-v0.61.0 registry backup created');

$GLOBALS['scw_options'] = array(
    SC_Workspace_Registry::OPTION_KEY => array(
        'schema' => 'scfs-canonical-product-registry/2.1',
        'products' => array(
            array('canonical_id' => 'sustainable-catalyst-workspace', 'public_version' => '0.8.0'),
            array('canonical_id' => 'catalyst-intelligence', 'display_order' => 410),
        ),
    ),
);
assert_true(SC_Workspace_Registry::register_product(), 'list registry update');
assert_true(SC_Workspace_Registry::register_product(), 'list registry idempotent update');
$r = get_option(SC_Workspace_Registry::OPTION_KEY);
assert_true($r['schema'] === 'scfs-canonical-product-registry/2.1', 'wrapper schema preserved');
$count = 0;
foreach ($r['products'] as $product) {
    if (($product['canonical_id'] ?? '') === 'sustainable-catalyst-workspace') {
        $count++;
        assert_true($product['public_version'] === '0.61.0', 'list Workspace version updated');
    }
}
assert_true($count === 1, 'Workspace appears exactly once');

$GLOBALS['scw_options'] = array();
assert_true(SC_Workspace_Registry::register_product() === false, 'missing registry does not fabricate a catalog');
assert_true(get_option(SC_Workspace_Registry::PENDING_KEY) === '1', 'v0.61.0 pending marker is set');

echo "PASS - Workspace v0.61.0 registry runtime migration\n";
