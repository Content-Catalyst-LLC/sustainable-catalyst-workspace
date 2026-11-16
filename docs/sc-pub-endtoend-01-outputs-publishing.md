# SC-PUB-ENDTOEND-01 — Outputs & Publishing

Workspace is where a researcher writes and requests release. Research decides and holds every released revision.
The public Research Hub on sustainablecatalyst.com only displays what Research serves. There is one publishing path.

## What a researcher does

1. In the Scientific Publication Studio, write an output (overview, report, brief, ...). Each save is an immutable
   Studio revision with its SHA-256. One project can hold many outputs; each is released or kept private separately.
2. **Outputs & Publishing** → *Bind* the output to a Research area and article slug. Binding is idempotent; an output
   has one article and two outputs never share one.
3. *Send revision*: the exact Studio revision (document id, revision, SHA-256) and the cited Research objects, pinned
   to their current content hashes, become a Research revision. Repeating it is a no-op.
4. Cited evidence: request scientific, rights, ownership and publication approvals; when signed, *Release evidence*
   (Research checks provenance, lineage, reproduction and figure rights).
5. *Submit*, then request the four article approvals. People holding `approver:<dimension>` grants decide in their
   inbox with step-up; nobody approves their own request; the owner decides only `ownership` raised by an editor.
6. The area steward publishes the area once (a signed `area-publication` approval, typed area slug).
7. *Publish* (typed article slug). Later revisions go through review while the published revision stays public.
8. *Unlist* (link only, `noindex`), *Relist*, *Withdraw* (typed slug, public notice, 410 tombstone).

Every state shown comes from Research's response, and every action stores Research's receipt in the project.
Research refusals are shown as Research worded them; Workspace records nothing for a refused action.

## Security

- The Studio sends each Research request as the signed-in person (`sc-workspace-research-session/1.0`, ≤300 s).
- The Studio holds **no** Research signing key. With `SC_WORKSPACE_RESEARCH_SIGNING_BACKEND_URL` set, it asks the
  backend (forwarding only the person's cookie and Origin) for their session and to sign approval decisions, and uses a
  session only if it names exactly that person and sign-in method.
- Writes need an allowlisted Origin; projects are owner-scoped; strangers get 404; Research must be `https` unless
  `SC_WORKSPACE_RESEARCH_API_ALLOW_HTTP` is set for isolated staging.

## Configuration (Studio)

| Setting | Production |
|---|---|
| `SC_WORKSPACE_RESEARCH_API_ORIGIN` | `https://research-api.sustainablecatalyst.com` |
| `SC_WORKSPACE_RESEARCH_SIGNING_BACKEND_URL` | `http://sc-workspace-backend:8089` |
| `SC_WORKSPACE_RESEARCH_HUB_URL` | default `https://sustainablecatalyst.com/research-hub/` |

Unset Research origin: the panel lists outputs and disables every control.

## Verification

- `backend/tests/test_sc_pub_e2e01_outputs.py` (CI: `sc-pub-e2e-01.yml`): fake Research that verifies every signature.
- `scripts/sc_pub_e2e01_staging_harness.py`: isolated staging, genuine PostgreSQL for Workspace and Research,
  synthetic SC Identity people with TOTP and step-up, keyless Studio. 36 checks, including an anonymous sweep of every
  public Research route for private sibling text, owner scope, project id and source hash.

## Release

`scripts/sc_pub_e2e01_release.py` with `SC_PUB_E2E01_SOURCE_SHA=<merged main sha>`: `build` (exact source, image
smoke, no cutover) → `recover` (off-host backup + isolated restore, receipt valid 24 h) → `deploy` (main ancestry,
overlay check, typed confirmation, `studio.sh` cutover, post-cutover probes, automatic rollback) → `rollback` if needed.
The release ships SC-PUB-LAYOUT-01 too. It publishes nothing; a real public release needs the owner's approval of the
exact output and revision.
