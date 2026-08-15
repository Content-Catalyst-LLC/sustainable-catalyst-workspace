<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Lab_Integration {
    const SCHEMA = 'sc-workspace-lab-integration/1.0';
    const CONTEXT_SCHEMA = 'sc-workspace-lab-scientific-context/1.0';
    const RETURN_SCHEMA = 'sc-workspace-lab-scientific-return/1.0';
    const ARTIFACT_SCHEMA = 'sc-workspace-scientific-artifact/1.0';
    public static function contract() {
        return array(
            'schema'=>self::SCHEMA,
            'workspaceVersion'=>SC_WORKSPACE_VERSION,
            'contextPackageSchema'=>self::CONTEXT_SCHEMA,
            'returnPackageSchema'=>self::RETURN_SCHEMA,
            'scientificArtifactSchema'=>self::ARTIFACT_SCHEMA,
            'canonicalLabRoute'=>'/lab/',
            'supportedWorkflows'=>array('model-studio','graph-studio','experiment','bayesian-inference','posterior-diagnostics','posterior-predictive-modeling','data-transformation','scientific-visualization'),
            'contextObjectTypes'=>array('source','evidence','dataset','analysis','document','export'),
            'returnArtifactFamilies'=>array('dataset','derived-variable','model','graph','posterior-summary','diagnostic','experiment-result','scientific-report'),
            'explicitContextSelection'=>true,
            'portableContextPackage'=>true,
            'outboundUrlCarriesContent'=>false,
            'roundTripHandoffIdentityRequired'=>true,
            'projectAndHandoffMatchRequired'=>true,
            'sourceObjectIdsPreserved'=>true,
            'provenancePreserved'=>true,
            'methodologyMetadataPreserved'=>true,
            'uncertaintyMetadataPreserved'=>true,
            'unitsMetadataPreserved'=>true,
            'explicitReturnImportRequired'=>true,
            'explicitWorkspaceMaterializationRequired'=>true,
            'traceabilityEdgesFromSelectedContext'=>true,
            'labExecutionAutomatic'=>false,
            'automaticContextUpload'=>false,
            'automaticReturnCommit'=>false,
            'automaticAI'=>false,
            'behavioralTelemetry'=>false,
            'queryTelemetry'=>false,
            'canonicalLabRecordsMutated'=>false,
            'schemaMigrationRequired'=>false,
            'storageSchemaVersion'=>35,
            'projectSchema'=>'sc-workspace-project/20.0',
            'exportSchema'=>'sc-workspace-project-export/20.0',
        );
    }
}
