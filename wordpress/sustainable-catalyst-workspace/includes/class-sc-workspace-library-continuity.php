<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Library_Continuity {
    const SCHEMA = 'sc-workspace-library-continuity/1.0';
    const PACKAGE_SCHEMA = 'sc-library-workspace-continuity/1.0';
    public static function contract() {
        return array(
            'schema'=>self::SCHEMA,
            'workspaceVersion'=>SC_WORKSPACE_VERSION,
            'canonicalLibraryRoute'=>'/knowledge-libraries/',
            'sharedIdentityProvider'=>'wordpress',
            'secondAccountRequired'=>false,
            'authenticatedIdentityReused'=>true,
            'guestWorkspacePreserved'=>true,
            'recordFamilies'=>array('saved-search','watchlist','research-queue-item','source-bundle','personal-recommendation'),
            'personalRecommendationsPrivateByDefault'=>true,
            'packageSchema'=>self::PACKAGE_SCHEMA,
            'explicitPackageOrSameOriginHandoff'=>true,
            'browserLocalStaging'=>true,
            'explicitProjectPromotionRequired'=>true,
            'provenancePreserved'=>true,
            'originIdsPreserved'=>true,
            'originUrlsPreserved'=>true,
            'canonicalLibraryRecordsMutated'=>false,
            'canonicalLibraryRecordsDuplicated'=>false,
            'automaticLibraryPull'=>false,
            'automaticBackgroundSync'=>false,
            'automaticAI'=>false,
            'behavioralTelemetry'=>false,
            'queryTelemetry'=>false,
            'schemaMigrationRequired'=>false,
            'storageSchemaVersion'=>35,
            'projectSchema'=>'sc-workspace-project/20.0',
            'exportSchema'=>'sc-workspace-project-export/20.0',
        );
    }
}
