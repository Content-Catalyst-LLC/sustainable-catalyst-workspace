# v0.72.0 — Research Workflow Guidance & Empty-State Refinement

v0.72.0 improves orientation inside an already capable Workspace. It does not add a new research object, readiness score, workflow engine, or automated research agent.

## Contextual next step

Research Home and the active Project Research surface now show one contextual next step derived from visible local counts. The sequence is advisory: orient to a project, frame a question, gather sources, extract evidence, connect claims, synthesize in Notebook, compose stable work, then review explicit next actions.

The guidance does not infer whether the research is correct or complete. It does not create tasks, change lifecycle state, invoke AI, navigate automatically, or mutate canonical research.

## Empty-state refinement

Blank surfaces now explain both why they are empty and what explicit action can populate them. Research questions, reading queues, claims, notebooks, tasks, and Integrated Knowledge use action-oriented language while preserving the local-first and canonical-record boundaries.

## Privacy and persistence

Guidance is derived at runtime from counts already rendered by Workspace. No behavioral profile is stored. No telemetry or automatic submission is introduced. The optional report contract contains counts and the derived next-step identifier, not project titles, descriptions, object text, source URLs, queries, or device identifiers.

## Schema stability

Storage remains `35`; Project remains `sc-workspace-project/20.0`; Project Export remains `sc-workspace-project-export/20.0`. No migration is required.
