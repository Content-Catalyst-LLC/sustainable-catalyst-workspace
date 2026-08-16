<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Product_Maturity {
 const SCHEMA='sc-workspace-product-maturity/1.0';
 const DOSSIER_SCHEMA='sc-workspace-product-maturity-dossier/1.0';
 const MATRIX_SCHEMA='sc-workspace-product-maturity-compatibility-matrix/1.0';
 const DEPRECATION_SCHEMA='sc-workspace-1x-deprecation-register/1.0';
 const CANDIDATE_SCHEMA='sc-workspace-2-0-candidate-boundary/1.0';
 public static function dimensions(){ return array('ux-consistency','accessibility','performance','compatibility','api-stability','recovery-integrity','data-portability','governance-provenance','privacy-security','deployment-operations','documentation-help','field-evidence'); }
 public static function contract(){ return array(
  'schema'=>self::SCHEMA,'workspaceVersion'=>SC_WORKSPACE_VERSION,'surface'=>'review/product-maturity',
  'dossierSchema'=>self::DOSSIER_SCHEMA,'compatibilityMatrixSchema'=>self::MATRIX_SCHEMA,'deprecationRegisterSchema'=>self::DEPRECATION_SCHEMA,'candidateBoundarySchema'=>self::CANDIDATE_SCHEMA,
  'dimensions'=>self::dimensions(),'states'=>array('ready','attention','blocked'),'deterministicAssessment'=>true,'numericScore'=>false,'evidenceRequired'=>true,
  'unresolvedBlockerPreventsCandidate'=>true,'compatibilityMatrixRequired'=>true,'deprecationRegisterRequired'=>true,'humanCandidateDesignationRequired'=>true,'candidateLabel'=>'2.0-candidate',
  'automatic20Promotion'=>false,'v2SchemaIntroduced'=>false,'automaticMigration'=>false,'breakingV1ContractChange'=>false,'v1ApiCompatibilityPreserved'=>true,
  'canonicalWorkspaceRecordsMutated'=>false,'automaticAi'=>false,'behavioralTelemetry'=>false,'queryTelemetry'=>false,'schemaMigrationRequired'=>false,
  'storageSchemaVersion'=>35,'projectSchema'=>'sc-workspace-project/20.0','exportSchema'=>'sc-workspace-project-export/20.0','previousRelease'=>'1.14.0','rollbackRelease'=>'1.14.0'); }
}
