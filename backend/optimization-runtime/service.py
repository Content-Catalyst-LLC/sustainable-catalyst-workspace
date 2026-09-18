\
import hashlib, itertools, json, math, os, random
from typing import Any
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

VERSION="2.21.0"
RUNTIME="python-optimization-parameter-search"
OPS=(
 "workspace.optimize.quadratic-box",
 "workspace.optimize.linear-box",
 "workspace.optimize.grid-search",
 "workspace.optimize.random-search",
 "workspace.optimize.coordinate-descent",
 "workspace.optimize.pareto-weighted-sum",
 "workspace.optimize.robust-scenario-rank",
 "workspace.optimize.parameter-sweep-rank",
)
TOKEN=os.getenv("SC_WORKSPACE_OPTIMIZATION_RUNTIME_TOKEN","").strip()
MAX_DIM=int(os.getenv("SC_WORKSPACE_OPTIMIZATION_MAX_DIMENSIONS","32"))
MAX_EVALS=int(os.getenv("SC_WORKSPACE_OPTIMIZATION_MAX_EVALUATIONS","50000"))
MAX_ITERS=int(os.getenv("SC_WORKSPACE_OPTIMIZATION_MAX_ITERATIONS","5000"))
app=FastAPI(title="Sustainable Catalyst Workspace Optimization & Parameter Search Runtime",version=VERSION)

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

def integer(v,name,lo,hi):
    try: x=int(v)
    except Exception: raise HTTPException(status_code=400,detail=f"{name} must be an integer")
    if x<lo or x>hi: raise HTTPException(status_code=400,detail=f"{name} must be between {lo} and {hi}")
    return x

def fingerprint(doc):
    return hashlib.sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def parse_bounds(p):
    raw=p.get("bounds") or []
    if not isinstance(raw,list) or not 1<=len(raw)<=MAX_DIM: raise HTTPException(status_code=400,detail=f"bounds must contain 1..{MAX_DIM} items")
    out=[]
    for i,b in enumerate(raw):
        if not isinstance(b,dict): raise HTTPException(status_code=400,detail="each bound must be an object")
        name=str(b.get("name") or f"x{i+1}")[:96]; lo=finite(b.get("min"),f"bounds[{i}].min"); hi=finite(b.get("max"),f"bounds[{i}].max")
        if not lo < hi: raise HTTPException(status_code=400,detail="each bound requires min < max")
        out.append((name,lo,hi))
    return out

def parse_direction(p):
    d=str(p.get("direction") or "minimize").lower()
    if d not in {"minimize","maximize"}: raise HTTPException(status_code=400,detail="direction must be minimize or maximize")
    return d

def better(v,best,direction): return best is None or (v<best if direction=="minimize" else v>best)

def vector_to_params(bounds,x): return {bounds[i][0]:float(x[i]) for i in range(len(bounds))}

def objective(spec,x):
    if not isinstance(spec,dict): raise HTTPException(status_code=400,detail="objective must be an object")
    kind=str(spec.get("kind") or "linear").lower()
    n=len(x); intercept=finite(spec.get("intercept",0),"objective.intercept")
    if kind=="linear":
        c=spec.get("coefficients") or []
        if not isinstance(c,list) or len(c)!=n: raise HTTPException(status_code=400,detail="linear objective coefficients must match bounds")
        return intercept+sum(finite(c[i],f"coefficient[{i}]")*x[i] for i in range(n))
    if kind=="quadratic":
        c=spec.get("linear") or [0.0]*n; q=spec.get("quadratic") or []
        if not isinstance(c,list) or len(c)!=n: raise HTTPException(status_code=400,detail="quadratic linear vector must match bounds")
        if not isinstance(q,list) or len(q)!=n or any(not isinstance(r,list) or len(r)!=n for r in q): raise HTTPException(status_code=400,detail="quadratic matrix must be square and match bounds")
        val=intercept+sum(finite(c[i],f"linear[{i}]")*x[i] for i in range(n))
        for i in range(n):
            for j in range(n): val += 0.5*finite(q[i][j],f"quadratic[{i}][{j}]")*x[i]*x[j]
        return val
    raise HTTPException(status_code=400,detail="objective kind must be linear or quadratic")

def evaluate_points(bounds,pts,spec,direction):
    best_v=None; best_x=None
    for x in pts:
        v=objective(spec,x)
        if better(v,best_v,direction): best_v=v; best_x=list(x)
    return best_v,best_x

def result(kind,bounds,direction,best_v,best_x,evals,iterations=0,seed=0,converged=True,extra=None):
    d={"kind":kind,"direction":direction,"bestValue":float(best_v),"bestParameters":vector_to_params(bounds,best_x),"evaluationCount":int(evals),"iterations":int(iterations),"seed":int(seed),"converged":bool(converged)}
    if extra: d.update(extra)
    return d

