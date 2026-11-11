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

    // SC-AUTH-01: bridge-only signing key. When set, requests carry a signed,
    // session-bound user assertion and never the shared token or a bare user id.
    private static function bridge_key() {
        $key = defined('SC_WORKSPACE_BRIDGE_ASSERTION_KEY') ? trim((string) SC_WORKSPACE_BRIDGE_ASSERTION_KEY) : '';
        return strlen($key) >= 32 && $key !== self::token() ? $key : '';
    }

    public static function bridge_enabled() {
        return self::bridge_key() !== '';
    }

    public static function configured() {
        return self::base_url() !== '' && (self::token() !== '' || self::bridge_enabled());
    }

    private static function b64url($raw) {
        return rtrim(strtr(base64_encode($raw), '+/', '-_'), '=');
    }

    // Must match backend/app/wp_bridge.py byte for byte: sorted keys, compact JSON.
    private static function bridge_assertion($user_id, $method, $target, $body_bytes) {
        $session_token = function_exists('wp_get_session_token') ? (string) wp_get_session_token() : '';
        if ($session_token === '') {
            return null;
        }
        $session = WP_Session_Tokens::get_instance($user_id)->get($session_token);
        if (!is_array($session) || empty($session['login'])) {
            return null;
        }
        $now = time();
        $claims = array(
            'aud' => defined('SC_WORKSPACE_BRIDGE_AUDIENCE') ? (string) SC_WORKSPACE_BRIDGE_AUDIENCE : 'sc-workspace-api',
            'bh' => hash('sha256', (string) $body_bytes),
            'exp' => $now + 60,
            'iat' => $now,
            'iss' => 'sc-wordpress-bridge',
            'm' => strtoupper((string) $method),
            'nonce' => bin2hex(random_bytes(32)),
            'p' => $target,
            'sat' => (int) $session['login'],
            'sid' => hash('sha256', $session_token),
            'sub' => (string) $user_id,
            'v' => 1,
        );
        ksort($claims, SORT_STRING);
        $encoded = self::b64url(wp_json_encode($claims, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
        return $encoded . '.' . hash_hmac('sha256', "sc-auth-01-wp-bridge-v1\0" . $encoded, self::bridge_key());
    }

    public static function enabled() {
        return self::mode() === 'primary' && self::configured();
    }

    // SC-AUTH-01 F4: account persistence must not silently move to another
    // store. The legacy WordPress user-meta store is served only on a site
    // that explicitly opts in and has no dedicated backend configured at all.
    public static function legacy_store_allowed() {
        return defined('SC_WORKSPACE_LEGACY_ACCOUNT_STORE') && SC_WORKSPACE_LEGACY_ACCOUNT_STORE === true
            && !defined('SC_WORKSPACE_BACKEND_MODE') && self::base_url() === '';
    }

    public static function fail_closed() {
        return new WP_Error('scw_backend_unavailable_fail_closed', 'Workspace account storage is not available. No fallback store was used.', array('status' => 503));
    }

    public static function contract() {
        return array(
            'schema' => self::CONTRACT_SCHEMA,
            'workspaceVersion' => defined('SC_WORKSPACE_VERSION') ? SC_WORKSPACE_VERSION : '2.20.0',
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
            'localProjectCanonicalOnDevice' => false,
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
            'runtimeEnforcementTelemetry' => true,
            'budgetAccounting' => true,
            'executionAttestations' => true,
            'runtimeTrustPolicyRegistry' => true,
            'attestationVerification' => true,
            'downstreamComplianceGates' => true,
            'humanComplianceWaivers' => true,
            'pythonScientificComputeRuntime' => true,
            'scientificComputeOperationRegistry' => true,
            'scientificComputeEngines' => array('numpy', 'pandas', 'scipy', 'sympy'),
            'computeResultArtifacts' => true,
            'computeExecutionReceipts' => true,
            'computeProgressEvents' => true,
            'computeCancellationChecks' => true,
            'boundedScientificOperationsOnly' => true,
            'polyglotScientificRuntimeFabric' => true,
            'polyglotLanguages' => array('python', 'r', 'julia', 'ml', 'sql', 'wasm'),
            'arrowCompatibleInterchange' => true,
            'nativeArrowParquetInterchange' => true,
            'interchangeFormats' => array('arrow-ipc-stream', 'parquet'),
            'interchangeRuntimeBoundedOperations' => 8,
            'interchangeReceipts' => true,
            'forecastingTimeSeriesRuntime' => true,
            'forecastRuntimeBoundedOperations' => 8,
            'forecastReceipts' => true,
            'forecastEvaluationReceipts' => true,
            'crossRuntimeReproductionVerification' => true,
            'toleranceAwareNumericComparison' => true,
            'crossRuntimeVerificationReceipts' => true,
            'polyglotExecutionReceipts' => true,
            'polyglotRuntimeCatalog' => true,
            'rStatisticalEconometricRuntime' => true,
            'rRuntimeBoundedOperations' => 8,
            'statisticalModelReceipts' => true,
            'hostFilesystemAccessAllowed' => false,
            'dockerSocketAccessAllowed' => false,
            'privilegedExecutionAllowed' => false,
            'automaticReproductionExecution' => false,
            'clientSuppliedRuntimeUrlsAllowed' => false,
            'clientSuppliedRuntimeCredentialsAllowed' => false,
            'arbitraryCodeExecution' => false,
            'unifiedScientificObjectApi' => true,
            'scientificObjectSchema' => 'sc-workspace-scientific-object/1.0',
            'scientificObjectRelations' => true,
            'scientificObjectGenericMutation' => false,
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
        $target = '/' . ltrim((string) $path, '/');
        $body_bytes = $body !== null ? wp_json_encode($body, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) : '';
        $args = array(
            'method' => strtoupper((string) $method),
            'timeout' => 15,
            'redirection' => 0,
            'headers' => array('Accept' => 'application/json'),
        );
        if (self::bridge_enabled()) {
            $assertion = self::bridge_assertion($user_id, $method, $target, $body_bytes);
            if ($assertion === null) {
                // No live WordPress session to bind (e.g. application passwords): refuse.
                return new WP_Error('scw_bridge_session_required', 'A signed-in WordPress browser session is required.', array('status' => 401));
            }
            $args['headers']['X-SC-Bridge-Assertion'] = $assertion;
        } else {
            $args['headers']['Authorization'] = 'Bearer ' . self::token();
            $args['headers']['X-SC-User-ID'] = (string) $user_id;
        }
        if ($body !== null) {
            $args['headers']['Content-Type'] = 'application/json';
            $args['body'] = $body_bytes;
        }
        $response = wp_remote_request(self::base_url() . $target, $args);
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
