# SC-PUB-TIPTAP-01 — Production Reporting Studio deployment

**Approved source:** Workspace commit \`13b9dd34131829a5dc8f2a1ad508d613830315a3\` (PR #53, merged).  
**Target service:** \`sc-workspace-reporting-live\`, existing Contabo Reporting Studio.  
**Candidate image tag:** \`sc-workspace-reporting:tiptap-13b9dd341318\`.  
**Status:** Operator script committed; **NOT YET RUN ON CONTABO OR DEPLOYED**. Production status must be established by \`status\`, not by an old server transcript.

## What's already accepted

- PR #53 contains Tiptap 3.34.0, local bundle build, source-preserving scientific Markdown, Citation Studio handling, five report output types and institutional DOCX/PDF/HTML export.
- All four relevant PR #53 workflows passed (Tiptap build, Chromium test, branded exports, SC-CITE-01, SC-MODEL-01 and Research authority checks). These were **source/isolated acceptance** only.
- No SQL changes or WordPress changes are required for this release.
- The historical \`scripts/sc_cite01_release.sh\` targets older \`candidate-43be67f\` and \`prod-5e354cba\`. **Do not use it for the Tiptap deployment**.

## Trusted infrastructure path

The operator runs on the Mac over existing SSH, not in GitHub Actions. It uses \`git archive\` of **only the merged source SHA's \`backend/\`**, transfers it through trusted SSH, labels and builds a new **immutable** candidate image, then verifies the Tiptap bundle offline. It uses the established \`$HOME/sc-sci02/rd/studio.sh cutover\` and \`rollback\` only after verifying the exact current live container/image and fresh off-host recovery receipts.

The candidate build requires at least 12 GiB available disk and 1.5 GiB available memory on Contabo. It refuses to overwrite an existing candidate image tag or a release-scoped source directory. Do **not** prune unrelated Docker images, volumes or live services to make space.

## Operator commands (Mac Terminal; exact approved source)

\`\`\`bash
# Use an existing local repository clone, or clone the Workspace repo once.
cd ~/sustainable-catalyst-workspace
git fetch origin main release/sc-pub-tiptap-production-20261115
git switch release/sc-pub-tiptap-production-20261115
git pull --ff-only

# Confirm current live Studio health, baseline and private-route denial.
python3 scripts/sc_pub_tiptap_release.py status

# Prepare the exact reviewed source image on Contabo.
# Does not replace, restart or alter the live Studio.
python3 scripts/sc_pub_tiptap_release.py build

# Set a NEW path under adequate, encrypted off-host storage.
# Do not create this leaf directory yourself: the recovery gate creates it.
export SC_PUB_TIPTAP_BACKUP_DIR="/Volumes/EncryptedResearchBackups/sc-pub-tiptap-20261115"
export SC_PUB_TIPTAP_RECOVERY_AUTHORIZATION=READ_ONLY_PRODUCTION_TO_OFFHOST

# Production: read-only pg_dump and read-only volume archive.
# Both archives are restored into separately named scratch resources
# with Docker --network none, and retained off-host with verified hashes.
python3 scripts/sc_pub_tiptap_release.py recover

# Only after all previous gates pass: interactive cutover confirmation.
# A wrong / missing receipt, changed live image, missing Tiptap bundle,
# unexpected anonymous authorization response or failed health blocks cutover.
python3 scripts/sc_pub_tiptap_release.py deploy
\`\`\`

**Do not copy the example encrypted volume path literally.** Pick an existing encrypted, off-host backup volume with sufficient space. The precise \`SC_PUB_TIPTAP_BACKUP_DIR\` must not exist until \`recover\` creates it. The operator never asks for a password/token in the command line and does not print private research or environment secrets.

\`--deploy\` requires the terminal operator to type \`DEPLOY SC-PUB-TIPTAP-01\`. It refuses non-interactive operation. The release script validates the independently produced restore evidence (schema, release, age <= 24h, matching live image, isolated DB/data restore, table/file counts, SHA-256 hashes of both archives). It compares the running container identity with the baseline recorded at build time and the candidate image digest with the exact approved source label.

A guarded cutover uses the existing server-managed backup and rollback. Post-cutover it checks live health (HTTP 200), exact image digest, absence of anonymous access to the editor bundle (401/403), and existence of the locally built Tiptap bundle in the running container. If the post-cutover checks fail, it attempts rollback.

## Actual owner browser acceptance after cutover

In the authenticated Workspace:

1. Open \`/v1/private-research/reporting-studio/publication\` and confirm **Tiptap** initializes. Anonymous access must remain denied; no editor service credentials appear in the browser.
2. Open the **existing Wexford scientific report** and **existing policy brief** (different document IDs). Do not create new project or reimport the existing source material.
3. Switch *Visual editor -> Markdown source -> Visual editor* without edits. Confirm every original citation marker, equation, figure reference, table and source digest is unchanged.
4. Make one deliberately identifiable, reversible text edit to a **draft** revision. Confirm immutable revision, conflict protection, citation rendering and source hash provenance.
5. Export the **same saved revision** to HTML, PDF and DOCX. Confirm institutional black/white/red styling, citations, mathematics and figures are complete; scientific provenance/verification notice is accurate.
6. Open Notebook Desk/Figure Studio links and confirm they resolve to the current project; do not claim full governed notebook/map insertion from Tiptap until that separate capability exists.
7. If a real-owner acceptance check fails, **roll back the Studio** promptly and keep existing document revisions/exports intact.

Manual reversible rollback (only if the live Studio is this exact Tiptap candidate):

\`\`\`bash
python3 scripts/sc_pub_tiptap_release.py rollback
# Type: ROLLBACK SC-PUB-TIPTAP-01
\`\`\`

## Explicit non-goals

This deployment **does not** enable Research editorial production writes, release a Wexford paper on the public Research Hub, change authentication issuers, modify WordPress/Bluehost, or approve rights. No new PostgreSQL schema, staging database or parallel scientific editor is created.

## Evidence to retain privately

- Source commit and exact candidate image ID, stored in \`~/.sc-pub-tiptap/sc-pub-tiptap-13b9dd341318.json\`.
- Immutable, current \`sc-pub-tiptap-recovery.json\` and the two verified off-host archives.
- Operator cutover time, prior/new live container and image digests.
- Authenticated Wexford editor and DOCX/PDF/HTML acceptance record, with only non-sensitive hashes/IDs in GitHub.

**Release result remains unverified until the operator actually executes these commands and returns the final guarded cutover outcome.** GitHub source merge or green CI is not a production deployment.
