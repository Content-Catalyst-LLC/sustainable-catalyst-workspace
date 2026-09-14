# Workspace v2.8.0 Validation Report

## Release
**Sustainable Catalyst Workspace v2.8.0 — Execution Policy, Resource Budgets & Runtime Sandboxing**

Validated against the v2.7.0 source baseline on 2026-09-14.

## Release-specific gate

The v2.8.0 release gate passed:

- structural validator: **PASS**
- targeted Python/backend contract tests: **40 passed**
- Python bytecode compilation: **PASS**
- WordPress PHP syntax: **31/31 files PASS**
- release manifest JSON: **PASS**
- product registry JSON: **PASS**
- execution-policy JSON Schema: **PASS**
- VPS deployment script `bash -n`: **PASS**

The targeted gate validates:

- v2.8.0 release identity and v2.7.0 lineage
- additive migration 008 and PostgreSQL grants
- revisioned execution-policy registry and immutable policy-decision receipts
- runtime-adapter trust levels (`untrusted`, `bounded`, `trusted`)
- fail-closed target/operation allowlists
- bounded CPU, memory, wall-time, output, PID, and temporary-storage requests
- hard denial of host-filesystem, Docker-socket, and privileged execution
- sandbox and network requirement contracts
- execution-policy requirement on reproduction execution plans
- frozen policy-decision revalidation before durable job creation
- propagation of policy, resource-budget, and sandbox envelopes through server-side routing
- WordPress server-proxy routes and backend capability flags
- explicit prohibition of client-supplied runtime URLs/credentials and arbitrary code execution

## Historical suite

The complete historical test tree produced:

- **1,156 passed**
- **123 failed**

The failures are legacy assertions that hard-code earlier releases as the current Workspace version, asset set, README heading, or release lineage. Examples include assertions requiring v2.0.4 plugin identity and v1.10.0 documentation headings. They are retained historical test debt and are not failures of the v2.8.0 execution-policy contracts.

No v2.8-targeted test failed.

## Enforcement boundary

v2.8.0 enforces a **pre-dispatch policy gate**. Workspace freezes and evaluates the policy revision, resource request, adapter trust, route, and sandbox requirements before a controlled handoff can become eligible. Human authorization remains a separate required action.

Strict kernel/container enforcement of CPU, memory, process, filesystem, or network isolation belongs to the selected specialist runtime/sandbox adapter. Workspace does not become a general shell, accept arbitrary command strings, expose service credentials, or execute client-supplied runtime URLs.

## Release-lineage checks

- current release: `2.8.0`
- previous release: `2.7.0`
- rollback release: `2.7.0`
- storage schema: `35`
- project schema: `sc-workspace-project/20.0`
- export schema: `sc-workspace-project-export/20.0`
- PostgreSQL migration: `008_execution_policy_resource_budgets_sandboxing.sql`
