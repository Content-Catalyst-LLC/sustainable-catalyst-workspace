# v0.82.1 — Production Certification Installer & Validation Lineage Repair

v0.82.1 is a surgical Release Candidate repair. It responds to a deployment failure in which the v0.82.0 installer reached an inherited Security & Privacy Audit II gate that evaluated a different plugin-version state than the release being installed.

## Repair boundary

The release does not add a product subsystem and does not migrate Workspace data. Storage remains 35, Project remains `sc-workspace-project/20.0`, and Project Export remains `sc-workspace-project-export/20.0`.

The repair separates two concepts that earlier validators sometimes conflated:

1. **Historical contract identity** — the release/version in which a capability or gate was introduced.
2. **Current installed release identity** — the WordPress header, runtime constant, current manifest/registry, cumulative JS/CSS, deployment predecessor, and certification predecessor in the tree being installed now.

Historical validators keep checking their original release manifests. Current-runtime checks derive the active release from the plugin tree.

## Installer lineage gates

The v0.82.1 installer must:

- verify the repository archive and v0.81.0 rollback ZIP;
- extract the source to an isolated temporary directory;
- verify source lineage as v0.82.1 <- v0.82.0 **before** touching the Git target;
- require a clean Git target and fast-forward it;
- rsync the exact source into the target;
- immediately verify the post-rsync target lineage;
- run the complete inherited release/test/runtime suite;
- verify WordPress's compact 8 KiB plugin header;
- stage the Git tree;
- verify lineage again on the exact staged working tree before commit;
- abort before commit/push on any mismatch.

No failed lineage state is allowed to create a release commit or push.

## Claim boundary

Passing v0.82.1 repairs package/install validation. It does not itself complete the live production field checks defined by v0.82.0.