def execute(op,p):
    bounds=parse_bounds(p); direction=parse_direction(p); spec=p.get("objective") or {"kind":"linear","coefficients":[1.0]*len(bounds)}
    n=len(bounds)
    if op=="workspace.optimize.linear-box":
        if str(spec.get("kind") or "linear").lower()!="linear": raise HTTPException(status_code=400,detail="linear-box requires a linear objective")
        c=spec.get("coefficients") or []
        if len(c)!=n: raise HTTPException(status_code=400,detail="coefficients must match bounds")
        x=[]
        for i,(_name,lo,hi) in enumerate(bounds):
            ci=finite(c[i],f"coefficient[{i}]"); x.append(lo if (direction=="minimize")==(ci>=0) else hi)
        return result("linear-box",bounds,direction,objective(spec,x),x,1)
    if op=="workspace.optimize.quadratic-box":
        if str(spec.get("kind") or "").lower()!="quadratic": raise HTTPException(status_code=400,detail="quadratic-box requires a quadratic objective")
        iters=integer(p.get("iterations",1000),"iterations",1,MAX_ITERS); lr=finite(p.get("learningRate",0.03),"learningRate")
        if lr<=0 or lr>2: raise HTTPException(status_code=400,detail="learningRate must be > 0 and <= 2")
        x=[finite((p.get("initial") or {}).get(name,(lo+hi)/2),f"initial.{name}") for name,lo,hi in bounds]
        for i,(_name,lo,hi) in enumerate(bounds): x[i]=min(max(x[i],lo),hi)
        q=spec.get("quadratic"); c=spec.get("linear") or [0.0]*n
        evals=1
        for k in range(iters):
            grad=[]
            for i in range(n): grad.append(finite(c[i],f"linear[{i}]")+sum(finite(q[i][j],f"quadratic[{i}][{j}]")*x[j] for j in range(n)))
            sign=1.0 if direction=="minimize" else -1.0
            nx=[min(max(x[i]-sign*lr*grad[i],bounds[i][1]),bounds[i][2]) for i in range(n)]
            evals+=1
            if max(abs(nx[i]-x[i]) for i in range(n))<1e-9: x=nx; return result("quadratic-box",bounds,direction,objective(spec,x),x,evals,k+1,converged=True)
            x=nx
        return result("quadratic-box",bounds,direction,objective(spec,x),x,evals,iters,converged=False)
    if op=="workspace.optimize.grid-search":
        if n>6: raise HTTPException(status_code=400,detail="grid-search supports at most 6 dimensions")
        ppd=integer(p.get("pointsPerDimension",9),"pointsPerDimension",2,41); total=ppd**n
        if total>MAX_EVALS: raise HTTPException(status_code=400,detail=f"grid would require {total} evaluations; limit is {MAX_EVALS}")
        axes=[[lo+(hi-lo)*i/(ppd-1) for i in range(ppd)] for _name,lo,hi in bounds]
        best_v,best_x=evaluate_points(bounds,itertools.product(*axes),spec,direction)
        return result("grid-search",bounds,direction,best_v,best_x,total,extra={"pointsPerDimension":ppd})
    if op=="workspace.optimize.random-search":
        samples=integer(p.get("samples",5000),"samples",10,MAX_EVALS); seed=int(p.get("seed",2210)); rng=random.Random(seed)
        pts=([rng.uniform(lo,hi) for _name,lo,hi in bounds] for _ in range(samples))
        best_v,best_x=evaluate_points(bounds,pts,spec,direction)
        return result("random-search",bounds,direction,best_v,best_x,samples,seed=seed)
    if op=="workspace.optimize.coordinate-descent":
        iters=integer(p.get("iterations",200),"iterations",1,MAX_ITERS); steps=integer(p.get("stepsPerCoordinate",9),"stepsPerCoordinate",3,41)
        x=[(lo+hi)/2 for _name,lo,hi in bounds]; best_v=objective(spec,x); evals=1
        for k in range(iters):
            changed=False
            for i,(_name,lo,hi) in enumerate(bounds):
                local_best=best_v; local_x=x[i]
                for j in range(steps):
                    cand=lo+(hi-lo)*j/(steps-1); xx=list(x); xx[i]=cand; v=objective(spec,xx); evals+=1
                    if better(v,local_best,direction): local_best=v; local_x=cand
                if local_x!=x[i]: x[i]=local_x; best_v=local_best; changed=True
            if not changed: return result("coordinate-descent",bounds,direction,best_v,x,evals,k+1,converged=True)
        return result("coordinate-descent",bounds,direction,best_v,x,evals,iters,converged=False)
    if op=="workspace.optimize.parameter-sweep-rank":
        candidates=p.get("candidates") or []
        if not isinstance(candidates,list) or not 1<=len(candidates)<=MAX_EVALS: raise HTTPException(status_code=400,detail=f"candidates must contain 1..{MAX_EVALS} items")
        ranked=[]
        for row in candidates:
            if not isinstance(row,dict): raise HTTPException(status_code=400,detail="each candidate must be an object")
            x=[finite(row.get(name),name) for name,_lo,_hi in bounds]
            for i,(_name,lo,hi) in enumerate(bounds):
                if not lo<=x[i]<=hi: raise HTTPException(status_code=400,detail="candidate is outside bounds")
            ranked.append((objective(spec,x),x))
        ranked.sort(key=lambda a:a[0],reverse=direction=="maximize")
        best_v,best_x=ranked[0]
        top=[{"value":float(v),"parameters":vector_to_params(bounds,x)} for v,x in ranked[:min(20,len(ranked))]]
        return result("parameter-sweep-rank",bounds,direction,best_v,best_x,len(ranked),extra={"ranked":top})
    if op=="workspace.optimize.pareto-weighted-sum":
        objectives=p.get("objectives") or []
        weights=p.get("weights") or []
        if not isinstance(objectives,list) or not 2<=len(objectives)<=8 or not isinstance(weights,list) or len(weights)!=len(objectives): raise HTTPException(status_code=400,detail="objectives and weights must contain 2..8 aligned items")
        ww=[finite(w,"weight") for w in weights]
        if sum(abs(w) for w in ww)<=0: raise HTTPException(status_code=400,detail="at least one weight must be non-zero")
        samples=integer(p.get("samples",5000),"samples",10,MAX_EVALS); seed=int(p.get("seed",2210)); rng=random.Random(seed)
        def combo(x): return sum(ww[i]*objective(objectives[i],x) for i in range(len(objectives)))
        best_v=None; best_x=None
        for _ in range(samples):
            x=[rng.uniform(lo,hi) for _name,lo,hi in bounds]; v=combo(x)
            if better(v,best_v,direction): best_v=v; best_x=x
        vals=[objective(o,best_x) for o in objectives]
        return result("pareto-weighted-sum",bounds,direction,best_v,best_x,samples,seed=seed,extra={"objectiveValues":vals,"weights":ww})
    if op=="workspace.optimize.robust-scenario-rank":
        candidates=p.get("candidates") or []; scenarios=p.get("scenarios") or []
        if not isinstance(candidates,list) or not 1<=len(candidates)<=5000: raise HTTPException(status_code=400,detail="candidates must contain 1..5000 items")
        if not isinstance(scenarios,list) or not 1<=len(scenarios)<=100: raise HTTPException(status_code=400,detail="scenarios must contain 1..100 items")
        criterion=str(p.get("criterion") or "worst-case").lower()
        if criterion not in {"worst-case","mean"}: raise HTTPException(status_code=400,detail="criterion must be worst-case or mean")
        best_v=None; best_x=None; evals=0
        for row in candidates:
            x=[finite(row.get(name),name) for name,_lo,_hi in bounds]
            scores=[]
            for s in scenarios:
                if not isinstance(s,dict): raise HTTPException(status_code=400,detail="scenario must be an object")
                delta=s.get("linearDelta") or [0.0]*n
                if not isinstance(delta,list) or len(delta)!=n: raise HTTPException(status_code=400,detail="scenario linearDelta must match bounds")
                scores.append(objective(spec,x)+sum(finite(delta[i],f"linearDelta[{i}]")*x[i] for i in range(n))); evals+=1
            v=(max(scores) if direction=="minimize" else min(scores)) if criterion=="worst-case" else sum(scores)/len(scores)
            if better(v,best_v,direction): best_v=v; best_x=x
        return result("robust-scenario-rank",bounds,direction,best_v,best_x,evals,extra={"criterion":criterion,"scenarioCount":len(scenarios)})
    raise HTTPException(status_code=400,detail="Unregistered optimization operation")

@app.get('/health')
def health():
    return {"ok":True,"service":"Sustainable Catalyst Workspace Optimization & Parameter Search Runtime","version":VERSION,"runtime":RUNTIME,"operations":list(OPS),"boundedOperationsOnly":True,"arbitraryCodeExecution":False,"maxDimensions":MAX_DIM,"maxEvaluations":MAX_EVALS,"maxIterations":MAX_ITERS}

@app.post('/v1/execute')
def run(e:Envelope, authorization:str|None=Header(default=None)):
    auth(authorization)
    if e.operation not in OPS: raise HTTPException(status_code=400,detail="Unregistered optimization operation")
    r=execute(e.operation,e.payload)
    return {"schema":"sc-workspace-optimization-result/1.0","runtime":RUNTIME,"operation":e.operation,"inputFingerprint":fingerprint(e.payload),"result":r}
