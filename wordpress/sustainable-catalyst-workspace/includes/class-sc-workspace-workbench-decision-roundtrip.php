<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Workbench_Decision_Roundtrip {
    const SCHEMA = 'sc-workspace-workbench-decision-roundtrip/1.0';
    const WORKBENCH_CONTEXT_SCHEMA = 'sc-workspace-workbench-context/1.0';
    const WORKBENCH_RETURN_SCHEMA = 'sc-workspace-workbench-return/1.0';
    const DECISION_CONTEXT_SCHEMA = 'sc-workspace-decision-studio-context/1.0';
    const DECISION_RETURN_SCHEMA = 'sc-workspace-decision-studio-return/1.0';
    public static function contract() {
        return array(
            'schema'=>self::SCHEMA,
            'workspaceVersion'=>SC_WORKSPACE_VERSION,
            'workbenchContextSchema'=>self::WORKBENCH_CONTEXT_SCHEMA,
            'workbenchReturnSchema'=>self::WORKBENCH_RETURN_SCHEMA,
            'decisionStudioContextSchema'=>self::DECISION_CONTEXT_SCHEMA,
            'decisionStudioReturnSchema'=>self::DECISION_RETURN_SCHEMA,
            'canonicalWorkbenchRoute'=>'/lab/workbench/',
            'canonicalDecisionStudioRoute'=>'/lab/decision-studio/',
            'destinations'=>array('workbench','decision-studio'),
            'workbenchWorkflows'=>array('calculation','simulation','optimization','engineering-analysis','data-transformation','sensitivity-analysis'),
            'decisionStudioWorkflows'=>array('decision-packet','scenario-comparison','tradeoff-analysis','option-assessment','risk-review','decision-brief'),
            'workbenchContextObjectTypes'=>array('dataset','analysis','evidence','document','export'),
            'decisionStudioContextObjectTypes'=>array('decision','evidence','source','analysis','document','export'),
            'workbenchReturnFamilies'=>array('calculation','simulation-result','optimization-result','transformed-dataset','engineering-report','sensitivity-result'),
            'decisionStudioReturnFamilies'=>array('decision-packet','scenario-set','recommendation','risk-register','decision-brief','outcome-plan'),
            'explicitContextSelection'=>true,
            'portableContextPackages'=>true,
            'outboundUrlCarriesContent'=>false,
            'roundTripHandoffIdentityRequired'=>true,
            'projectAndHandoffMatchRequired'=>true,
            'destinationMatchRequired'=>true,
            'sourceObjectIdsPreserved'=>true,
            'provenancePreserved'=>true,
            'methodParametersPreserved'=>true,
            'constraintsAssumptionsPreserved'=>true,
            'scenarioMetadataPreserved'=>true,
            'explicitReturnImportRequired'=>true,
            'explicitWorkspaceMaterializationRequired'=>true,
            'traceabilityEdgesFromSelectedContext'=>true,
            'specializedExecutionAutomatic'=>false,
            'automaticContextUpload'=>false,
            'automaticReturnCommit'=>false,
            'automaticAI'=>false,
            'behavioralTelemetry'=>false,
            'queryTelemetry'=>false,
            'canonicalToolRecordsMutated'=>false,
            'schemaMigrationRequired'=>false,
            'storageSchemaVersion'=>35,
            'projectSchema'=>'sc-workspace-project/20.0',
            'exportSchema'=>'sc-workspace-project-export/20.0',
        );
    }
}
