<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__);
if (!defined('SC_WORKSPACE_VERSION')) define('SC_WORKSPACE_VERSION','1.8.0');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-review-rooms.php';
$c=SC_Workspace_Review_Rooms::contract();
if ($c['workspaceVersion']!=='1.8.0'||$c['schema']!=='sc-workspace-shared-review-rooms/1.0'||count($c['roomStates'])!==6||count($c['roles'])!==4||!$c['scopedPermissions']||!$c['immutableReviewSnapshots']||$c['serverAclCreated']||$c['automaticInvitationDelivery']||$c['liveCoediting']||$c['automaticCanonicalMutation']||$c['schemaMigrationRequired']) { fwrite(STDERR,"FAIL\n"); exit(1); }
echo "PASS - v1.8.0 shared review rooms PHP runtime\n";
