<?php
if (!defined('ABSPATH')) { exit; }

final class SC_Workspace_Backend {
    const CONTRACT_SCHEMA = 'sc-workspace-backend-bridge/1.0';

    public static function mode() {
        $mode = defined('SC_WORKSPACE_BACKEND_MODE') ? strtolower(trim((string) SC_WORKSPACE_BACKEND_MODE)) : 'disabled';
        return in_array($mode, array('disabled', 'primary'), true) ? $mode : 'disabled';
    }

    public static function base_url() {
        return defined('SC_WORKSPACE_BACKEND_URL') ? rtrim(trim((string) SC_WORKSPACE_BACKEND_URL), '/') : '';
    }

    private static function token() {
        return defined('SC_WORKSPACE_BACKEND_TOKEN') ? trim((string) SC_WORKSPACE_BACKEND_TOKEN) : '';
    }

    public static function configured() {
        return self::base_url() !== '' && self::token() !== '';
    }

    public static function enabled() {
        return self::mode() === 'primary' && self::configured();
    }

    public static function contract() {
        return array(
            'schema' => self::CONTRACT_SCHEMA,
            'workspaceVersion' => defined('SC_WORKSPACE_VERSION') ? SC_WORKSPACE_VERSION : '2.8.0',
            'backendMode' => self::mode(),
            'configured' => self::configured(),
            'enabled' => self::enabled(),
            'transport' => 'wordpress-server-proxy',
            'browserDirectBackendAccess' => false,
            'serviceCredentialServerSideOnly' => true,
            'failClosedWhenPrimary' => true,
            'legacyWordPressUserMetaFallbackWhenDisabled' => true,
            'automaticMigration' => false,
            'legacyMigrationPlanApply' => true,
            'legacyStoreRetainedAfterMigration' => true,
            'migrationReceipts' => true,
            'localProjectCanonicalOnDevice' => true,
            'explicitBackupAndSyncOnly' => true,
            'projectSchema' => 'sc-workspace-project/20.0',
            'notebookSchema' => 'sc-workspace-notebook/3.0',
            'backendPersistence' => 'postgresql',
            'backendRevisionHistory' => true,
            'objectStorage' => true,
            'objectStorageMode' => 'content-addressed-filesystem',
            'recoverySnapshots' => true,
            'storageIntegrityChecks' => true,
            'backgroundJobs' => true,
            'durableJobQueue' => true,
            'workerProcess' => true,
            'jobEventHistory' => true,
            'jobRetryAndCancel' => true,
            'computeOrchestration' => true,
            'orchestrationContract' => 'sc-workspace-compute-handoff/1.0',
            'serverConfiguredRoutesOnly' => true,
            'datasetRegistry' => true,
            'datasetRevisionHistory' => true,
            'modelRegistry' => true,
            'modelRevisionHistory' => true,
            'parameterSetRegistry' => true,
            'executionRunRegistry' => true,
            'executionRunEvents' => true,
            'executionRunOutputs' => true,
            'jobExecutionRunLinkage' => true,
            'reproducibilityFingerprints' => true,
            'executionEnvironmentRegistry' => true,
            'executionEnvironmentRevisionHistory' => true,
            'dependencyManifests' => true,
            'dependencyLockArtifacts' => true,
            'runtimeVersionCapture' => true,
            'containerIdentityCapture' => true,
            'randomSeedCapture' => true,
            'runtimeAdapterRegistry' => true,
            'runtimeAdapterRevisionHistory' => true,
            'runtimeCompatibilityChecks' => true,
            'reproductionPlans' => true,
            'reproductionVerification' => true,
            'deterministicRerunComparison' => true,
            'reproductionExecutionPlans' => true,
            'controlledRuntimeHandoffs' => true,
            'humanAuthorizedDispatch' => true,
            'frozenExecutionEnvelope' => true,
            'executionPolicyRegistry' => true,
            'executionPolicyRevisionHistory' => true,
            'executionPolicyDecisions' => true,
            'resourceBudgets' => true,
            'runtimeSandboxing' => true,
            'sandboxEnforcementMode' => 'pre-dispatch-policy-gate',
            'policyRequiredForControlledHandoffs' => true,
            'adapterTrustLevels' => true,
            'hostFilesystemAccessAllowed' => false,
            'dockerSocketAccessAllowed' => false,
            'privilegedExecutionAllowed' => false,
            'automaticReproductionExecution' => false,
            'clientSuppliedRuntimeUrlsAllowed' => false,
            'clientSuppliedRuntimeCredentialsAllowed' => false,
            'arbitraryCodeExecution' => false,
            'secretEnvironmentValuesCaptured' => false,
        );
    }

