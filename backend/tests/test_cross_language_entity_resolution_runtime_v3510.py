from app.cross_language_entity_resolution_runtime import *
def test_ambiguous_and_resolved_candidates():
    req=CrossLanguageEntityResolutionRequest(operation=OPERATIONS[4],entities=[
      {"entityId":"p1","entityType":"place","canonicalLabel":"München","nameForms":[{"nameId":"n1","text":"Munich","kind":"exonym","languageIdentityId":"en"}],"regions":["Bavaria"]},
      {"entityId":"p2","entityType":"place","canonicalLabel":"Munich","regions":["North Dakota"]}],queries=[{"queryId":"q1","text":"Munich","entityType":"place","regions":["Bavaria"]}])
    out=execute(req); item=out['result']['items'][0]; assert item['status']=='resolved' and item['entityId']=='p1'
def test_toponym_filter():
    req=CrossLanguageEntityResolutionRequest(operation=OPERATIONS[2],entities=[{"entityId":"x","entityType":"person","canonicalLabel":"Paris"},{"entityId":"y","entityType":"place","canonicalLabel":"Paris"}],queries=[{"queryId":"q","text":"Paris"}])
    rows=execute(req)['result']['items'][0]['candidates']; assert [x['entityId'] for x in rows]==['y']
