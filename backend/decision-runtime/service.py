\
import hashlib, json, math, os
from typing import Any
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

VERSION="2.22.0"
RUNTIME="python-robust-decision-pareto"
OPS=(
 "workspace.decision.pareto-front",
 "workspace.decision.expected-utility-rank",
 "workspace.decision.minimax-regret",
 "workspace.decision.constraint-robustness",
 "workspace.decision.stochastic-dominance",
 "workspace.decision.robustness-envelope",
 "workspace.decision.scenario-stress-rank",
 "workspace.decision.value-of-perfect-information",
)
TOKEN=os.getenv("SC_WORKSPACE_DECISION_RUNTIME_TOKEN","").strip()
MAX_CANDIDATES=int(os.getenv("SC_WORKSPACE_DECISION_MAX_CANDIDATES","5000"))
MAX_SCENARIOS=int(os.getenv("SC_WORKSPACE_DECISION_MAX_SCENARIOS","500"))
MAX_METRICS=int(os.getenv("SC_WORKSPACE_DECISION_MAX_METRICS","64"))
app=FastAPI(title="Sustainable Catalyst Workspace Robust Decision Optimization & Pareto Runtime",version=VERSION)

class Envelope(BaseModel):
    operation:str
    payload:dict[str,Any]=Field(default_factory=dict)

def auth(authorization:str|None):
    if TOKEN and authorization != f"Bearer {TOKEN}": raise HTTPException(status_code=401,detail="Unauthorized")

def finite(v,name):
    try: x=float(v)
    except Exception: raise HTTPException(status_code=400,detail=f"{name} must be numeric")
    if not math.isfinite(x): raise HTTPException(status_code=400,detail=f"{name} must be finite")
    return x

def fingerprint(doc): return hashlib.sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def quantile(xs,q):
    ys=sorted(float(x) for x in xs)
    if not ys: raise HTTPException(status_code=400,detail="values must not be empty")
    pos=(len(ys)-1)*q; lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    if lo==hi: return ys[lo]
    return ys[lo]*(hi-pos)+ys[hi]*(pos-lo)

def parse_candidates(p, require_metrics=True):
    rows=p.get("candidates") or []
    if not isinstance(rows,list) or not 1<=len(rows)<=MAX_CANDIDATES: raise HTTPException(status_code=400,detail=f"candidates must contain 1..{MAX_CANDIDATES} items")
    out=[]
    for i,row in enumerate(rows):
        if not isinstance(row,dict): raise HTTPException(status_code=400,detail="each candidate must be an object")
        cid=str(row.get("id") or row.get("name") or f"candidate-{i+1}")[:160]
        metrics=row.get("metrics") if isinstance(row.get("metrics"),dict) else {}
        if require_metrics and not metrics: raise HTTPException(status_code=400,detail="candidate.metrics is required")
        if len(metrics)>MAX_METRICS: raise HTTPException(status_code=400,detail=f"metrics exceed limit {MAX_METRICS}")
        metrics={str(k)[:96]:finite(v,f"metrics.{k}") for k,v in metrics.items()}
        out.append({"id":cid,"metrics":metrics,"raw":row})
    return out

def directions(p, keys):
    raw=p.get("directions") if isinstance(p.get("directions"),dict) else {}
    out={}
    for k in keys:
        d=str(raw.get(k,"maximize")).lower()
        if d not in {"maximize","minimize"}: raise HTTPException(status_code=400,detail=f"direction for {k} must be maximize or minimize")
        out[k]=d
    return out

def weights(p,keys):
    raw=p.get("weights") if isinstance(p.get("weights"),dict) else {}
    vals={k:finite(raw.get(k,1.0),f"weights.{k}") for k in keys}
    if all(abs(v)<1e-15 for v in vals.values()): raise HTTPException(status_code=400,detail="at least one weight must be non-zero")
    scale=sum(abs(v) for v in vals.values())
    return {k:v/scale for k,v in vals.items()}

def scores_matrix(p):
    cand=p.get("candidates") or []
    scenarios=p.get("scenarios") or []
    if not isinstance(cand,list) or not 1<=len(cand)<=MAX_CANDIDATES: raise HTTPException(status_code=400,detail="candidates out of bounds")
    if not isinstance(scenarios,list) or not 1<=len(scenarios)<=MAX_SCENARIOS: raise HTTPException(status_code=400,detail="scenarios out of bounds")
    ids=[]; matrix=[]
    for i,row in enumerate(cand):
        if not isinstance(row,dict): raise HTTPException(status_code=400,detail="candidate must be object")
        ids.append(str(row.get("id") or f"candidate-{i+1}")[:160])
        vals=row.get("scores")
        if not isinstance(vals,list) or len(vals)!=len(scenarios): raise HTTPException(status_code=400,detail="candidate scores must match scenarios")
        matrix.append([finite(x,"score") for x in vals])
    probs=[]
    for s in scenarios:
        if not isinstance(s,dict): raise HTTPException(status_code=400,detail="scenario must be object")
        probs.append(max(0.0,finite(s.get("probability",1.0),"scenario.probability")))
    total=sum(probs)
    if total<=0: raise HTTPException(status_code=400,detail="scenario probabilities must sum above zero")
    probs=[x/total for x in probs]
    return ids,matrix,scenarios,probs

