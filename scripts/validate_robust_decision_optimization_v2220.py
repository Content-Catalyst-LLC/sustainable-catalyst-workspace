from pathlib import Path
import json, py_compile
root=Path(__file__).resolve().parents[1]
required=[
 'backend/decision-runtime/service.py','backend/migrations/022_robust_decision_optimization_pareto.sql',
 'schemas/sc-workspace-decision-optimization-result-v1.schema.json','schemas/sc-workspace-decision-optimization-receipt-v1.schema.json',
 'backend/tests/test_robust_decision_optimization_v2220.py']
for rel in required:
    assert (root/rel).is_file(), rel
for rel in ['backend/decision-runtime/service.py','backend/app/config.py','backend/app/models.py','backend/app/polyglot.py','backend/app/main.py']:
    py_compile.compile(str(root/rel),doraise=True)
for rel in ['schemas/sc-workspace-decision-optimization-result-v1.schema.json','schemas/sc-workspace-decision-optimization-receipt-v1.schema.json','release-manifest-v2.22.0.json']:
    json.load(open(root/rel))
s=(root/'backend/app/main.py').read_text(); assert 'robustDecisionOptimizationRuntime' in s and 'decisionOptimizationReceipts' in s
print('PASS - v2.22.0 robust decision optimization & Pareto contract')
