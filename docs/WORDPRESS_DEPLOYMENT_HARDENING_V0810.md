# Workspace v0.81.0 — WordPress & Deployment Hardening

## Purpose

v0.81.0 hardens the WordPress deployment boundary while the Workspace remains feature-frozen as a Release Candidate. It introduces no canonical project capability and no schema migration.

## Server bootstrap guard

The main plugin now checks that the core PHP bootstrap files exist and are readable before requiring them. An incomplete WordPress package therefore fails closed to an administrator-visible bootstrap warning instead of blindly calling a missing include and creating an avoidable site-wide PHP fatal.

The deployment class separately checks the current cumulative JavaScript/CSS, deployment runtime/UI, and inherited Release Candidate runtime. These checks inspect release files only; they never inspect browser-local projects.

## Activation and upgrade observation

The plugin records a bounded server-side deployment marker when a new Workspace version is first observed. The history is limited to twelve version transitions and contains only release version, transition source, and timestamp. It is not project telemetry.

Activation has an explicit preflight for required release files plus the declared WordPress/PHP minimums. Registry registration remains separate and pending registry state is surfaced as a deployment warning rather than silently treated as healthy.

## Mixed-version browser detection

Review → Deployment checks that the rendered root, WordPress-localized configuration, cumulative script, cumulative stylesheet, and Release Candidate stage all agree on v0.81.0. A current HTML shell with an older cumulative asset is treated as blocked.

The release continues to use versioned cumulative filenames plus the WordPress `?ver=` query. v0.81.0 does not automatically purge caches: cache invalidation remains an explicit deployment operation because browser-local project storage must never be treated as a cache.

## Rollback boundary

The v0.81.0 release bundle includes the validated v0.80.0 WordPress plugin as the rollback artifact. Storage remains 35 and Project/Export remain 20.0, so this RC step introduces no project migration that would make the prior RC unreadable.

Rollback remains manual. The plugin does not self-replace, automatically deactivate itself, or rewrite project data.

## Navigation defect closed

During the deployment audit, the central Research Navigation map was found to lag the newer Review surfaces. Final Audit, Beta Closure, Release Candidate, and the new Deployment view are now registered in the same navigation map used by runtime view validation. This closes a real route-consistency defect without changing canonical data.

## Human production validation

Automated deployment coherence does not certify production. After upload, verify the WordPress replacement metadata, activation/public-page smoke, REST health, anonymous/authenticated use, preservation of an existing browser-local project, cache coherence, and a v0.80.0 rollback rehearsal.
