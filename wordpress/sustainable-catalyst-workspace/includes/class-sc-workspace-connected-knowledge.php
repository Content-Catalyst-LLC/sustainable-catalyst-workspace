<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Connected_Knowledge {
 const SCHEMA='sc-workspace-connected-knowledge-workspace/2.0';
 const CONTEXT_SCHEMA='sc-workspace-connected-knowledge-context/2.0';
 const REFERENCE_SCHEMA='sc-workspace-knowledge-object-reference/2.0';
 const ROUTE_SCHEMA='sc-workspace-knowledge-route/2.0';
 const COMPATIBILITY_SCHEMA='sc-workspace-v1-compatibility-registry/2.0';
 const RECEIPT_SCHEMA='sc-workspace-connected-knowledge-receipt/2.0';
 public static function surfaces(){ return array('workspace-projects','workspace-research','knowledge-library','site-intelligence','lab','workbench','decision-studio','shared-review','institutional-audit','public-knowledge','developer-api'); }
 public static function context_families(){ return array('project','source','evidence','dataset','analysis','decision','document','export','citation','library-pointer','knowledge-graph-reference','review-snapshot','audit-reference','public-knowledge-object'); }
 public static function compatibility_registry(){ return array(
  'schema'=>self::COMPATIBILITY_SCHEMA,
  'workspaceVersion'=>SC_WORKSPACE_VERSION,
  'v1RestNamespacePreserved'=>true,
  'v1DeveloperApiPreserved'=>true,
  'v1ProjectSchemaAccepted'=>true,
  'v1ExportSchemaAccepted'=>true,
  'storageSchemaVersion'=>35,
  'projectSchema'=>'sc-workspace-project/20.0',
  'exportSchema'=>'sc-workspace-project-export/20.0',
  'v2NativeProjectSchemaIntroduced'=>false,
  'automaticMigration'=>false,
  'destructiveMigration'=>false,
  'futureV2SchemaRequiresExplicitMigrationContract'=>true
 ); }
 public static function contract(){ return array(
  'schema'=>self::SCHEMA,
  'workspaceVersion'=>SC_WORKSPACE_VERSION,
  'release'=>'Connected Knowledge Workspace',
  'releaseStage'=>'connected-knowledge-workspace',
  'stableMajorRelease'=>true,
  'contextSchema'=>self::CONTEXT_SCHEMA,
  'referenceSchema'=>self::REFERENCE_SCHEMA,
  'routeSchema'=>self::ROUTE_SCHEMA,
  'compatibilitySchema'=>self::COMPATIBILITY_SCHEMA,
  'receiptSchema'=>self::RECEIPT_SCHEMA,
  'surfaces'=>self::surfaces(),
  'contextFamilies'=>self::context_families(),
  'singleContextEnvelope'=>true,
  'canonicalOwnershipPreserved'=>true,
  'returnToOriginRequired'=>true,
  'provenanceRequired'=>true,
  'sharedIdentityContinuity'=>true,
  'guestWorkspaceFirstClass'=>true,
  'localProjectCanonicalOnDevice'=>true,
  'specialistExecutionRemainsExternal'=>true,
  'controlledCollaborationPreserved'=>true,
  'institutionalGovernancePreserved'=>true,
  'publicKnowledgeRequiresExplicitProjection'=>true,
  'developerExtensionsReadOnlyByDefault'=>true,
  'institutionalScaleHardeningPreserved'=>true,
  'v1RestNamespacePreserved'=>true,
  'v2RestNamespaceAvailable'=>true,
  'v1ProjectCompatibility'=>true,
  'v1ExportCompatibility'=>true,
  'storageSchemaVersion'=>35,
  'projectSchema'=>'sc-workspace-project/20.0',
  'exportSchema'=>'sc-workspace-project-export/20.0',
  'schemaMigrationRequired'=>false,
  'automaticMigration'=>false,
  'automaticCrossProductExecution'=>false,
  'automaticContextUpload'=>false,
  'automaticReturnCommit'=>false,
  'automaticAi'=>false,
  'canonicalWorkspaceRecordsMutated'=>false,
  'behavioralTelemetry'=>false,
  'queryTelemetry'=>false,
  'previousRelease'=>'1.15.0',
  'rollbackRelease'=>'1.15.0'
 ); }
}
