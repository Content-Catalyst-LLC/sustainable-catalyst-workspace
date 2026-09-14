# Workspace v2.7.0 — Controlled Runtime Handoffs

Workspace v2.7.0 adds a bounded bridge between reproducibility records and the existing durable job/orchestration layer.

A reproduction execution plan is a frozen execution envelope. It references an existing v2.6 reproduction plan and a planned reproduction run, then verifies that inputs, execution environment, runtime adapter, target product, operation, adapter capability, and server-side route are still compatible. Creating the plan never queues work.

Dispatch is a separate human-authorized operation. The client cannot replace the frozen target or operation and cannot provide a runtime URL, service credential, or shell command. Workspace creates the durable job from the frozen envelope and writes an immutable runtime-handoff receipt.

Specialist execution remains owned by the routed Sustainable Catalyst product. Workspace remains the orchestration and provenance layer.
