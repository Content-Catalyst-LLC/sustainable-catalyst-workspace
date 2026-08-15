<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Cross_Device_Production {
    const SCHEMA = 'sc-workspace-cross-device-production/1.0';
    const PLAN_SCHEMA = 'sc-workspace-cross-device-sync-plan/1.0';
    const RECEIPT_SCHEMA = 'sc-workspace-cross-device-sync-receipt/1.0';
    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'planSchema' => self::PLAN_SCHEMA,
            'receiptSchema' => self::RECEIPT_SCHEMA,
            'identityProvider' => 'wordpress',
            'guestWorkspaceFirstClass' => true,
            'accountRequiredForSync' => true,
            'explicitProjectEnrollment' => true,
            'automaticEnrollmentOnSignIn' => false,
            'manualSyncNow' => true,
            'backgroundSync' => false,
            'automaticUpload' => false,
            'localProjectCanonicalOnDevice' => true,
            'cloudHeadIsContinuityCopy' => true,
            'deterministicContinuityPlan' => true,
            'planActions' => array('local-only','enroll','push','pull-safe','open-remote-copy','recreate-cloud','noop','conflict'),
            'revisionPreconditionRequired' => true,
            'silentLastWriteWins' => false,
            'conflictPreservesBothSides' => true,
            'safePullRequiresUnchangedLocalBaseline' => true,
            'syncOperationJournal' => true,
            'idempotentOperationRetry' => true,
            'interruptedOperationReconciliation' => true,
            'productionReceiptExport' => true,
            'receiptContainsProjectContent' => false,
            'receiptContainsQueryText' => false,
            'receiptContainsSourceUrls' => false,
            'receiptContainsDeviceIdentifier' => false,
            'deviceFingerprinting' => false,
            'accountProfileInReceipt' => false,
            'integrityAlgorithm' => 'SHA-256',
            'teamSync' => false,
            'institutionalSync' => false,
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
