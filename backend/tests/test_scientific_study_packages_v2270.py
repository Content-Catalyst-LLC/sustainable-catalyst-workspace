from app.study_packages import STUDY_SCHEMA, profile, _bundle_bytes, _manifest_fingerprint
from app.schemas import ScientificStudyPackageCreateRequest, ScientificStudyPackageVerifyRequest
import io, json, zipfile


def test_profile_is_reproducible_and_bounded():
    p=profile()
    assert p["backendAuthoritative"] is True
    assert p["deterministicManifest"] is True
    assert p["artifactRevisionAndSha256Pinning"] is True
    assert p["scientificReceiptClosure"] is True
    assert p["arbitraryCodeExecution"] is False


def test_request_contract_defaults_to_embedded_artifact_snapshots():
    x=ScientificStudyPackageCreateRequest.model_validate({"schema":"sc-workspace-scientific-study-package-request/1.0","projectId":"p1"})
    assert x.includeArtifactBlobs is True and x.includeScientificReceipts is True


def test_verify_request_is_deep_by_default():
    x=ScientificStudyPackageVerifyRequest.model_validate({"schema":"sc-workspace-scientific-study-package-verify-request/1.0"})
    assert x.deep is True


def test_deterministic_bundle_manifest_entry():
    manifest={"schema":STUDY_SCHEMA,"manifestFingerprint":"a"*64,"artifacts":[]}
    a=_bundle_bytes(manifest,[],False); b=_bundle_bytes(manifest,[],False)
    assert a==b
    with zipfile.ZipFile(io.BytesIO(a)) as zf:
        assert json.loads(zf.read("manifest.json"))["schema"]==STUDY_SCHEMA


def test_manifest_fingerprint_excludes_self_field():
    m={"schema":STUDY_SCHEMA,"project":{"projectId":"p1"}}
    fp=_manifest_fingerprint(m); m["manifestFingerprint"]=fp
    assert _manifest_fingerprint(m)==fp
