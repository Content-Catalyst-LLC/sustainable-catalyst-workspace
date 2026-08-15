<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Knowledge_Graph_Explorer {
    const SCHEMA = 'sc-workspace-knowledge-graph-explorer/1.0';
    const SNAPSHOT_SCHEMA = 'sc-workspace-knowledge-graph-snapshot/1.0';
    public static function contract() {
        return array(
            'schema'=>self::SCHEMA,
            'workspaceVersion'=>SC_WORKSPACE_VERSION,
            'baseKnowledgeGraphSchema'=>'sc-workspace-knowledge-graph/2.0',
            'relationshipExplorerSchema'=>'sc-workspace-relationship-explorer/2.0',
            'snapshotSchema'=>self::SNAPSHOT_SCHEMA,
            'nodeFamilies'=>array('project','provenance','library-record','source','evidence','dataset','analysis','decision','document','export','notebook','notebook-block','research-question','research-claim','reference','synthesis','canvas-node'),
            'explicitPathTracing'=>true,
            'maxPathDepth'=>5,
            'incomingOutgoingBacklinkLedger'=>true,
            'edgeExplanationVisible'=>true,
            'libraryContinuityPointersIncluded'=>true,
            'universalSearchOriginRouting'=>true,
            'portableGraphSnapshotExport'=>true,
            'snapshotCopiesCanonicalBodies'=>false,
            'derivedAtRuntime'=>true,
            'canonicalRecordsMutated'=>false,
            'serverGraphDatabase'=>false,
            'semanticEmbeddings'=>false,
            'automaticRelationshipInference'=>false,
            'automaticSemanticSimilarityEdges'=>false,
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
