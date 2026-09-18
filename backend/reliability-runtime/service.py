\
import hashlib, json, math, os
from typing import Any
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

VERSION="2.23.0"
RUNTIME="python-reliability-survival"
OPS=(
 "workspace.reliability.kaplan-meier",
 "workspace.reliability.exponential-fit",
 "workspace.reliability.weibull-fit",
 "workspace.reliability.reliability-at-time",
 "workspace.reliability.series-parallel-system",
 "workspace.reliability.repairable-availability",
 "workspace.reliability.binomial-reliability",
 "workspace.reliability.inverse-power-life",
)
TOKEN=os.getenv("SC_WORKSPACE_RELIABILITY_RUNTIME_TOKEN","").strip()
MAX_SAMPLES=int(os.getenv("SC_WORKSPACE_RELIABILITY_MAX_SAMPLES","20000"))
MAX_COMPONENTS=int(os.getenv("SC_WORKSPACE_RELIABILITY_MAX_COMPONENTS","1000"))
MAX_GROUPS=int(os.getenv("SC_WORKSPACE_RELIABILITY_MAX_GROUPS","256"))
app=FastAPI(title="Sustainable Catalyst Workspace Reliability, Survival & Failure-Time Runtime",version=VERSION)

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

def positive(v,name,allow_zero=False):
    x=finite(v,name)
    if x < 0 or (x == 0 and not allow_zero): raise HTTPException(status_code=400,detail=f"{name} must be {'non-negative' if allow_zero else 'positive'}")
    return x

def fingerprint(doc): return hashlib.sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def linear_fit(xs,ys):
    n=len(xs)
    if n<2: raise HTTPException(status_code=400,detail="at least two observations are required")
    mx=sum(xs)/n; my=sum(ys)/n
    den=sum((x-mx)**2 for x in xs)
    if den<=0: raise HTTPException(status_code=400,detail="predictor has zero variance")
    slope=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den
    intercept=my-slope*mx
    fitted=[intercept+slope*x for x in xs]
    ssr=sum((y-f)**2 for y,f in zip(ys,fitted)); sst=sum((y-my)**2 for y in ys)
    r2=1.0-ssr/sst if sst>0 else 1.0
    return intercept,slope,r2

def parse_survival(p):
    times=p.get("times") or []; events=p.get("events")
    if not isinstance(times,list) or not 1<=len(times)<=MAX_SAMPLES: raise HTTPException(status_code=400,detail=f"times must contain 1..{MAX_SAMPLES} observations")
    ts=[positive(x,"time") for x in times]
    if events is None: es=[1]*len(ts)
    else:
        if not isinstance(events,list) or len(events)!=len(ts): raise HTTPException(status_code=400,detail="events must match times")
        es=[]
        for e in events:
            if e in (1,True): es.append(1)
            elif e in (0,False): es.append(0)
            else: raise HTTPException(status_code=400,detail="events must contain only 0/1 values")
    return ts,es

def km(ts,es):
    unique=sorted(set(ts)); survival=1.0; table=[]; n=len(ts)
    for t in unique:
        at_risk=sum(1 for x in ts if x>=t)
        deaths=sum(1 for x,e in zip(ts,es) if x==t and e==1)
        censored=sum(1 for x,e in zip(ts,es) if x==t and e==0)
        if deaths and at_risk: survival *= (1.0-deaths/at_risk)
        table.append({"time":t,"atRisk":at_risk,"events":deaths,"censored":censored,"survival":survival,"failureProbability":1.0-survival})
    return table