def execute(op,p):
    if op=="workspace.decision.pareto-front":
        rows=parse_candidates(p); keys=sorted({k for r in rows for k in r["metrics"]})
        if not keys: raise HTTPException(status_code=400,detail="metrics required")
        d=directions(p,keys)
        def dominates(a,b):
            weak=True; strict=False
            for k in keys:
                av=a["metrics"].get(k,0.0); bv=b["metrics"].get(k,0.0)
                if d[k]=="maximize": weak &= av>=bv; strict |= av>bv
                else: weak &= av<=bv; strict |= av<bv
            return weak and strict
        front=[]
        for a in rows:
            if not any(dominates(b,a) for b in rows if b is not a): front.append(a["id"])
        return {"kind":"pareto-front","selectedAlternative":front[0] if len(front)==1 else "","paretoFront":front,"candidateCount":len(rows),"scenarioCount":0,"criterion":"non-dominated","summary":{"frontierSize":len(front),"metrics":keys}}
    if op=="workspace.decision.expected-utility-rank":
        rows=parse_candidates(p); keys=sorted({k for r in rows for k in r["metrics"]}); d=directions(p,keys); w=weights(p,keys)
        ranges={}
        for k in keys:
            xs=[r["metrics"].get(k,0.0) for r in rows]; lo=min(xs); hi=max(xs); ranges[k]=(lo,hi)
        ranked=[]
        for r in rows:
            u=0.0
            for k in keys:
                lo,hi=ranges[k]; z=0.5 if hi==lo else (r["metrics"].get(k,0.0)-lo)/(hi-lo)
                if d[k]=="minimize": z=1.0-z
                u += w[k]*z
            ranked.append({"id":r["id"],"utility":u})
        ranked.sort(key=lambda x:x["utility"],reverse=True)
        return {"kind":"expected-utility-rank","selectedAlternative":ranked[0]["id"],"candidateCount":len(rows),"scenarioCount":0,"criterion":"normalized-weighted-utility","summary":{"ranking":ranked,"weights":w}}
    if op=="workspace.decision.minimax-regret":
        ids,matrix,scenarios,probs=scores_matrix(p); direction=str(p.get("direction") or "maximize").lower()
        if direction not in {"maximize","minimize"}: raise HTTPException(status_code=400,detail="direction invalid")
        regrets=[]
        for i,cid in enumerate(ids):
            rs=[]
            for j in range(len(scenarios)):
                vals=[matrix[k][j] for k in range(len(ids))]; best=max(vals) if direction=="maximize" else min(vals)
                rs.append((best-matrix[i][j]) if direction=="maximize" else (matrix[i][j]-best))
            regrets.append({"id":cid,"maxRegret":max(rs),"expectedRegret":sum(rs[j]*probs[j] for j in range(len(rs)))})
        regrets.sort(key=lambda x:(x["maxRegret"],x["expectedRegret"]))
        return {"kind":"minimax-regret","selectedAlternative":regrets[0]["id"],"candidateCount":len(ids),"scenarioCount":len(scenarios),"criterion":"minimax-regret","summary":{"ranking":regrets}}
    if op=="workspace.decision.constraint-robustness":
        rows=parse_candidates(p,False); constraints=p.get("constraints") or []
        if not isinstance(constraints,list) or not 1<=len(constraints)<=MAX_METRICS: raise HTTPException(status_code=400,detail="constraints required")
        ranking=[]
        for r in rows:
            scenarios=r["raw"].get("scenarios") or []
            if not isinstance(scenarios,list) or not 1<=len(scenarios)<=MAX_SCENARIOS: raise HTTPException(status_code=400,detail="candidate.scenarios required")
            passed=0; margins=[]
            for sc in scenarios:
                ok=True; local=[]
                for c in constraints:
                    metric=str(c.get("metric")); sense=str(c.get("sense") or "<="); limit=finite(c.get("limit"),"constraint.limit"); val=finite((sc.get("metrics") or {}).get(metric),metric)
                    margin=(limit-val) if sense=="<=" else (val-limit)
                    if sense not in {"<=",">="}: raise HTTPException(status_code=400,detail="constraint sense invalid")
                    ok &= margin>=0; local.append(margin)
                passed += 1 if ok else 0; margins.append(min(local))
            ranking.append({"id":r["id"],"feasibilityRate":passed/len(scenarios),"worstMargin":min(margins)})
        ranking.sort(key=lambda x:(x["feasibilityRate"],x["worstMargin"]),reverse=True)
        return {"kind":"constraint-robustness","selectedAlternative":ranking[0]["id"],"candidateCount":len(rows),"scenarioCount":max(len(r["raw"].get("scenarios") or []) for r in rows),"criterion":"robust-feasibility","summary":{"ranking":ranking}}
    if op=="workspace.decision.stochastic-dominance":
        rows=p.get("candidates") or []
        if not isinstance(rows,list) or not 2<=len(rows)<=100: raise HTTPException(status_code=400,detail="2..100 candidates required")
        parsed=[]
        for i,r in enumerate(rows):
            vals=r.get("values") if isinstance(r,dict) else None
            if not isinstance(vals,list) or not 2<=len(vals)<=10000: raise HTTPException(status_code=400,detail="candidate values required")
            parsed.append((str(r.get("id") or f"candidate-{i+1}"),sorted(finite(x,"value") for x in vals)))
        dominated=set(); pairs=[]
        for i,(aid,a) in enumerate(parsed):
            for j,(bid,b) in enumerate(parsed):
                if i==j or len(a)!=len(b): continue
                # Quantile-wise first-order dominance for equal-sized empirical samples.
                if all(a[k]>=b[k] for k in range(len(a))) and any(a[k]>b[k] for k in range(len(a))):
                    dominated.add(bid); pairs.append({"dominant":aid,"dominated":bid})
        front=[cid for cid,_ in parsed if cid not in dominated]
        return {"kind":"stochastic-dominance","selectedAlternative":front[0] if len(front)==1 else "","candidateCount":len(parsed),"scenarioCount":len(parsed[0][1]),"criterion":"empirical-first-order-dominance","summary":{"nonDominated":front,"dominancePairs":pairs}}
    if op=="workspace.decision.robustness-envelope":
        ids,matrix,scenarios,probs=scores_matrix(p); ranking=[]
        for i,cid in enumerate(ids):
            xs=matrix[i]; ranking.append({"id":cid,"mean":sum(xs[j]*probs[j] for j in range(len(xs))),"worst":min(xs),"best":max(xs),"p10":quantile(xs,0.1),"p50":quantile(xs,0.5),"p90":quantile(xs,0.9)})
        ranking.sort(key=lambda x:(x["p10"],x["mean"]),reverse=True)
        return {"kind":"robustness-envelope","selectedAlternative":ranking[0]["id"],"candidateCount":len(ids),"scenarioCount":len(scenarios),"criterion":"p10-then-mean","summary":{"ranking":ranking}}
    if op=="workspace.decision.scenario-stress-rank":
        ids,matrix,scenarios,probs=scores_matrix(p); stress=[max(0.0,finite(s.get("stressWeight",1.0),"stressWeight")) for s in scenarios]; sw=sum(stress)
        if sw<=0: raise HTTPException(status_code=400,detail="stress weights must sum above zero")
        stress=[x/sw for x in stress]; ranking=[]
        for i,cid in enumerate(ids): ranking.append({"id":cid,"stressScore":sum(matrix[i][j]*stress[j] for j in range(len(stress)))})
        ranking.sort(key=lambda x:x["stressScore"],reverse=True)
        return {"kind":"scenario-stress-rank","selectedAlternative":ranking[0]["id"],"candidateCount":len(ids),"scenarioCount":len(scenarios),"criterion":"stress-weighted-score","summary":{"ranking":ranking}}
    if op=="workspace.decision.value-of-perfect-information":
        ids,matrix,scenarios,probs=scores_matrix(p); direction=str(p.get("direction") or "maximize").lower()
        expected=[sum(matrix[i][j]*probs[j] for j in range(len(probs))) for i in range(len(ids))]
        base=max(expected) if direction=="maximize" else min(expected); base_i=expected.index(base)
        perfect=0.0
        for j in range(len(scenarios)):
            vals=[matrix[i][j] for i in range(len(ids))]; perfect += (max(vals) if direction=="maximize" else min(vals))*probs[j]
        evpi=(perfect-base) if direction=="maximize" else (base-perfect)
        return {"kind":"value-of-perfect-information","selectedAlternative":ids[base_i],"candidateCount":len(ids),"scenarioCount":len(scenarios),"criterion":"expected-value","summary":{"bestExpectedValue":base,"perfectInformationValue":perfect,"evpi":max(0.0,evpi),"expectedValues":dict(zip(ids,expected))}}
    raise HTTPException(status_code=400,detail="Unregistered decision operation")

@app.get('/health')
def health():
    return {"ok":True,"service":"Sustainable Catalyst Workspace Robust Decision Optimization & Pareto Runtime","version":VERSION,"runtime":RUNTIME,"operations":list(OPS),"boundedOperationsOnly":True,"arbitraryCodeExecution":False,"maxCandidates":MAX_CANDIDATES,"maxScenarios":MAX_SCENARIOS,"maxMetrics":MAX_METRICS}

@app.post('/v1/execute')
def run(e:Envelope, authorization:str|None=Header(default=None)):
    auth(authorization)
    if e.operation not in OPS: raise HTTPException(status_code=400,detail="Unregistered decision operation")
    r=execute(e.operation,e.payload)
    return {"schema":"sc-workspace-decision-optimization-result/1.0","runtime":RUNTIME,"operation":e.operation,"inputFingerprint":fingerprint(e.payload),"result":r}
