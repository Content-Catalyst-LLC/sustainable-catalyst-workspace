from app.cross_lingual_semantic_evidence_runtime import *

def _units():
    return [
      {"unitId":"u-de","text":"München ist die Hauptstadt Bayerns.","languageIdentityId":"de","scriptIdentityId":"Latn",
       "unitKind":"claim","conceptIds":["munich","bavaria","capital"],"entityIds":["place:munich","region:bavaria"],"embedding":[1.0,0.0,0.0],"sourceRefs":["src:de"]},
      {"unitId":"u-en","text":"Munich is the capital of Bavaria.","languageIdentityId":"en","scriptIdentityId":"Latn",
       "unitKind":"claim","conceptIds":["munich","bavaria","capital"],"entityIds":["place:munich","region:bavaria"],"embedding":[0.99,0.01,0.0],"sourceRefs":["src:en"]},
      {"unitId":"u-fr","text":"Berlin est la capitale de l'Allemagne.","languageIdentityId":"fr","scriptIdentityId":"Latn",
       "unitKind":"claim","conceptIds":["berlin","germany","capital"],"entityIds":["place:berlin"],"embedding":[0.0,1.0,0.0],"sourceRefs":["src:fr"]},
    ]

def test_cross_language_candidate_search_prefers_semantic_match():
    req=CrossLingualSemanticEvidenceRequest(operation=OPERATIONS[1],units=_units(),
        sourceUnitIds=["u-de"],targetUnitIds=["u-en","u-fr"],topK=2)
    out=execute(req)["result"]["items"][0]["candidates"]
    assert out[0]["targetUnitId"]=="u-en"
    assert "cross-language" in out[0]["signals"]

def test_accepted_equivalence_requires_human_review():
    req=CrossLingualSemanticEvidenceRequest(operation=OPERATIONS[0],units=_units(),
        links=[{"linkId":"l1","sourceUnitId":"u-de","targetUnitId":"u-en","relationType":"equivalent","status":"accepted","humanReviewed":False}])
    out=execute(req)["result"]
    assert out["valid"] is False
    assert any(x["code"]=="accepted-equivalence-requires-human-review" for x in out["issues"])

def test_semantic_link_proposal_never_auto_accepts():
    req=CrossLingualSemanticEvidenceRequest(operation=OPERATIONS[3],units=_units(),
        sourceUnitIds=["u-de"],targetUnitIds=["u-en"])
    item=execute(req)["result"]["items"][0]
    assert item["status"]=="proposed"
    assert item["automaticAcceptanceApplied"] is False

def test_evidence_analysis_does_not_rank_or_determine_truth():
    req=CrossLingualSemanticEvidenceRequest(operation=OPERATIONS[4],units=_units(),
        links=[{"linkId":"l1","sourceUnitId":"u-de","targetUnitId":"u-en","relationType":"supports","status":"reviewed","humanReviewed":True}])
    out=execute(req)["result"]
    assert out["truthDeterminationApplied"] is False
    assert out["automaticEvidenceRankingApplied"] is False