    public static function status() {
        $base = self::base_url();
        $result = array(
            'schema' => 'sc-workspace-backend-status/1.0',
            'mode' => self::mode(),
            'configured' => self::configured(),
            'enabled' => self::enabled(),
            'available' => false,
            'service' => '',
            'version' => '',
            'persistence' => '',
        );
        if ($base === '') {
            return $result;
        }
        $response = wp_remote_get($base . '/health', array('timeout' => 3, 'redirection' => 0));
        if (is_wp_error($response)) {
            $result['error'] = 'backend-unreachable';
            return $result;
        }
        $code = (int) wp_remote_retrieve_response_code($response);
        $body = json_decode((string) wp_remote_retrieve_body($response), true);
        if ($code >= 200 && $code < 300 && is_array($body) && !empty($body['ok'])) {
            $result['available'] = true;
            $result['service'] = sanitize_text_field((string) ($body['service'] ?? ''));
            $result['version'] = sanitize_text_field((string) ($body['version'] ?? ''));
            $result['persistence'] = sanitize_text_field((string) ($body['persistence'] ?? ''));
        } else {
            $result['error'] = 'backend-health-failed';
            $result['httpStatus'] = $code;
        }
        return $result;
    }

    public static function request($method, $path, $body = null) {
        return self::request_internal($method, $path, $body, true);
    }

    public static function configured_request($method, $path, $body = null) {
        return self::request_internal($method, $path, $body, false);
    }

    private static function request_internal($method, $path, $body, $require_primary) {
        if ($require_primary && !self::enabled()) {
            return new WP_Error('scw_backend_disabled', 'Workspace dedicated backend is not enabled.', array('status' => 503));
        }
        if (!self::configured()) {
            return new WP_Error('scw_backend_unconfigured', 'Workspace dedicated backend is not configured.', array('status' => 503));
        }
        $user_id = get_current_user_id();
        if ($user_id <= 0) {
            return new WP_Error('scw_backend_auth_required', 'A signed-in Workspace account is required.', array('status' => 401));
        }
        $args = array(
            'method' => strtoupper((string) $method),
            'timeout' => 15,
            'redirection' => 0,
            'headers' => array(
                'Authorization' => 'Bearer ' . self::token(),
                'X-SC-User-ID' => (string) $user_id,
                'Accept' => 'application/json',
            ),
        );
        if ($body !== null) {
            $args['headers']['Content-Type'] = 'application/json';
            $args['body'] = wp_json_encode($body, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        }
        $response = wp_remote_request(self::base_url() . '/' . ltrim((string) $path, '/'), $args);
        if (is_wp_error($response)) {
            return new WP_Error('scw_backend_unreachable', 'Workspace backend is unavailable. No fallback write was attempted.', array('status' => 503));
        }
        $code = (int) wp_remote_retrieve_response_code($response);
        $decoded = json_decode((string) wp_remote_retrieve_body($response), true);
        if (!is_array($decoded)) {
            return new WP_Error('scw_backend_invalid_response', 'Workspace backend returned an invalid response.', array('status' => 502));
        }
        if ($code < 200 || $code >= 300) {
            $message = isset($decoded['message']) ? (string) $decoded['message'] : 'Workspace backend request failed.';
            $data = array('status' => $code);
            foreach (array('currentRevision','current') as $field) {
                if (array_key_exists($field, $decoded)) {
                    $data[$field] = $decoded[$field];
                }
            }
            return new WP_Error('scw_backend_request_failed', $message, $data);
        }
        return rest_ensure_response($decoded);
    }
}
