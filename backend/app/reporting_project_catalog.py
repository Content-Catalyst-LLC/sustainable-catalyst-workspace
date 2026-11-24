"""RD-01.1.2: session-owned read-only bridge for the existing Reporting Studio.

The two Workspace artifact stores are NOT equivalent: the legacy research-artifact
rows hold blobs in private-research/, whereas native ArtifactHead rows live under
the hash-addressed object_store namespace. Never synthesize native IDs/hashes.
"""
from __future__ import annotations

from urllib.parse import quote
from sqlalchemy import inspect, text


def catalog_projects(projects: list[dict]) -> dict:
    return {
        'schema': 'sc-reporting-project-catalog/1.0',
        'projects': [
            {'projectId': p['projectId'], 'title': p['title'],
             'revision': p['revision']}
            for p in projects
        ],
    }


def read_legacy_artifacts(db, owner: str, project_id: str) -> tuple[list[dict], bool]:
    # The source schema may be older on isolated acceptance installations.
    # Check existence without causing schema creation or modifications.
    table = 'workspace_private_research_artifacts'
    if not inspect(db.get_bind()).has_table(table):
        return [], False
    rows = db.execute(text("""
        SELECT artifact_id, branch_id, filename, media_type, sha256, byte_count
        FROM workspace_private_research_artifacts
        WHERE user_key = :owner AND project_id = :project_id
        ORDER BY created_at, artifact_id
    """), {'owner': owner, 'project_id': project_id}).mappings().all()
    result = []
    for row in rows:
        ident = str(row['artifact_id'])
        result.append({
            'artifactId': ident,
            'branchId': row['branch_id'],
            'filename': row['filename'],
            'mediaType': row['media_type'],
            'sha256': row['sha256'],
            'bytes': row['byte_count'],
            'storageClass': 'legacy-private-research',
            'editableInFigureStudio': False,
            'downloadUrl': ('/v1/private-research/projects/' + quote(project_id, safe='')
                            + '/artifacts/' + quote(ident, safe='')),
        })
    return result, True


def catalog_details(project: dict, package: dict, native: list[dict],
                    legacy: list[dict], legacy_catalog_present: bool) -> dict:
    ident = project['projectId']
    # The protected owner-scoped query is the authority. Never pass unrelated
    # native artifacts from the same account to a different project.
    files = [dict(f) for f in native if f.get('projectId') == ident]
    eligible = [f['artifactId'] for f in files
                if str(f.get('filename', '')).lower().endswith('.json')
                and isinstance(f.get('metadata'), dict)
                and f['metadata'].get('source') == 'private-research'
                and isinstance(f.get('revision'), int)
                and f['revision'] >= 1
                and isinstance(f.get('sha256'), str)
                and len(f['sha256']) == 64]
    return {
        'schema': 'sc-reporting-project-detail/1.0',
        'project': project,
        'package': package,
        'files': files,
        'eligibleSourceIds': eligible,
        'legacyFiles': legacy,
        'legacyCatalogPresent': legacy_catalog_present,
        'reportEditingRequiresNativeArtifact': True,
    }