def execute(op,p):
    if op=="workspace.reliability.kaplan-meier":
        ts,es=parse_survival(p); table=km(ts,es); med=None
        for row in table:
            if row["survival"]<=0.5: med=row["time"]; break
        return {"kind":"kaplan-meier","modelKind":"nonparametric","sampleCount":len(ts),"eventCount":sum(es),"horizon":max(ts),"metrics":{"medianSurvival":med,"survivalAtHorizon":table[-1]["survival"]},"survivalTable":table}
    if op=="workspace.reliability.exponential-fit":
        ts,es=parse_survival(p); d=sum(es); exposure=sum(ts)
        if d<=0 or exposure<=0: raise HTTPException(status_code=400,detail="at least one observed failure is required")
        rate=d/exposure; mean_life=1.0/rate
        horizon=positive(p.get("horizon",mean_life),"horizon",allow_zero=True)
        rel=math.exp(-rate*horizon)
        return {"kind":"exponential-fit","modelKind":"exponential","sampleCount":len(ts),"eventCount":d,"horizon":horizon,"metrics":{"failureRate":rate,"meanLife":mean_life,"reliabilityAtHorizon":rel,"failureProbabilityAtHorizon":1-rel}}
    if op=="workspace.reliability.weibull-fit":
        ts,es=parse_survival(p)
        failures=sorted(t for t,e in zip(ts,es) if e==1)
        if len(failures)<3: raise HTTPException(status_code=400,detail="Weibull fit requires at least three observed failures")
        n=len(failures); xs=[]; ys=[]
        for i,t in enumerate(failures,1):
            F=(i-0.3)/(n+0.4); xs.append(math.log(t)); ys.append(math.log(-math.log(1-F)))
        intercept,shape,r2=linear_fit(xs,ys)
        if shape<=0: raise HTTPException(status_code=400,detail="estimated Weibull shape must be positive")
        scale=math.exp(-intercept/shape)
        horizon=positive(p.get("horizon",scale),"horizon",allow_zero=True)
        rel=math.exp(-((horizon/scale)**shape)) if horizon>0 else 1.0
        return {"kind":"weibull-fit","modelKind":"weibull","sampleCount":len(ts),"eventCount":sum(es),"horizon":horizon,"metrics":{"shape":shape,"scale":scale,"plotR2":r2,"reliabilityAtHorizon":rel,"failureProbabilityAtHorizon":1-rel}}
    if op=="workspace.reliability.reliability-at-time":
        model=str(p.get("model") or "exponential").lower(); t=positive(p.get("time",0),"time",allow_zero=True)
        if model=="exponential":
            rate=positive(p.get("failureRate"),"failureRate"); r=math.exp(-rate*t); metrics={"failureRate":rate}
        elif model=="weibull":
            shape=positive(p.get("shape"),"shape"); scale=positive(p.get("scale"),"scale"); r=math.exp(-((t/scale)**shape)) if t else 1.0; metrics={"shape":shape,"scale":scale}
        else: raise HTTPException(status_code=400,detail="model must be exponential or weibull")
        metrics.update({"reliability":r,"failureProbability":1-r})
        return {"kind":"reliability-at-time","modelKind":model,"sampleCount":0,"eventCount":0,"horizon":t,"metrics":metrics}
    if op=="workspace.reliability.series-parallel-system":
        groups=p.get("groups") or []
        if not isinstance(groups,list) or not 1<=len(groups)<=MAX_GROUPS: raise HTTPException(status_code=400,detail=f"groups must contain 1..{MAX_GROUPS} items")
        group_rs=[]; count=0
        for g in groups:
            if not isinstance(g,dict): raise HTTPException(status_code=400,detail="group must be object")
            kind=str(g.get("kind") or "series").lower(); vals=g.get("reliabilities") or []
            if not isinstance(vals,list) or not vals: raise HTTPException(status_code=400,detail="group reliabilities required")
            if count+len(vals)>MAX_COMPONENTS: raise HTTPException(status_code=400,detail=f"components exceed limit {MAX_COMPONENTS}")
            rs=[finite(x,"reliability") for x in vals]
            if any(x<0 or x>1 for x in rs): raise HTTPException(status_code=400,detail="reliabilities must be between 0 and 1")
            count+=len(rs)
            if kind=="series": gr=math.prod(rs)
            elif kind=="parallel": gr=1.0-math.prod(1.0-x for x in rs)
            else: raise HTTPException(status_code=400,detail="group kind must be series or parallel")
            group_rs.append(gr)
        system_kind=str(p.get("systemKind") or "series").lower()
        if system_kind=="series": sr=math.prod(group_rs)
        elif system_kind=="parallel": sr=1.0-math.prod(1.0-x for x in group_rs)
        else: raise HTTPException(status_code=400,detail="systemKind must be series or parallel")
        return {"kind":"series-parallel-system","modelKind":"reliability-block","sampleCount":count,"eventCount":0,"horizon":0,"metrics":{"systemReliability":sr,"systemFailureProbability":1-sr,"groupReliabilities":group_rs}}
    if op=="workspace.reliability.repairable-availability":
        mtbf=positive(p.get("mtbf"),"mtbf"); mttr=positive(p.get("mttr"),"mttr",allow_zero=True)
        availability=mtbf/(mtbf+mttr); rate=1.0/mtbf; repair=(1.0/mttr if mttr>0 else None)
        return {"kind":"repairable-availability","modelKind":"steady-state-repairable","sampleCount":0,"eventCount":0,"horizon":0,"metrics":{"mtbf":mtbf,"mttr":mttr,"availability":availability,"unavailability":1-availability,"failureRate":rate,"repairRate":repair}}
    if op=="workspace.reliability.binomial-reliability":
        successes=int(p.get("successes",0)); trials=int(p.get("trials",0))
        if trials<1 or trials>MAX_SAMPLES or successes<0 or successes>trials: raise HTTPException(status_code=400,detail="invalid successes/trials")
        z=finite(p.get("z",1.959963984540054),"z"); phat=successes/trials; den=1+z*z/trials
        center=(phat+z*z/(2*trials))/den; half=z*math.sqrt((phat*(1-phat)+z*z/(4*trials))/trials)/den
        return {"kind":"binomial-reliability","modelKind":"binomial-wilson","sampleCount":trials,"eventCount":trials-successes,"horizon":0,"metrics":{"reliability":phat,"failures":trials-successes,"interval":{"lower":max(0.0,center-half),"upper":min(1.0,center+half)}}}
    if op=="workspace.reliability.inverse-power-life":
        stresses=p.get("stresses") or []; lives=p.get("lives") or []
        if not isinstance(stresses,list) or not isinstance(lives,list) or len(stresses)!=len(lives) or not 2<=len(stresses)<=MAX_SAMPLES: raise HTTPException(status_code=400,detail="stresses and lives must be equal-length arrays with at least two points")
        xs=[math.log(positive(x,"stress")) for x in stresses]; ys=[math.log(positive(y,"life")) for y in lives]
        intercept,slope,r2=linear_fit(xs,ys); exponent=-slope; coefficient=math.exp(intercept)
        target=p.get("targetStress"); predicted=None
        if target is not None: predicted=coefficient*(positive(target,"targetStress")**(-exponent))
        return {"kind":"inverse-power-life","modelKind":"inverse-power","sampleCount":len(xs),"eventCount":len(xs),"horizon":0,"metrics":{"coefficient":coefficient,"exponent":exponent,"r2":r2,"predictedLife":predicted}}
    raise HTTPException(status_code=400,detail="Unregistered reliability operation")

@app.get('/health')
def health():
    return {"ok":True,"service":"Sustainable Catalyst Workspace Reliability, Survival & Failure-Time Runtime","version":VERSION,"runtime":RUNTIME,"operations":list(OPS),"boundedOperationsOnly":True,"arbitraryCodeExecution":False,"maxSamples":MAX_SAMPLES,"maxComponents":MAX_COMPONENTS,"maxGroups":MAX_GROUPS}

@app.post('/v1/execute')
def run(e:Envelope, authorization:str|None=Header(default=None)):
    auth(authorization)
    if e.operation not in OPS: raise HTTPException(status_code=400,detail="Unregistered reliability operation")
    r=execute(e.operation,e.payload)
    return {"schema":"sc-workspace-reliability-analysis-result/1.0","runtime":RUNTIME,"operation":e.operation,"inputFingerprint":fingerprint(e.payload),"result":r}
