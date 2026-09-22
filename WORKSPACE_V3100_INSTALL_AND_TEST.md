# Workspace v3.1.0 Install and Test

1. Promote the repository release/tag.
2. Deploy and verify the backend first.
3. Install `sustainable-catalyst-workspace-v3.1.0-wordpress-plugin.zip` in WordPress.
4. Keep the existing WordPress shortcode registry guard enabled; this release does not add new public WordPress shortcodes.
5. Verify the Workspace page and backend proxy after plugin update.

## WordPress smoke

```bash
curl -L -s -o /dev/null -w '%{http_code}\n' https://sustainablecatalyst.com/platform/
```

Expected: `200`.

## Backend/Core integration smoke

The WordPress plugin proxies Platform Core runtime access through the Workspace backend. The Core write key is server-only and must never be localized into JavaScript or returned in browser configuration.
