from app.source_evidence_citation_workspace import profile

def test_v3750_profile():
    x=profile()
    assert x["version"]=="3.75.0"
    assert x["referenceFirst"] is True
    assert x["derivedCitationReferences"] is True
    assert x["locatorPreserving"] is True
    assert x["fingerprintPinning"] is True
    assert x["databaseMigrationRequired"] is False
    assert x["automaticEvidenceRanking"] is False
    assert x["automaticTruthDetermination"] is False
