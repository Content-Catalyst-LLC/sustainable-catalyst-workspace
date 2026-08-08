<?php
class WP_Error { public $code; public function __construct($c,$m=''){ $this->code=$c; } }
function is_wp_error($v){ return $v instanceof WP_Error; }
define('ABSPATH', __DIR__ . '/'); define('OBJECT','OBJECT');
$GLOBALS['opts']=array(); $GLOBALS['posts']=array(); $GLOBALS['meta']=array(); $GLOBALS['updated']=array();
function add_action(){ } function admin_url($p=''){return 'https://example.test/wp-admin/'.$p;} function home_url($p=''){return 'https://example.test'.$p;} function current_user_can(){return true;} function wp_die($m){throw new Exception($m);} function check_admin_referer(){return true;} function sanitize_key($v){return $v;} function wp_unslash($v){return $v;} function get_current_screen(){return null;} function esc_url($v){return $v;} function esc_html($v){return $v;} function submit_button(){} function wp_nonce_field(){} function add_query_arg($a,$u){return $u;} function wp_safe_redirect(){} function flush_rewrite_rules(){} function get_page_template_slug(){return 'default';} function wp_parse_url($u,$part=-1){return parse_url($u,$part);} function untrailingslashit($s){return rtrim($s,'/');}
function get_option($k,$d=null){return array_key_exists($k,$GLOBALS['opts'])?$GLOBALS['opts'][$k]:$d;} function update_option($k,$v){$GLOBALS['opts'][$k]=$v;return true;} function add_option($k,$v){if(array_key_exists($k,$GLOBALS['opts']))return false;$GLOBALS['opts'][$k]=$v;return true;} function delete_option($k){unset($GLOBALS['opts'][$k]);return true;}
function get_page_by_path($slug){return (object)array('ID'=>77,'post_title'=>'Workspace','post_content'=>'[sc_workspace_platform]','post_name'=>'platform','post_parent'=>0,'post_status'=>'publish','post_excerpt'=>'');}
function get_posts($args){return $GLOBALS['posts'];}
function get_post_meta($id,$key,$single=true){return isset($GLOBALS['meta'][$id][$key])?$GLOBALS['meta'][$id][$key]:'';}
function wp_update_post($args,$err=false){$GLOBALS['updated'][]=$args;foreach($GLOBALS['posts'] as $p){if($p->ID==$args['ID']&&isset($args['post_title']))$p->post_title=$args['post_title'];}return $args['ID'];}
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-platform.php';
$GLOBALS['posts']=array((object)array('ID'=>10,'post_title'=>'Platform'),(object)array('ID'=>11,'post_title'=>'Platform'),(object)array('ID'=>12,'post_title'=>'Platform'));
$GLOBALS['meta'][10]=array('_menu_item_object'=>'page','_menu_item_object_id'=>77,'_menu_item_url'=>'');
$GLOBALS['meta'][11]=array('_menu_item_object'=>'custom','_menu_item_object_id'=>0,'_menu_item_url'=>'https://example.test/platform/');
$GLOBALS['meta'][12]=array('_menu_item_object'=>'custom','_menu_item_object_id'=>0,'_menu_item_url'=>'https://example.test/other/');
$r=SC_Workspace_Platform::relabel_navigation_items(); if($r['changed']!==2){fwrite(STDERR,'expected 2 changed\n');exit(1);} if($GLOBALS['posts'][0]->post_title!=='Workspace'||$GLOBALS['posts'][1]->post_title!=='Workspace'||$GLOBALS['posts'][2]->post_title!=='Platform'){fwrite(STDERR,'wrong relabel scope\n');exit(1);} if(get_option(SC_Workspace_Platform::NAV_BACKUP_KEY,null)===null){fwrite(STDERR,'missing backup\n');exit(1);} $rr=SC_Workspace_Platform::restore_navigation_items(); if(is_wp_error($rr)){fwrite(STDERR,'restore failed\n');exit(1);} echo "PASS - navigation relabel runtime\n";
