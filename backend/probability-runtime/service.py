import hashlib, json, math, os, random
from statistics import NormalDist
from typing import Any
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

VERSION="2.19.0"
RUNTIME="python-probabilistic-bayesian"
OPS=(
 "workspace.probability.normal-summary",
 "workspace.probability.beta-binomial-update",
 "workspace.probability.normal-normal-update",
 "workspace.probability.gamma-poisson-update",
 "workspace.probability.posterior-predictive-binomial",
 "workspace.probability.uncertainty-propagate",
)
MAX_DRAWS=int(os.getenv("SC_WORKSPACE_PROBABILITY_MAX_DRAWS","20000"))
TOKEN=os.getenv("SC_WORKSPACE_PROBABILITY_RUNTIME_TOKEN","").strip()
app=FastAPI(title="Sustainable Catalyst Workspace Probabilistic & Bayesian Runtime",version=VERSION)

class Envelope(BaseModel):
    operation:str
    payload:dict[str,Any]=Field(default_factory=dict)

def auth(authorization:str|None):
    if TOKEN and authorization != f"Bearer {TOKEN}": raise HTTPException(status_code=401,detail="Unauthorized")

def finite(x,name):
    try: v=float(x)
    except Exception: raise HTTPException(status_code=400,detail=f"{name} must be numeric")
    if not math.isfinite(v): raise HTTPException(status_code=400,detail=f"{name} must be finite")
    return v

def pos(x,name):
    v=finite(x,name)
    if v<=0: raise HTTPException(status_code=400,detail=f"{name} must be > 0")
    return v

def nonneg_int(x,name):
    try: v=int(x)
    except Exception: raise HTTPException(status_code=400,detail=f"{name} must be an integer")
    if v<0: raise HTTPException(status_code=400,detail=f"{name} must be >= 0")
    return v

def q(sorted_vals,p):
    if not sorted_vals:return None
    i=(len(sorted_vals)-1)*p; lo=int(math.floor(i)); hi=int(math.ceil(i))
    if lo==hi:return float(sorted_vals[lo])
    return float(sorted_vals[lo]*(hi-i)+sorted_vals[hi]*(i-lo))

def interval(samples,level):
    s=sorted(float(x) for x in samples); a=(1-level)/2
    return {"level":level,"lower":q(s,a),"upper":q(s,1-a)}

