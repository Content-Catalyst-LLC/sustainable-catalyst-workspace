<?php
error_reporting(E_ALL);
define('ABSPATH', __DIR__);
define('SC_WORKSPACE_VERSION', '0.36.0');
$GLOBALS['logged_in'] = true;
$GLOBALS['user_meta'] = array();
function add_action($a,$b){}
function add_shortcode($a,$b){}
function is_user_logged_in(){ return $GLOBALS['logged_in']; }
function current_user_can($cap){ return $GLOBALS['logged_in']; }
function get_current_user_id(){ return 42; }
function get_user_meta($uid,$key,$single=true){ return $GLOBALS['user_meta'][$uid][$key] ?? ''; }
function update_user_meta($uid,$key,$value){ $GLOBALS['user_meta'][$uid][$key]=$value; return true; }
function sanitize_key($s){ return preg_replace('/[^a-z0-9_\-.]/','', strtolower((string)$s)); }
function sanitize_text_field($s){ return trim(strip_tags((string)$s)); }
function wp_json_encode($v,$flags=0){ return json_encode($v,$flags); }
function rest_ensure_response($v){ return $v; }
class WP_Error { public $code,$message,$data; function __construct($c,$m,$d=array()){ $this->code=$c;$this->message=$m;$this->data=$d; } }
class Req implements ArrayAccess {
  private $json; private $params;
  function __construct($json=array(),$params=array()){ $this->json=$json;$this->params=$params; }
  function get_json_params(){ return $this->json; }
  public function offsetExists($o): bool { return isset($this->params[$o]); }
  public function offsetGet($o): mixed { return $this->params[$o] ?? null; }
  public function offsetSet($o,$v): void { $this->params[$o]=$v; }
  public function offsetUnset($o): void { unset($this->params[$o]); }
}
require dirname(__DIR__) . '/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php';
function ok($cond,$msg){ if(!$cond){ fwrite(STDERR,"FAIL: $msg\n"); exit(1);} }
$w=SC_Workspace::instance();
ok($w->cloud_permission()===true,'authenticated permission');
$GLOBALS['logged_in']=false; ok($w->cloud_permission()===false,'anonymous permission denied'); $GLOBALS['logged_in']=true;
$project=array('schema'=>'sc-workspace-project/14.0','id'=>'scwp-demo','title'=>'Demo','updatedAt'=>'2026-08-09T00:00:00Z','objects'=>array(array('id'=>'scwo-1','schema'=>'sc-workspace-object/1.0','title'=>'Evidence')));
$payload=array('schema'=>'sc-workspace-cloud-backup/1.0','sourceProjectId'=>'scwp-demo','projectTitle'=>'Demo','clientUpdatedAt'=>'2026-08-09T00:00:00Z','project'=>$project);
$res=$w->cloud_project_store(new Req($payload)); ok(is_array($res)&&$res['ok']===true,'backup stored'); ok(strlen($res['item']['fingerprint'])===64,'sha256 fingerprint'); ok(($res['item']['revision']??0)===1,'manual backup creates revision 1');
$list=$w->cloud_projects_list(); ok(count($list['items'])===1,'backup listed'); ok(!isset($list['items'][0]['package']),'list metadata excludes content');
$get=$w->cloud_project_get(new Req(array(),array('project_id'=>'scwp-demo'))); ok(($get['package']['project']['title']??'')==='Demo','backup retrieved');
$del=$w->cloud_project_delete(new Req(array(),array('project_id'=>'scwp-demo'))); ok($del['deleted']===true,'backup deleted'); ok(count($w->cloud_projects_list()['items'])===0,'backup index empty');
echo "PASS - v0.33.0 account cloud persistence runtime\n";
