<?php
error_reporting(E_ALL);
define('ABSPATH', __DIR__);
define('SC_WORKSPACE_VERSION', '0.67.0');
$GLOBALS['logged_in']=true;$GLOBALS['uid']=42;$GLOBALS['user_meta']=array();
function add_action($a,$b){} function add_shortcode($a,$b){}
function is_user_logged_in(){return $GLOBALS['logged_in'];} function current_user_can($cap){return $GLOBALS['logged_in'];} function get_current_user_id(){return $GLOBALS['uid'];}
function get_user_meta($uid,$key,$single=true){return $GLOBALS['user_meta'][$uid][$key]??'';} function update_user_meta($uid,$key,$value){$GLOBALS['user_meta'][$uid][$key]=$value;return true;}
function sanitize_key($s){return preg_replace('/[^a-z0-9_\-.]/','',strtolower((string)$s));} function sanitize_text_field($s){return trim(strip_tags((string)$s));}
function wp_json_encode($v,$flags=0){return json_encode($v,$flags);} function rest_ensure_response($v){return $v;}
class WP_Error{public $code,$message,$data;function __construct($c,$m,$d=array()){$this->code=$c;$this->message=$m;$this->data=$d;}function get_error_code(){return $this->code;}function get_error_data(){return $this->data;}}
class Req implements ArrayAccess{private $json;private $params;function __construct($json=array(),$params=array()){$this->json=$json;$this->params=$params;}function get_json_params(){return $this->json;}public function offsetExists($o):bool{return isset($this->params[$o]);}public function offsetGet($o):mixed{return $this->params[$o]??null;}public function offsetSet($o,$v):void{$this->params[$o]=$v;}public function offsetUnset($o):void{unset($this->params[$o]);}}
require dirname(__DIR__).'/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php';
function ok($c,$m){if(!$c){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$w=SC_Workspace::instance();
$GLOBALS['logged_in']=false;ok($w->cloud_permission()===false,'anonymous sync denied');$GLOBALS['logged_in']=true;
$p=array('schema'=>'sc-workspace-project/20.0','id'=>'scwp-sync','title'=>'Sync Demo','updatedAt'=>'2026-08-11T20:00:00Z','persistence'=>array('mode'=>'device-local'),'recentTools'=>array('x'),'objects'=>array(array('id'=>'scwo-1','schema'=>'sc-workspace-object/1.0','title'=>'Evidence')));
$push=function($expected,$title,$operationId)use($w,$p){$q=$p;$q['title']=$title;return $w->cloud_project_store(new Req(array('schema'=>'sc-workspace-sync-push/1.0','sourceProjectId'=>'scwp-sync','projectTitle'=>$title,'clientUpdatedAt'=>'2026-08-11T20:00:00Z','expectedRevision'=>$expected,'operationId'=>$operationId,'project'=>$q)));};
$r1=$push(0,'Sync One','op-1');ok(is_array($r1)&&$r1['ok']===true&&$r1['item']['revision']===1,'first sync revision 1');ok($r1['item']['storageMode']==='sync-head','sync storage mode');ok(strlen($r1['item']['projectFingerprint'])===64,'project fingerprint');ok(($r1['item']['lastOperationId']??'')==='op-1','operation id persisted');
$replay=$push(0,'Sync One','op-1');ok(is_array($replay)&&($replay['replayed']??false)===true&&$replay['item']['revision']===1,'same operation id replays without new revision');
$stale=$push(0,'Stale','op-stale');ok($stale instanceof WP_Error,'stale push rejected');ok($stale->code==='scw_sync_conflict','stale conflict code');ok(($stale->data['status']??0)===409,'stale HTTP 409');ok(($stale->data['currentRevision']??0)===1,'current revision returned');
$r2=$push(1,'Sync Two','op-2');ok($r2['item']['revision']===2,'correct revision advances');
$manual=$w->cloud_project_store(new Req(array('schema'=>'sc-workspace-cloud-backup/1.0','sourceProjectId'=>'scwp-sync','projectTitle'=>'Manual','clientUpdatedAt'=>'2026-08-11T20:00:00Z','project'=>$p)));ok($manual instanceof WP_Error,'manual backup cannot replace sync head');ok($manual->code==='scw_manual_backup_sync_head_conflict','manual/sync boundary conflict code');ok(($manual->data['status']??0)===409,'manual/sync boundary HTTP 409');
$manualProject=$p;$manualProject['id']='scwp-manual';$manualProject['title']='Manual only';
$manual2=$w->cloud_project_store(new Req(array('schema'=>'sc-workspace-cloud-backup/1.0','sourceProjectId'=>'scwp-manual','projectTitle'=>'Manual only','clientUpdatedAt'=>'2026-08-11T20:00:00Z','project'=>$manualProject)));ok(is_array($manual2)&&$manual2['item']['revision']===1,'manual backup works for non-sync-head project');ok($manual2['item']['storageMode']==='manual-backup','manual storage mode');
$list=$w->cloud_projects_list();ok(count($list['items'])===2,'two cloud project heads');ok(!isset($list['items'][0]['package']),'list excludes content');
$get=$w->cloud_project_get(new Req(array(),array('project_id'=>'scwp-sync')));ok(($get['package']['project']['id']??'')==='scwp-sync','cloud package retrieved');
$GLOBALS['uid']=99;ok(count($w->cloud_projects_list()['items'])===0,'per-user isolation');
echo "PASS - v0.67.0 cross-device sync runtime\n";
