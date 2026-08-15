<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Institutional_Audit_Studio {
    const SCHEMA = 'sc-workspace-institutional-audit-studio/1.0';
    const DOSSIER_SCHEMA = 'sc-workspace-audit-dossier/1.0';
    const PROVENANCE_SCHEMA = 'sc-workspace-audit-provenance-record/1.0';
    const ATTESTATION_SCHEMA = 'sc-workspace-audit-attestation/1.0';
    const PACKAGE_SCHEMA = 'sc-workspace-institutional-audit-package/1.0';
    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'dossierSchema' => self::DOSSIER_SCHEMA,
            'provenanceSchema' => self::PROVENANCE_SCHEMA,
            'attestationSchema' => self::ATTESTATION_SCHEMA,
            'packageSchema' => self::PACKAGE_SCHEMA,
            'surface' => 'review/institutional-audit-studio',
            'evidenceFamilies' => array('audit-trail','version-history','reconciliation-receipts','review-room-snapshots','decisions','institutional-handoff','knowledge-graph','project-lifecycle','citations','provenance'),
            'explicitScope' => true,
            'derivedFromAuthoritativeLedgers' => true,
            'canonicalRecordsRemainOwnedBySourceSubsystems' => true,
            'evidenceLineageVisible' => true,
            'decisionLineageVisible' => true,
            'relationshipExplanationsVisible' => true,
            'immutableEvidenceFingerprint' => true,
            'integrityAlgorithm' => 'SHA-256',
            'reproducibleAuditPackageExport' => true,
            'auditPackageCopiesCanonicalBodies' => false,
            'attestationUserSupplied' => true,
            'attestationIdentityInferred' => false,
            'institutionalHandoffLinked' => true,
            'reviewRoomEvidenceLinked' => true,
            'regulatoryCertificationClaimed' => false,
            'complianceScore' => false,
            'automaticComplianceInference' => false,
            'automaticExternalSubmission' => false,
            'automaticCanonicalMutation' => false,
            'automaticAi' => false,
            'behavioralTelemetry' => false,
            'queryTelemetry' => false,
            'schemaMigrationRequired' => false,
            'storageSchemaVersion' => 35,
            'projectSchema' => 'sc-workspace-project/20.0',
            'exportSchema' => 'sc-workspace-project-export/20.0',
        );
    }
}
