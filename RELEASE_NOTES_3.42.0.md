# Workspace v3.42.0 — Advanced Accelerator Scheduling & Resource Governance

Workspace v3.42.0 extends the v3.41 distributed neural worker fabric with bounded, declarative accelerator scheduling and resource-governance objects.

## New governed operations

- `workspace.neural.accelerator-inventory-contract`
- `workspace.neural.accelerator-resource-request`
- `workspace.neural.accelerator-quota-evaluate`
- `workspace.neural.accelerator-admission-decision`
- `workspace.neural.accelerator-placement-plan`
- `workspace.neural.accelerator-reservation-plan`
- `workspace.neural.accelerator-preemption-plan`
- `workspace.neural.accelerator-scheduling-receipt`

The neural registry advances from 117 to 125 operations. No database migration is required.

## Governance boundary

The runtime produces scheduling plans and receipts only. It does not provision infrastructure, mutate cloud resources, connect to client-supplied scheduler endpoints, accept credentials, or execute arbitrary remote code. Accelerator inventory must reference devices already declared by the governed v3.41 worker pool.

## Frontend continuity

The v3.41.0.1 frontend repair is carried forward as the v3.42.0 asset baseline. Current-version CSS/JS remain substantive and the canonical plugin-root checks remain active.
