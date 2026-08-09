<?php
error_reporting(E_ALL);
define('ABSPATH', __DIR__ . '/');
define('SC_WORKSPACE_VERSION', '0.31.0');
$GLOBALS['opts'] = array();
$GLOBALS['updates'] = array();
class WP_Error { public $code; public $message; public function __construct($c,$m){$this->code=$c;$this->message=$m;} }
function is_wp_error($v){ return $v instanceof WP_Error; }
function add_action($a,$b){}
function get_option($k,$d=null){ return array_key_exists($k,$GLOBALS['opts']) ? $GLOBALS['opts'][$k] : $d; }
function add_option($k,$v,$deprecated='',$autoload='yes'){ if(array_key_exists($k,$GLOBALS['opts'])) return false; $GLOBALS['opts'][$k]=$v; return true; }
function update_option($k,$v,$autoload=null){ $GLOBALS['opts'][$k]=$v; return true; }
function delete_option($k){ unset($GLOBALS['opts'][$k]); return true; }
function get_page_template_slug($id){ return 'templates/platform.php'; }
function wp_update_post($data,$wp_error=false){ $GLOBALS['updates'][]=$data; return $data['ID']; }
function flush_rewrite_rules($hard=true){}
function home_url($path=''){ return 'https://example.test'.$path; }
function assert_true($c,$m){ if(!$c){fwrite(STDERR,"FAIL - $m\n");exit(1);} }
require dirname(__DIR__) . '/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-platform.php';
$page=(object)array('ID'=>42,'post_title'=>'Platform','post_content'=>'Original platform content','post_excerpt'=>'Original excerpt','post_name'=>'platform','post_parent'=>0,'post_status'=>'publish');
$result=SC_Workspace_Platform::perform_conversion($page);
assert_true(!is_wp_error($result),'conversion succeeds');
assert_true($result['page_id']===42,'page ID retained');
assert_true($GLOBALS['updates'][0]['ID']===42,'same page updated');
assert_true($GLOBALS['updates'][0]['post_title']==='Workspace','title becomes Workspace');
assert_true($GLOBALS['updates'][0]['post_content']==='[sc_workspace_platform]','dedicated shortcode installed');
assert_true(!isset($GLOBALS['updates'][0]['post_name']),'slug not rewritten');
assert_true(SC_Workspace_Platform::is_converted(),'conversion state recorded');
$backup=get_option($result['backup_key']);
assert_true($backup['title']==='Platform' && $backup['content']==='Original platform content','snapshot captures original content');
$restored=SC_Workspace_Platform::perform_restore();
assert_true($restored===true,'restore succeeds');
$last=end($GLOBALS['updates']);
assert_true($last['ID']===42 && $last['post_title']==='Platform' && $last['post_content']==='Original platform content','restore uses original title/content');
assert_true(SC_Workspace_Platform::is_converted()===false,'conversion state cleared');
echo "PASS - Workspace v0.22.0 Platform conversion runtime\n";
