<?php
if (!defined('ABSPATH')) {
    exit;
}

final class SC_Workspace_Registry {
    const OPTION_KEY = 'scfs_canonical_product_registry';
    const BACKUP_KEY = 'sc_workspace_registry_backup_v0680';
    const PENDING_KEY = 'sc_workspace_registry_pending_v0680';
    const LEGACY_PENDING_KEY_V0670 = 'sc_workspace_registry_pending_v0670';
    const LEGACY_PENDING_KEY_V0661 = 'sc_workspace_registry_pending_v0661';
    const LEGACY_PENDING_KEY_V0660 = 'sc_workspace_registry_pending_v0660';
    const LEGACY_PENDING_KEY_V0650 = 'sc_workspace_registry_pending_v0650';
    const LEGACY_PENDING_KEY_V0641 = 'sc_workspace_registry_pending_v0641';
    const LEGACY_PENDING_KEY_V0640 = 'sc_workspace_registry_pending_v0640';
    const LEGACY_PENDING_KEY_V0630 = 'sc_workspace_registry_pending_v0630';
    const LEGACY_PENDING_KEY_V0620 = 'sc_workspace_registry_pending_v0620';
    const LEGACY_PENDING_KEY_V0610 = 'sc_workspace_registry_pending_v0610';
    const LEGACY_PENDING_KEY_V0600 = 'sc_workspace_registry_pending_v0600';
    const LEGACY_PENDING_KEY_V0591 = 'sc_workspace_registry_pending_v0591';
    const LEGACY_PENDING_KEY_V0590 = 'sc_workspace_registry_pending_v0590';
    const LEGACY_PENDING_KEY_V0580 = 'sc_workspace_registry_pending_v0580';
    const LEGACY_PENDING_KEY_V0570 = 'sc_workspace_registry_pending_v0570';
    const LEGACY_PENDING_KEY_V0560 = 'sc_workspace_registry_pending_v0560';
    const LEGACY_PENDING_KEY_V0550 = 'sc_workspace_registry_pending_v0550';
    const LEGACY_PENDING_KEY_V0540 = 'sc_workspace_registry_pending_v0540';
    const LEGACY_PENDING_KEY_V0530 = 'sc_workspace_registry_pending_v0530';
    const LEGACY_PENDING_KEY_V0520 = 'sc_workspace_registry_pending_v0520';
    const LEGACY_PENDING_KEY_V0510 = 'sc_workspace_registry_pending_v0510';
    const LEGACY_PENDING_KEY_V0500 = 'sc_workspace_registry_pending_v0500';
    const LEGACY_PENDING_KEY_V0490 = 'sc_workspace_registry_pending_v0490';
    const LEGACY_PENDING_KEY_V0480 = 'sc_workspace_registry_pending_v0480';
    const LEGACY_PENDING_KEY_V0470 = 'sc_workspace_registry_pending_v0470';
    const LEGACY_PENDING_KEY_V0461 = 'sc_workspace_registry_pending_v0461';
    const LEGACY_PENDING_KEY_V0460 = 'sc_workspace_registry_pending_v0460';
    const LEGACY_PENDING_KEY_V0450 = 'sc_workspace_registry_pending_v0450';
    const LEGACY_PENDING_KEY_V0440 = 'sc_workspace_registry_pending_v0440';
    const LEGACY_PENDING_KEY_V0430 = 'sc_workspace_registry_pending_v0430';
    const LEGACY_PENDING_KEY_V0420 = 'sc_workspace_registry_pending_v0420';
    const LEGACY_PENDING_KEY_V0410 = 'sc_workspace_registry_pending_v0410';
    const LEGACY_PENDING_KEY_V0400 = 'sc_workspace_registry_pending_v0400';
    const LEGACY_PENDING_KEY_V0390 = 'sc_workspace_registry_pending_v0390';
    const LEGACY_PENDING_KEY_V0380 = 'sc_workspace_registry_pending_v0380';
    const LEGACY_PENDING_KEY_V0370 = 'sc_workspace_registry_pending_v0370';
    const LEGACY_PENDING_KEY_V0360 = 'sc_workspace_registry_pending_v0360';
    const LEGACY_PENDING_KEY_V0350 = 'sc_workspace_registry_pending_v0350';
    const LEGACY_PENDING_KEY_V0340 = 'sc_workspace_registry_pending_v0340';
    const LEGACY_PENDING_KEY_V0330 = 'sc_workspace_registry_pending_v0330';
    const LEGACY_PENDING_KEY_V0320 = 'sc_workspace_registry_pending_v0320';
    const LEGACY_PENDING_KEY_V0310 = 'sc_workspace_registry_pending_v0310';
    const LEGACY_PENDING_KEY_V0300 = 'sc_workspace_registry_pending_v0300';
    const LEGACY_PENDING_KEY_V0290 = 'sc_workspace_registry_pending_v0290';
    const LEGACY_PENDING_KEY_V0280 = 'sc_workspace_registry_pending_v0280';
    const LEGACY_PENDING_KEY_V0270 = 'sc_workspace_registry_pending_v0270';
    const LEGACY_PENDING_KEY_V0260 = 'sc_workspace_registry_pending_v0260';
    const LEGACY_PENDING_KEY_V0250 = 'sc_workspace_registry_pending_v0250';
    const LEGACY_PENDING_KEY_V0240 = 'sc_workspace_registry_pending_v0240';
    const LEGACY_PENDING_KEY_V0230 = 'sc_workspace_registry_pending_v0230';
    const LEGACY_PENDING_KEY_V0220 = 'sc_workspace_registry_pending_v0220';
    const LEGACY_PENDING_KEY_V0210 = 'sc_workspace_registry_pending_v0210';
    const LEGACY_PENDING_KEY_V0200 = 'sc_workspace_registry_pending_v0200';
    const LEGACY_PENDING_KEY_V0190 = 'sc_workspace_registry_pending_v0190';
    const LEGACY_PENDING_KEY_V0180 = 'sc_workspace_registry_pending_v0180';
    const LEGACY_PENDING_KEY_V0170 = 'sc_workspace_registry_pending_v0170';
    const LEGACY_PENDING_KEY_V0160 = 'sc_workspace_registry_pending_v0160';
    const LEGACY_PENDING_KEY_V0150 = 'sc_workspace_registry_pending_v0150';
    const LEGACY_PENDING_KEY_V0140 = 'sc_workspace_registry_pending_v0140';
    const LEGACY_PENDING_KEY_V0130 = 'sc_workspace_registry_pending_v0130';
    const LEGACY_PENDING_KEY_V0120 = 'sc_workspace_registry_pending_v0120';
    const LEGACY_PENDING_KEY_V0110 = 'sc_workspace_registry_pending_v0110';
    const LEGACY_PENDING_KEY_V0100 = 'sc_workspace_registry_pending_v0100';
    const LEGACY_PENDING_KEY_V0901 = 'sc_workspace_registry_pending_v0901';
    const LEGACY_PENDING_KEY_V090 = 'sc_workspace_registry_pending_v090';
    const LEGACY_PENDING_KEY_V0831 = 'sc_workspace_registry_pending_v0831';
    const LEGACY_PENDING_KEY_V083 = 'sc_workspace_registry_pending_v083';
    const LEGACY_PENDING_KEY_V082 = 'sc_workspace_registry_pending_v082';
    const LEGACY_PENDING_KEY_V081 = 'sc_workspace_registry_pending_v081';
    const LEGACY_PENDING_KEY_V080 = 'sc_workspace_registry_pending_v080';
    const LEGACY_PENDING_KEY_V070 = 'sc_workspace_registry_pending_v070';
    const LEGACY_PENDING_KEY_V061 = 'sc_workspace_registry_pending_v061';
    const LEGACY_PENDING_KEY_V060 = 'sc_workspace_registry_pending_v060';
    const LEGACY_PENDING_KEY_V041 = 'sc_workspace_registry_pending_v041';
    const LEGACY_PENDING_KEY_V040 = 'sc_workspace_registry_pending_v040';
    const LEGACY_PENDING_KEY_V030 = 'sc_workspace_registry_pending_v030';
    const LEGACY_PENDING_KEY_V020 = 'sc_workspace_registry_pending_v020';
    const LEGACY_PENDING_KEY_V010 = 'sc_workspace_registry_pending_v010';
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
        delete_option(self::LEGACY_PENDING_KEY_V0670);
        delete_option(self::LEGACY_PENDING_KEY_V0661);
        delete_option(self::LEGACY_PENDING_KEY_V0660);
        delete_option(self::LEGACY_PENDING_KEY_V0650);
        delete_option(self::LEGACY_PENDING_KEY_V0641);
        delete_option(self::LEGACY_PENDING_KEY_V0640);
        delete_option(self::LEGACY_PENDING_KEY_V0630);
        delete_option(self::LEGACY_PENDING_KEY_V0620);
        delete_option(self::LEGACY_PENDING_KEY_V0610);
        delete_option(self::LEGACY_PENDING_KEY_V0600);
        delete_option(self::LEGACY_PENDING_KEY_V0591);
        delete_option(self::LEGACY_PENDING_KEY_V0590);
        delete_option(self::LEGACY_PENDING_KEY_V0580);
        delete_option(self::LEGACY_PENDING_KEY_V0570);
        delete_option(self::LEGACY_PENDING_KEY_V0560);
        delete_option(self::LEGACY_PENDING_KEY_V0550);
        delete_option(self::LEGACY_PENDING_KEY_V0540);
        delete_option(self::LEGACY_PENDING_KEY_V0530);
        delete_option(self::LEGACY_PENDING_KEY_V0520);
        delete_option(self::LEGACY_PENDING_KEY_V0510);
        delete_option(self::LEGACY_PENDING_KEY_V0500);
        delete_option(self::LEGACY_PENDING_KEY_V0490);
        delete_option(self::LEGACY_PENDING_KEY_V0480);
        delete_option(self::LEGACY_PENDING_KEY_V0470);
        delete_option(self::LEGACY_PENDING_KEY_V0461);
        delete_option(self::LEGACY_PENDING_KEY_V0460);
        delete_option(self::LEGACY_PENDING_KEY_V0450);
        delete_option(self::LEGACY_PENDING_KEY_V0440);
        delete_option(self::LEGACY_PENDING_KEY_V0430);
        delete_option(self::LEGACY_PENDING_KEY_V0420);
        delete_option(self::LEGACY_PENDING_KEY_V0410);
        delete_option(self::LEGACY_PENDING_KEY_V0400);
        delete_option(self::LEGACY_PENDING_KEY_V0390);
        delete_option(self::LEGACY_PENDING_KEY_V0380);
        delete_option(self::LEGACY_PENDING_KEY_V0370);
        delete_option(self::LEGACY_PENDING_KEY_V0360);
        delete_option(self::LEGACY_PENDING_KEY_V0350);
        delete_option(self::LEGACY_PENDING_KEY_V0340);
        delete_option(self::LEGACY_PENDING_KEY_V0330);
        delete_option(self::LEGACY_PENDING_KEY_V0320);
        delete_option(self::LEGACY_PENDING_KEY_V0310);
        delete_option(self::LEGACY_PENDING_KEY_V0300);
        delete_option(self::LEGACY_PENDING_KEY_V0290);
        delete_option(self::LEGACY_PENDING_KEY_V0280);
        delete_option(self::LEGACY_PENDING_KEY_V0270);
        delete_option(self::LEGACY_PENDING_KEY_V0260);
        delete_option(self::LEGACY_PENDING_KEY_V0250);
        delete_option(self::LEGACY_PENDING_KEY_V0240);
        delete_option(self::LEGACY_PENDING_KEY_V0230);
        delete_option(self::LEGACY_PENDING_KEY_V0220);
        delete_option(self::LEGACY_PENDING_KEY_V0210);
        delete_option(self::LEGACY_PENDING_KEY_V0200);
        delete_option(self::LEGACY_PENDING_KEY_V0190);
        delete_option(self::LEGACY_PENDING_KEY_V0180);
        delete_option(self::LEGACY_PENDING_KEY_V0170);
        delete_option(self::LEGACY_PENDING_KEY_V0160);
        delete_option(self::LEGACY_PENDING_KEY_V0150);
        delete_option(self::LEGACY_PENDING_KEY_V0140);
        delete_option(self::LEGACY_PENDING_KEY_V0130);
        delete_option(self::LEGACY_PENDING_KEY_V0120);
        delete_option(self::LEGACY_PENDING_KEY_V0110);
        delete_option(self::LEGACY_PENDING_KEY_V0100);
        delete_option(self::LEGACY_PENDING_KEY_V0901);
        delete_option(self::LEGACY_PENDING_KEY_V090);
        delete_option(self::LEGACY_PENDING_KEY_V0831);
        delete_option(self::LEGACY_PENDING_KEY_V083);
        delete_option(self::LEGACY_PENDING_KEY_V082);
        delete_option(self::LEGACY_PENDING_KEY_V081);
        delete_option(self::LEGACY_PENDING_KEY_V080);
        delete_option(self::LEGACY_PENDING_KEY_V070);
        delete_option(self::LEGACY_PENDING_KEY_V061);
        delete_option(self::LEGACY_PENDING_KEY_V060);
        delete_option(self::LEGACY_PENDING_KEY_V041);
        delete_option(self::LEGACY_PENDING_KEY_V040);
        delete_option(self::LEGACY_PENDING_KEY_V030);
        delete_option(self::LEGACY_PENDING_KEY_V020);
        delete_option(self::LEGACY_PENDING_KEY_V010);
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
            'product_url' => '/platform/',
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
            'previous_version' => '0.67.0',
            'release_date' => '2026-08-11',
            'release_name' => 'Performance II: Long Sessions & Very Large Workspaces',
            'change_summary' => 'Performance II adds bounded memory-only session profiling, route/render/index timing, cooperative large-work yields, and explicit long-session pressure diagnostics.',
            'superseded_by' => '',
            'manual_notes' => 'Storage 35 / Project 20.0 remain schema-stable. Performance samples stay bounded in memory, are not uploaded automatically, and never mutate canonical research.',
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
