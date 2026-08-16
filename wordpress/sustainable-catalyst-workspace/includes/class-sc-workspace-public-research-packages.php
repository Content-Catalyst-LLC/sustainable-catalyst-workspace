<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Public_Research_Packages {
 const SCHEMA='sc-workspace-public-research-packages/1.0';
 const PACKAGE_SCHEMA='sc-workspace-public-research-package/1.0';
 const OBJECT_SCHEMA='sc-workspace-portable-knowledge-object/1.0';
 const MANIFEST_SCHEMA='sc-workspace-public-research-package-manifest/1.0';
 const RECEIPT_SCHEMA='sc-workspace-publication-receipt/1.0';
 public static function contract(){ return array(
  'schema'=>self::SCHEMA,'workspaceVersion'=>SC_WORKSPACE_VERSION,'surface'=>'exchange/public-research',
  'packageSchema'=>self::PACKAGE_SCHEMA,'objectSchema'=>self::OBJECT_SCHEMA,'manifestSchema'=>self::MANIFEST_SCHEMA,'receiptSchema'=>self::RECEIPT_SCHEMA,
  'publishableFamilies'=>array('source','evidence','dataset','analysis','decision','document','export','citation','library-pointer','graph-reference'),
  'visibilityStates'=>array('private-draft','public-package'),'licenseRequiredForPublic'=>true,'explicitSelectionRequired'=>true,'explicitPublicationConfirmationRequired'=>true,
  'privateByDefault'=>true,'portableKnowledgeObjects'=>true,'provenancePreserved'=>true,'sourceRecordIdsPreserved'=>true,'immutableReleasedProjection'=>true,
  'sha256Integrity'=>true,'includedFieldsExplicit'=>true,'excludedFieldsRecorded'=>true,'packageManifestRequired'=>true,'publicationReceiptMetadataOnly'=>true,
  'canonicalWorkspaceRecordsMutated'=>false,'automaticPublication'=>false,'automaticUpload'=>false,'automaticNetworkRequest'=>false,'automaticAi'=>false,
  'behavioralTelemetry'=>false,'queryTelemetry'=>false,'schemaMigrationRequired'=>false,'storageSchemaVersion'=>35,'projectSchema'=>'sc-workspace-project/20.0','exportSchema'=>'sc-workspace-project-export/20.0',
  'previousRelease'=>'1.13.0','rollbackRelease'=>'1.13.0'); }
}
