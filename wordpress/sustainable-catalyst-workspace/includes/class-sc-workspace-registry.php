<?php
if (!defined('ABSPATH')) {
    exit;
}

final class SC_Workspace_Registry {
    const OPTION_KEY = 'scfs_canonical_product_registry';
    const BACKUP_KEY = 'sc_workspace_registry_backup_v020';
    const PENDING_KEY = 'sc_workspace_registry_pending_v020';
    const LEGACY_PENDING_KEY = 'sc_workspace_registry_pending_v010';
    const CANONICAL_ID = 'sustainable-catalyst-workspace';

    public static function activate() {
        self::register_product();
    }

    public static function register_product() {
        $registry = get_option(self::OPTION_KEY, null);
        if (!is_array($registry)) {
            update_option(self::PENDING_KEY, '1', false);
            return false;
        }

        if (get_option(self::BACKUP_KEY, null) === null) {
            add_option(self::BACKUP_KEY, $registry, '', 'no');
        }

        $record = self::record();
        $updated = false;

        if (isset($registry['products']) && is_array($registry['products'])) {
            if (self::is_list($registry['products'])) {
                $found = false;
                foreach ($registry['products'] as $index => $existing) {
                    if (is_array($existing) && isset($existing['canonical_id']) && $existing['canonical_id'] === self::CANONICAL_ID) {
                        $registry['products'][$index] = array_merge($existing, $record);
                        $found = true;
                        $updated = true;
                        break;
                    }
                }
                if (!$found) {
                    $registry['products'][] = $record;
                    $updated = true;
                }
            } else {
                $existing = isset($registry['products'][self::CANONICAL_ID]) && is_array($registry['products'][self::CANONICAL_ID])
                    ? $registry['products'][self::CANONICAL_ID]
                    : array();
                $registry['products'][self::CANONICAL_ID] = array_merge($existing, $record);
                $updated = true;
            }
        } else {
            $existing = isset($registry[self::CANONICAL_ID]) && is_array($registry[self::CANONICAL_ID])
                ? $registry[self::CANONICAL_ID]
                : array();
            $registry[self::CANONICAL_ID] = array_merge($existing, $record);
            $updated = true;
        }

        if (!$updated) {
            update_option(self::PENDING_KEY, '1', false);
            return false;
        }

        if (!update_option(self::OPTION_KEY, $registry, false)) {
            $current = get_option(self::OPTION_KEY, array());
            if ($current !== $registry) {
                update_option(self::PENDING_KEY, '1', false);
                return false;
            }
        }

        delete_option(self::PENDING_KEY);
        delete_option(self::LEGACY_PENDING_KEY);
        do_action('scfs_product_registry_updated', self::CANONICAL_ID, $record);
        return true;
    }

    public static function record() {
        $now = gmdate('c');
        return array(
            'canonical_id' => self::CANONICAL_ID,
            'name' => 'Sustainable Catalyst Workspace',
            'short_name' => 'Workspace',
            'internal_name' => 'Sustainable Catalyst Workspace',
            'legacy_names' => array(),
            'legacy_plugin_files' => array(),
            'legacy_plugin_slugs' => array(),
            'legacy_text_domains' => array(),
            'family' => 'commercial',
            'console_screen' => 'commercial',
            'display_order' => 400,
            'repository_slug' => 'sustainable-catalyst-workspace',
            'product_type' => 'wordpress_plugin',
            'version_source' => 'wordpress_plugin',
            'version_precedence' => 'discovered',
            'plugin_slug' => 'sustainable-catalyst-workspace',
            'plugin_file' => 'sustainable-catalyst-workspace/sustainable-catalyst-workspace.php',
            'plugin_text_domain' => 'sustainable-catalyst-workspace',
            'product_url' => '/platform/workspace/',
            'owner' => 'Content Catalyst LLC',
            'public_visible' => '1',
            'homepage_visible' => '1',
            'lifecycle_state' => 'experimental',
            'release_channel' => 'stable',
            'status' => 'current',
            'validation_state' => 'validated',
            'documentation_state' => 'ready',
            'known_issue_count' => 0,
            'commercial' => '1',
            'public_interest' => '1',
            'discovery_enabled' => '1',
            'discovery_locked' => '',
            'discovery_state' => 'unscanned',
            'discovery_match' => '',
            'discovered_active' => '',
            'discovered_activation_scope' => 'inactive',
            'discovered_plugin_name' => '',
            'discovered_plugin_version' => '',
            'discovered_plugin_version_raw' => '',
            'discovered_version_state' => 'unscanned',
            'discovered_text_domain' => '',
            'last_discovered_at' => '',
            'installed_version' => SC_WORKSPACE_VERSION,
            'public_version' => SC_WORKSPACE_VERSION,
            'previous_version' => '0.1.0',
            'release_date' => '2026-08-08',
            'change_summary' => 'Projects and Persistent Work: device-local project creation, autosave, archive and recovery, project import/export, activity history, and active-project handoffs across Sustainable Catalyst.',
            'superseded_by' => '',
            'manual_notes' => 'Commercial Release governance with free public access. v0.2.0 persists Workspace Projects on the current device only; there is no account, cloud project store, collaboration layer, or server-side project synchronization.',
            'verification_source' => 'wordpress_plugin',
            'source_verified_at' => $now,
            'record_updated_at' => $now,
            'last_verified_at' => $now,
        );
    }

    private static function is_list(array $array) {
        if (count($array) === 0) {
            return true;
        }
        if (function_exists('array_is_list')) {
            return array_is_list($array);
        }
        return array_keys($array) === range(0, count($array) - 1);
    }
}
