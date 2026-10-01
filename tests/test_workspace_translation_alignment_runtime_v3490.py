from backend.app.translation_alignment_runtime import TranslationAlignmentRuntimeRequest, OPERATIONS, execute

def req(operation):
    return TranslationAlignmentRuntimeRequest.model_validate({
        "schema":"sc-workspace-translation-alignment-runtime-request/1.0","operation":operation,
        "transformations":[{"transformationId":"t1","transformationType":"translation","sourceTextId":"ar","derivedTextId":"en","sourceLanguageTag":"ar","targetLanguageTag":"en","method":"human"}],
        "segments":[{"segmentId":"s1","textId":"ar","languageTag":"ar","text":"مرحبا"},{"segmentId":"s2","textId":"en","languageTag":"en","text":"Hello"}],
        "alignments":[{"alignmentId":"a1","sourceSegmentIds":["s1"],"targetSegmentIds":["s2"],"relation":"1:1","method":"human"}],
    })

def test_all_operations():
    for operation in OPERATIONS:
        x=execute(req(operation))
        assert x["operation"]==operation
        assert x["policy"]["originalLanguageFirst"] is True
        assert x["policy"]["automaticTranslationEnabled"] is False
        assert x["policy"]["automaticAlignmentEnabled"] is False

def test_coverage_and_lineage():
    assert execute(req("workspace.linguistics.parallel-alignment-coverage"))["result"]["coverage"]==1.0
    x=execute(req("workspace.linguistics.translation-alignment-lineage"))["result"]
    assert x["transformationEdgeCount"]==1 and x["alignmentEdgeCount"]==1
    assert x["originalLanguageRemainsCanonical"] is True
