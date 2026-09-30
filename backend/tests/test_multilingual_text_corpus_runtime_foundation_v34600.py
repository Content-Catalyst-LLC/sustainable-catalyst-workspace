from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

P = Path(__file__).resolve().parents[1] / "app" / "multilingual_corpus_runtime.py"
spec = importlib.util.spec_from_file_location("sc_workspace_multilingual_v34600", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
ROOT = P.parents[1]
REPO = ROOT.parent


def req(**kwargs):
    return m.MultilingualCorpusRuntimeRequest(**kwargs)


def test_profile_is_bounded_original_language_first_foundation():
    p = m.profile()
    assert p["version"] == "3.46.0"
    assert p["schema"] == "sc-workspace-multilingual-text-corpus-runtime/1.0"
    assert p["boundedOperationCount"] == 6
    assert p["originalLanguageFirst"] is True
    assert p["translationIsDerivedRepresentation"] is True
    assert p["automaticLanguageDetectionEnabled"] is False
    assert p["automaticTranslationEnabled"] is False
    assert p["externalNetworkAccessEnabled"] is False
    assert p["arbitraryCodeExecution"] is False


def test_unicode_normalization_preserves_source_and_records_derived_result():
    source = "Cafe\u0301"
    out = m.execute(req(
        operation="workspace.linguistics.text-normalize",
        text=source,
        languageTag="fr",
        script="Latn",
        normalizationForm="NFC",
    ))
    r = out["result"]
    assert r["resultText"] == "Café"
    assert r["changed"] is True
    assert r["sourcePreserved"] is True
    assert r["derivedRepresentation"] is True
    assert r["sourceSha256"] != r["resultSha256"]


def test_segmentation_is_deterministic_and_does_not_claim_linguistic_annotation():
    out = m.execute(req(
        operation="workspace.linguistics.text-segment",
        text="第一句。 第二句！ Third sentence?",
        languageTag="zh-Hans",
        script="Hans",
        segmentMode="simple-sentence",
    ))
    r = out["result"]
    assert r["segmentCount"] == 3
    assert r["linguisticAnnotationApplied"] is False
    assert [x["segmentIndex"] for x in r["segments"]] == [0, 1, 2]


def test_corpus_profile_is_multilingual_and_fingerprint_is_order_independent():
    docs = [
        {"documentId":"orig","text":"Bonjour","languageTag":"fr","script":"Latn","representation":"original"},
        {"documentId":"ar","text":"مرحبا","languageTag":"ar","script":"Arab","representation":"original"},
        {"documentId":"en","text":"Hello","languageTag":"en","script":"Latn","representation":"derived","derivedFromId":"orig","transformation":"translation"},
    ]
    a = m.execute(req(operation="workspace.linguistics.corpus-profile", documents=docs))["result"]
    b = m.execute(req(operation="workspace.linguistics.corpus-profile", documents=list(reversed(docs))))["result"]
    assert a["documentCount"] == 3
    assert a["languageDistribution"] == {"ar":1,"en":1,"fr":1}
    assert a["originalDocumentCount"] == 2
    assert a["derivedDocumentCount"] == 1
    assert a["corpusFingerprintSha256"] == b["corpusFingerprintSha256"]
    assert a["automaticLanguageDetectionApplied"] is False


def test_translation_is_lineage_only_not_automatic_translation():
    docs = [
        {"documentId":"source","text":"La mer","languageTag":"fr","script":"Latn","representation":"original","sourceRef":"urn:test:source"},
        {"documentId":"derived","text":"The sea","languageTag":"en","script":"Latn","representation":"derived","derivedFromId":"source","transformation":"translation"},
    ]
    r = m.execute(req(operation="workspace.linguistics.corpus-lineage", documents=docs))["result"]
    reversed_r = m.execute(req(operation="workspace.linguistics.corpus-lineage", documents=list(reversed(docs))))["result"]
    assert r["edgeCount"] == 1
    assert r["edges"][0]["transformation"] == "translation"
    assert r["translationIsDerivedRepresentation"] is True
    assert r["automaticTransformationApplied"] is False
    assert r["lineageFingerprintSha256"] == reversed_r["lineageFingerprintSha256"]


def test_fail_closed_without_language_or_broken_lineage():
    with pytest.raises(ValueError):
        m.execute(req(operation="workspace.linguistics.text-identity", text="hello"))
    with pytest.raises(ValueError):
        m.execute(req(operation="workspace.linguistics.corpus-lineage", documents=[
            {"documentId":"derived","text":"Hello","languageTag":"en","representation":"derived","derivedFromId":"missing","transformation":"translation"}
        ]))


def test_backend_and_wordpress_release_integration_markers():
    main = (ROOT / "app" / "main.py").read_text()
    config = (ROOT / "app" / "config.py").read_text()
    contracts = (ROOT / "app" / "client_contracts.py").read_text()
    assert 'service_version: str = "3.46.0"' in config
    assert '"multilingualTextCorpusRuntime": True' in main
    assert '/v1/multilingual-text-corpus-runtime' in main
    assert '"multilingualTextCorpusRuntime"' in contracts
    if (REPO / "wordpress").exists():
        wp = REPO / "wordpress" / "sustainable-catalyst-workspace"
        plugin = (wp / "sustainable-catalyst-workspace.php").read_text()
        cls = (wp / "includes" / "class-sc-workspace.php").read_text()
        dep = (wp / "includes" / "class-sc-workspace-deployment.php").read_text()
        assert "Version: 3.46.0" in plugin
        assert "SC_WORKSPACE_VERSION', '3.46.0'" in plugin
        assert "workspace-v3.46.0.css" in cls and "workspace-v3.46.0.js" in cls
        assert "const PREVIOUS_RELEASE = '3.45.0';" in dep
        assert "const ROLLBACK_RELEASE = '3.45.0';" in dep
        assert (wp / "assets/css/workspace-v3.46.0.css").stat().st_size >= 100000
        assert (wp / "assets/js/workspace-v3.46.0.js").stat().st_size >= 5000


def test_release_is_non_migrating():
    assert not (ROOT / "migrations" / "0042_workspace_v34600.sql").exists()
