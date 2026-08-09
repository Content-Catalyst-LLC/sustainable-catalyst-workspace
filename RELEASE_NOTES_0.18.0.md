# Sustainable Catalyst Workspace v0.18.0

## Collaboration Foundation

v0.18.0 introduces structured asynchronous review without changing the free personal Workspace into a shared cloud tenant.

### Changes
- Adds the top-level Collaborate environment.
- Adds local review identity with descriptive owner/contributor/reviewer/observer roles.
- Adds review sessions linked to existing projects.
- Adds object-linked comment, suggestion, and question threads with open/resolved state.
- Adds explicit review status from Draft through Approved/Closed.
- Adds SHA-256-fingerprinted portable review-request packages containing privacy-minimized project copies.
- Adds portable review-response packages containing feedback but no project content.
- Imports review requests as new local project copies.
- Requires matching request ID + source project ID before response feedback can be committed.
- Never mutates source project content automatically from imported feedback.
- Integrates open collaboration reviews into explainable Activity Intelligence signals.

### Business and governance boundary
Roles are descriptive review responsibilities in v0.18.0, not server-enforced permissions. There is no live co-editing, cloud team directory, organization membership, shared project server, or institutional access-control plane. Those capabilities remain outside the personal Workspace boundary.

### Data boundary
Storage advances from schema 18 to 19. Project schema remains `sc-workspace-project/11.0`; collaboration state is Workspace-level and references canonical projects/objects.