def fingerprint(doc): return hashlib.sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def execute(op,p):
    level=finite(p.get("credibleLevel",0.95),"credibleLevel")
    if not 0.5 < level < 0.9999: raise HTTPException(status_code=400,detail="credibleLevel must be between 0.5 and 0.9999")
    seed=int(p.get("seed",202619))
    draws=min(MAX_DRAWS,max(500,int(p.get("draws",5000))))
    rng=random.Random(seed)
    if op=="workspace.probability.normal-summary":
        mu=finite(p.get("mean",0),"mean"); sd=pos(p.get("sd",1),"sd"); z=NormalDist().inv_cdf((1+level)/2)
        return {"kind":"normal","parameters":{"mean":mu,"sd":sd},"mean":mu,"variance":sd*sd,"credibleInterval":{"level":level,"lower":mu-z*sd,"upper":mu+z*sd}}
    if op=="workspace.probability.beta-binomial-update":
        a=pos(p.get("alpha",1),"alpha"); b=pos(p.get("beta",1),"beta"); y=nonneg_int(p.get("successes",0),"successes"); n=nonneg_int(p.get("trials",0),"trials")
        if y>n: raise HTTPException(status_code=400,detail="successes cannot exceed trials")
        ap=a+y; bp=b+n-y; samples=[rng.betavariate(ap,bp) for _ in range(draws)]
        return {"kind":"beta-binomial","prior":{"alpha":a,"beta":b},"data":{"successes":y,"trials":n},"posterior":{"alpha":ap,"beta":bp,"mean":ap/(ap+bp),"credibleInterval":interval(samples,level)},"draws":draws,"seed":seed}
    if op=="workspace.probability.normal-normal-update":
        pm=finite(p.get("priorMean",0),"priorMean"); psd=pos(p.get("priorSd",1),"priorSd"); sigma=pos(p.get("knownSd",1),"knownSd"); xs=p.get("observations") or []
        if not isinstance(xs,list) or not xs or len(xs)>50000: raise HTTPException(status_code=400,detail="observations must be a non-empty bounded array")
        vals=[finite(x,"observation") for x in xs]; n=len(vals); xbar=sum(vals)/n
        pv=psd*psd; sv=sigma*sigma; postv=1/(1/pv+n/sv); postm=postv*(pm/pv+n*xbar/sv); postsd=math.sqrt(postv); z=NormalDist().inv_cdf((1+level)/2)
        return {"kind":"normal-normal","prior":{"mean":pm,"sd":psd},"data":{"n":n,"mean":xbar,"knownSd":sigma},"posterior":{"mean":postm,"sd":postsd,"credibleInterval":{"level":level,"lower":postm-z*postsd,"upper":postm+z*postsd}}}
    if op=="workspace.probability.gamma-poisson-update":
        shape=pos(p.get("shape",1),"shape"); rate=pos(p.get("rate",1),"rate"); counts=p.get("counts") or []
        if not isinstance(counts,list) or not counts or len(counts)>50000: raise HTTPException(status_code=400,detail="counts must be a non-empty bounded array")
        vals=[nonneg_int(x,"count") for x in counts]; sh=shape+sum(vals); rt=rate+len(vals); samples=[rng.gammavariate(sh,1/rt) for _ in range(draws)]
        return {"kind":"gamma-poisson","prior":{"shape":shape,"rate":rate},"data":{"n":len(vals),"sum":sum(vals)},"posterior":{"shape":sh,"rate":rt,"mean":sh/rt,"credibleInterval":interval(samples,level)},"draws":draws,"seed":seed}
    if op=="workspace.probability.posterior-predictive-binomial":
        a=pos(p.get("alpha",1),"alpha"); b=pos(p.get("beta",1),"beta"); trials=nonneg_int(p.get("futureTrials",1),"futureTrials")
        if trials>100000: raise HTTPException(status_code=400,detail="futureTrials exceeds bound")
        sims=[]
        for _ in range(draws):
            theta=rng.betavariate(a,b); sims.append(sum(1 for _ in range(trials) if rng.random()<theta))
        return {"kind":"beta-binomial-posterior-predictive","futureTrials":trials,"predictiveMean":sum(sims)/draws,"predictiveInterval":interval(sims,level),"draws":draws,"seed":seed}
    if op=="workspace.probability.uncertainty-propagate":
        terms=p.get("terms") or []
        if not isinstance(terms,list) or not terms or len(terms)>64: raise HTTPException(status_code=400,detail="terms must contain 1..64 normal terms")
        clean=[]
        for t in terms:
            if not isinstance(t,dict): raise HTTPException(status_code=400,detail="each term must be an object")
            clean.append((finite(t.get("coefficient",1),"coefficient"),finite(t.get("mean",0),"mean"),pos(t.get("sd",1),"sd")))
        offset=finite(p.get("offset",0),"offset"); sims=[]
        for _ in range(draws): sims.append(offset+sum(c*rng.gauss(m,s) for c,m,s in clean))
        mean=sum(sims)/draws; var=sum((x-mean)**2 for x in sims)/(draws-1)
        return {"kind":"linear-normal-uncertainty-propagation","mean":mean,"sd":math.sqrt(var),"credibleInterval":interval(sims,level),"draws":draws,"seed":seed,"termCount":len(clean)}
    raise HTTPException(status_code=400,detail="Unregistered probabilistic operation")

@app.get('/health')
def health(): return {"ok":True,"service":"Sustainable Catalyst Workspace Probabilistic & Bayesian Runtime","version":VERSION,"runtime":RUNTIME,"operations":list(OPS),"boundedOperationsOnly":True,"arbitraryCodeExecution":False,"maxDraws":MAX_DRAWS}

@app.post('/v1/execute')
def run(e:Envelope,authorization:str|None=Header(default=None)):
    auth(authorization)
    if e.operation not in OPS: raise HTTPException(status_code=400,detail="Operation is not registered")
    result=execute(e.operation,e.payload)
    return {"schema":"sc-workspace-probabilistic-result/1.0","runtime":RUNTIME,"operation":e.operation,"inputFingerprint":fingerprint(e.payload),"result":result}
