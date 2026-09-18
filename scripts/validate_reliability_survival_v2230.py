from pathlib import Path
import json, py_compile
root=Path(__file__).resolve().parents[1]
required=['backend/reliability-runtime/service.py','backend/migrations/023_reliability_survival_failure_time.sql','schemas/sc-workspace-reliability-analysis-result-v1.schema.json','schemas/sc-workspace-reliability-analysis-receipt-v1.schema.json','backend/tests/test_reliability_survival_v2230.py']
for rel in required: assert (root/rel).is_file(), rel
for rel in ['backend/reliability-runtime/service.py','backend/app/config.py','backend/app/models.py','backend/app/polyglot.py','backend/app/main.py']:
    py_compile.compile(str(root/rel),doraise=True)
for rel in ['schemas/sc-workspace-reliability-analysis-result-v1.schema.json','schemas/sc-workspace-reliability-analysis-receipt-v1.schema.json','release-manifest-v2.23.0.json']:
    json.load(open(root/rel))
s=(root/'backend/app/main.py').read_text(); assert 'reliabilitySurvivalFailureTimeRuntime' in s and 'reliabilityAnalysisReceipts' in s
print('PASS - v2.23.0 reliability, survival & failure-time contract')
