<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Review_Rooms {
    const SCHEMA = 'sc-workspace-shared-review-rooms/1.0';
    const ROOM_SCHEMA = 'sc-workspace-shared-review-room/1.0';
    const INVITATION_SCHEMA = 'sc-workspace-review-room-invitation/1.0';
    const SNAPSHOT_SCHEMA = 'sc-workspace-review-room-snapshot/1.0';
    const EVENT_SCHEMA = 'sc-workspace-review-room-event/1.0';
    const EXPORT_SCHEMA = 'sc-workspace-review-room-export/1.0';
    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'roomSchema' => self::ROOM_SCHEMA,
            'invitationSchema' => self::INVITATION_SCHEMA,
            'snapshotSchema' => self::SNAPSHOT_SCHEMA,
            'eventSchema' => self::EVENT_SCHEMA,
            'exportSchema' => self::EXPORT_SCHEMA,
            'surface' => 'exchange/collaboration/shared-review-rooms',
            'roomStates' => array('draft','open','in-review','changes-requested','approved','closed'),
            'roles' => array('owner','editor','reviewer','observer'),
            'scopedPermissions' => true,
            'permissionsAreLocalGovernanceRecords' => true,
            'serverAclCreated' => false,
            'explicitInvitations' => true,
            'automaticInvitationDelivery' => false,
            'invitationCreatesAccount' => false,
            'immutableReviewSnapshots' => true,
            'snapshotScopeUsesExplicitObjectIds' => true,
            'snapshotFingerprintRequired' => true,
            'snapshotReplacedByLaterProjectEdits' => false,
            'roomCommentsReferenceSnapshotOrCanonicalIds' => true,
            'reviewStateTransitionsAudited' => true,
            'ownerClosesRoom' => true,
            'portableRoomExport' => true,
            'portableRoomImportStagesBeforeCommit' => true,
            'canonicalProjectOwnerRetained' => true,
            'proposalAcceptanceAppliesCanonicalChange' => false,
            'automaticCanonicalMutation' => false,
            'liveCoediting' => false,
            'sharedCloudTenant' => false,
            'teamCloudStorage' => false,
            'backgroundSync' => false,
            'automaticExternalSend' => false,
            'automaticAI' => false,
            'behavioralTelemetry' => false,
            'queryTelemetry' => false,
            'schemaMigrationRequired' => false,
            'storageSchemaVersion' => 35,
            'projectSchema' => 'sc-workspace-project/20.0',
            'exportSchema' => 'sc-workspace-project-export/20.0',
        );
    }
}
