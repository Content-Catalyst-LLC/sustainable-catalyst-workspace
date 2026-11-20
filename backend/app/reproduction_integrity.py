"""Resolve registered run outputs to stored bytes and verify them at comparison time."""
import hashlib

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ArtifactHead, ArtifactRevision, ExecutionRunOutput
from .object_store import _path_for_key


def check_output(
    db: Session, output: ExecutionRunOutput, *, capture_limit: int = 0,
) -> tuple[dict, bytes | None]:
    evidence = {
        "outputId": output.output_id,
        "artifactId": output.artifact_id,
        "registeredSha256": output.sha256,
        "registeredBytes": output.bytes,
    }
    if not output.artifact_id or not output.sha256:
        return {**evidence, "status": "unavailable", "reason": "unverifiable-reference"}, None

    # A registered output records a digest and size, not the current artifact head.
    artifact = db.scalar(
        select(ArtifactRevision).where(
            ArtifactRevision.user_key == output.user_key,
            ArtifactRevision.artifact_id == output.artifact_id,
            ArtifactRevision.sha256 == output.sha256,
            ArtifactRevision.bytes == output.bytes,
        ).order_by(ArtifactRevision.revision.desc()).limit(1)
    )
    if artifact is None:
        head = db.get(ArtifactHead, (output.user_key, output.artifact_id))
        if head is None or (head.sha256, head.bytes) != (output.sha256, output.bytes):
            return {**evidence, "status": "missing", "reason": "registered-artifact-revision-missing"}, None
        artifact = head

    evidence["artifactRevision"] = artifact.revision
    digest = hashlib.sha256()
    observed_bytes = 0
    content = bytearray() if 0 < capture_limit and output.bytes <= capture_limit else None
    try:
        with _path_for_key(artifact.storage_key).open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                observed_bytes += len(chunk)
                if content is not None:
                    if observed_bytes <= capture_limit:
                        content.extend(chunk)
                    else:
                        content = None
    except FileNotFoundError:
        return {**evidence, "status": "missing", "reason": "artifact-blob-missing"}, None
    except (OSError, HTTPException):
        return {**evidence, "status": "unavailable", "reason": "artifact-storage-unavailable"}, None

    observed_digest = digest.hexdigest()
    evidence.update(observedSha256=observed_digest, observedBytes=observed_bytes)
    if (observed_digest, observed_bytes) != (output.sha256, output.bytes):
        return {**evidence, "status": "corrupted", "reason": "registered-content-mismatch"}, None
    return {**evidence, "status": "verified"}, bytes(content) if content is not None else None
