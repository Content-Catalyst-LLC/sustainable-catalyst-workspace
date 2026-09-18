\
import hashlib, json, math, os, random, statistics
from typing import Any
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

VERSION="2.20.0"
RUNTIME="python-monte-carlo-uq"
OPS=(
 "workspace.uncertainty.monte-carlo-weighted-sum",
 "workspace.uncertainty.bootstrap-interval",
 "workspace.uncertainty.latin-hypercube",
 "workspace.uncertainty.correlated-normal",
 "workspace.uncertainty.empirical-summary",
 "workspace.uncertainty.rank-correlation-sensitivity",
 "workspace.uncertainty.variance-contribution-linear",
 "workspace.uncertainty.scenario-envelope",
)
MAX_DRAWS=int(os.getenv("SC_WORKSPACE_UNCERTAINTY_MAX_DRAWS","20000"))
MAX_ROWS=int(os.getenv("SC_WORKSPACE_UNCERTAINTY_MAX_ROWS","10000"))
MAX_VARIABLES=int(os.getenv("SC_WORKSPACE_UNCERTAINTY_MAX_VARIABLES","64"))
TOKEN=os.getenv("SC_WORKSPACE_UNCERTAINTY_RUNTIME_TOKEN","").strip()
app=FastAPI(title="Sustainable Catalyst Workspace Monte Carlo & Uncertainty Quantification Runtime",version=VERSION)

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

def bounded_int(x,name,lo,hi):
    try: v=int(x)
    except Exception: raise HTTPException(status_code=400,detail=f"{name} must be an integer")
    if v<lo or v>hi: raise HTTPException(status_code=400,detail=f"{name} must be between {lo} and {hi}")
    return v

def quantile(sorted_vals,p):
    if not sorted_vals: return None
    i=(len(sorted_vals)-1)*p; lo=int(math.floor(i)); hi=int(math.ceil(i))
    if lo==hi: return float(sorted_vals[lo])
    return float(sorted_vals[lo]*(hi-i)+sorted_vals[hi]*(i-lo))

def interval(vals,level):
    s=sorted(float(x) for x in vals); a=(1-level)/2
    return {"level":level,"lower":quantile(s,a),"upper":quantile(s,1-a)}

def summary(vals,level=0.95):
    xs=[float(x) for x in vals]
    if not xs: raise HTTPException(status_code=400,detail="values must not be empty")
    m=sum(xs)/len(xs); var=(sum((x-m)**2 for x in xs)/(len(xs)-1)) if len(xs)>1 else 0.0
    s=sorted(xs)
    return {"n":len(xs),"mean":m,"sd":math.sqrt(max(var,0.0)),"min":s[0],"max":s[-1],"q05":quantile(s,0.05),"median":quantile(s,0.5),"q95":quantile(s,0.95),"interval":interval(s,level)}

def fingerprint(doc):
    return hashlib.sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def parse_level(p):
    level=finite(p.get("intervalLevel",0.95),"intervalLevel")
    if not 0.5 < level < 0.9999: raise HTTPException(status_code=400,detail="intervalLevel must be between 0.5 and 0.9999")
    return level

def sample_distribution(spec,rng):
    if not isinstance(spec,dict): raise HTTPException(status_code=400,detail="distribution must be an object")
    kind=str(spec.get("kind") or "normal").lower()
    if kind=="constant": return finite(spec.get("value",0),"value")
    if kind=="normal": return rng.gauss(finite(spec.get("mean",0),"mean"),pos(spec.get("sd",1),"sd"))
    if kind=="uniform":
        lo=finite(spec.get("min",0),"min"); hi=finite(spec.get("max",1),"max")
        if not lo < hi: raise HTTPException(status_code=400,detail="uniform min must be < max")
        return rng.uniform(lo,hi)
    if kind=="triangular":
        lo=finite(spec.get("min",0),"min"); hi=finite(spec.get("max",1),"max"); mode=finite(spec.get("mode",(lo+hi)/2),"mode")
        if not lo < hi or not lo <= mode <= hi: raise HTTPException(status_code=400,detail="triangular parameters are invalid")
        return rng.triangular(lo,hi,mode)
    if kind=="beta":
        a=pos(spec.get("alpha",1),"alpha"); b=pos(spec.get("beta",1),"beta")
        lo=finite(spec.get("min",0),"min"); hi=finite(spec.get("max",1),"max")
        if not lo < hi: raise HTTPException(status_code=400,detail="beta min must be < max")
        return lo+(hi-lo)*rng.betavariate(a,b)
    raise HTTPException(status_code=400,detail=f"Unsupported distribution kind: {kind}")

def ranks(vals):
    n=len(vals); order=sorted(range(n),key=lambda i: vals[i]); out=[0.0]*n; i=0
    while i<n:
        j=i
        while j+1<n and vals[order[j+1]]==vals[order[i]]: j+=1
        rank=(i+j+2)/2.0
        for k in range(i,j+1): out[order[k]]=rank
        i=j+1
    return out

def corr(a,b):
    if len(a)!=len(b) or len(a)<2: return 0.0
    ma=sum(a)/len(a); mb=sum(b)/len(b)
    da=sum((x-ma)**2 for x in a); db=sum((y-mb)**2 for y in b)
    if da<=0 or db<=0: return 0.0
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(da*db)

def cholesky(a):
    n=len(a); L=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            s=sum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                v=a[i][i]-s
                if v<=1e-12: raise HTTPException(status_code=400,detail="correlationMatrix must be positive definite")
                L[i][j]=math.sqrt(v)
            else:
                L[i][j]=(a[i][j]-s)/L[j][j]
    return L

def execute(op,p):
    level=parse_level(p); seed=int(p.get("seed",202620)); rng=random.Random(seed)
    if op=="workspace.uncertainty.monte-carlo-weighted-sum":
        terms=p.get("terms") or []
        if not isinstance(terms,list) or not 1<=len(terms)<=MAX_VARIABLES: raise HTTPException(status_code=400,detail=f"terms must contain 1..{MAX_VARIABLES} items")
        draws=bounded_int(p.get("draws",5000),"draws",500,MAX_DRAWS); offset=finite(p.get("offset",0),"offset")
        clean=[]
        for idx,t in enumerate(terms):
            if not isinstance(t,dict): raise HTTPException(status_code=400,detail="each term must be an object")
            clean.append((str(t.get("name") or f"x{idx+1}")[:96],finite(t.get("coefficient",1),"coefficient"),t.get("distribution") or {}))
        sims=[]
        for _ in range(draws): sims.append(offset+sum(c*sample_distribution(d,rng) for _n,c,d in clean))
        out=summary(sims,level); threshold=p.get("threshold")
        if threshold is not None:
            th=finite(threshold,"threshold"); out["threshold"]=th; out["probabilityAboveThreshold"]=sum(x>th for x in sims)/draws
        return {"kind":"monte-carlo-weighted-sum","draws":draws,"seed":seed,"termCount":len(clean),"summary":out,"interval":out["interval"]}
    if op=="workspace.uncertainty.bootstrap-interval":
        vals=p.get("values") or []
        if not isinstance(vals,list) or not 2<=len(vals)<=MAX_ROWS: raise HTTPException(status_code=400,detail=f"values must contain 2..{MAX_ROWS} items")
        xs=[finite(x,"value") for x in vals]; draws=bounded_int(p.get("draws",5000),"draws",500,MAX_DRAWS)
        stat=str(p.get("statistic") or "mean").lower()
        if stat not in {"mean","median"}: raise HTTPException(status_code=400,detail="statistic must be mean or median")
        stats=[]; n=len(xs)
        for _ in range(draws):
            sample=[xs[rng.randrange(n)] for _ in range(n)]
            stats.append(sum(sample)/n if stat=="mean" else statistics.median(sample))
        point=sum(xs)/n if stat=="mean" else statistics.median(xs); ci=interval(stats,level)
        return {"kind":"bootstrap-interval","statistic":stat,"n":n,"draws":draws,"seed":seed,"estimate":point,"interval":ci,"summary":summary(stats,level)}
    if op=="workspace.uncertainty.latin-hypercube":
        variables=p.get("variables") or []
        if not isinstance(variables,list) or not 1<=len(variables)<=min(MAX_VARIABLES,32): raise HTTPException(status_code=400,detail="variables must contain 1..32 items")
        samples=bounded_int(p.get("samples",100),"samples",2,min(MAX_ROWS,2000)); cols=[]
        for idx,v in enumerate(variables):
            if not isinstance(v,dict): raise HTTPException(status_code=400,detail="each variable must be an object")
            name=str(v.get("name") or f"x{idx+1}")[:96]; lo=finite(v.get("min",0),"min"); hi=finite(v.get("max",1),"max")
            if not lo<hi: raise HTTPException(status_code=400,detail="variable min must be < max")
            strata=[(i+rng.random())/samples for i in range(samples)]; rng.shuffle(strata); cols.append((name,lo,hi,strata))
        rows=[]
        for i in range(samples): rows.append({name:lo+(hi-lo)*strata[i] for name,lo,hi,strata in cols})
        return {"kind":"latin-hypercube","samples":samples,"seed":seed,"variables":[c[0] for c in cols],"rows":rows,"summary":{"variableCount":len(cols),"sampleCount":samples}}
    if op=="workspace.uncertainty.correlated-normal":
        means=p.get("means") or []; sds=p.get("sds") or []; matrix=p.get("correlationMatrix") or []
        if not isinstance(means,list) or not 1<=len(means)<=16 or len(sds)!=len(means) or len(matrix)!=len(means): raise HTTPException(status_code=400,detail="means/sds/correlationMatrix dimensions are invalid")
        mu=[finite(x,"mean") for x in means]; sd=[pos(x,"sd") for x in sds]; n=len(mu); corrm=[]
        for i,row in enumerate(matrix):
            if not isinstance(row,list) or len(row)!=n: raise HTTPException(status_code=400,detail="correlationMatrix must be square")
            rr=[finite(x,"correlation") for x in row]
            if abs(rr[i]-1)>1e-8: raise HTTPException(status_code=400,detail="correlationMatrix diagonal must equal 1")
            corrm.append(rr)
        for i in range(n):
            for j in range(n):
                if abs(corrm[i][j]-corrm[j][i])>1e-8 or abs(corrm[i][j])>1.0000001: raise HTTPException(status_code=400,detail="correlationMatrix must be symmetric with entries in [-1,1]")
        L=cholesky(corrm); draws=bounded_int(p.get("draws",2000),"draws",500,min(MAX_DRAWS,5000)); samples=[]; columns=[[] for _ in range(n)]
        for _ in range(draws):
            z=[rng.gauss(0,1) for _ in range(n)]; y=[sum(L[i][k]*z[k] for k in range(i+1)) for i in range(n)]; row=[mu[i]+sd[i]*y[i] for i in range(n)]
            for i,x in enumerate(row): columns[i].append(x)
            if len(samples)<25: samples.append(row)
        return {"kind":"correlated-normal","draws":draws,"seed":seed,"dimension":n,"summaries":[summary(c,level) for c in columns],"samplePreview":samples,"interval":{"level":level,"dimensions":n}}
    if op=="workspace.uncertainty.empirical-summary":
        vals=p.get("values") or []
        if not isinstance(vals,list) or not 1<=len(vals)<=MAX_ROWS*5: raise HTTPException(status_code=400,detail=f"values must contain 1..{MAX_ROWS*5} items")
        xs=[finite(x,"value") for x in vals]; out=summary(xs,level); qs=p.get("quantiles") or [0.01,0.05,0.25,0.5,0.75,0.95,0.99]
        if not isinstance(qs,list) or len(qs)>20: raise HTTPException(status_code=400,detail="quantiles must be an array of at most 20 values")
        s=sorted(xs); qout={}
        for qv in qs:
            qq=finite(qv,"quantile")
            if not 0<=qq<=1: raise HTTPException(status_code=400,detail="quantiles must be between 0 and 1")
            qout[str(qq)]=quantile(s,qq)
        threshold=p.get("threshold")
        if threshold is not None:
            th=finite(threshold,"threshold"); out["threshold"]=th; out["probabilityAboveThreshold"]=sum(x>th for x in xs)/len(xs)
        return {"kind":"empirical-summary","n":len(xs),"summary":out,"quantiles":qout,"interval":out["interval"]}
    if op=="workspace.uncertainty.rank-correlation-sensitivity":
        rows=p.get("rows") or []; outcome=str(p.get("outcome") or "")
        if not outcome or not isinstance(rows,list) or not 3<=len(rows)<=MAX_ROWS: raise HTTPException(status_code=400,detail="rows/outcome are invalid")
        features=p.get("features")
        if features is None:
            keys=set.intersection(*(set(r.keys()) for r in rows if isinstance(r,dict))) if rows else set(); features=sorted(k for k in keys if k!=outcome)
        if not isinstance(features,list) or not 1<=len(features)<=min(MAX_VARIABLES,32): raise HTTPException(status_code=400,detail="features must contain 1..32 names")
        clean=[]
        for row in rows:
            if not isinstance(row,dict): raise HTTPException(status_code=400,detail="each row must be an object")
            try: y=finite(row[outcome],outcome); xs=[finite(row[f],f) for f in features]
            except KeyError: raise HTTPException(status_code=400,detail="row is missing outcome or feature")
            clean.append((xs,y))
        yr=ranks([y for _x,y in clean]); scores=[]
        for idx,f in enumerate(features):
            xr=ranks([x[idx] for x,_y in clean]); scores.append({"feature":str(f)[:96],"spearman":corr(xr,yr)})
        scores.sort(key=lambda x:abs(x["spearman"]),reverse=True)
        return {"kind":"rank-correlation-sensitivity","n":len(clean),"outcome":outcome,"sensitivity":{"method":"spearman-rank-correlation","scores":scores},"summary":{"featureCount":len(features),"strongest":scores[0] if scores else {}}}
    if op=="workspace.uncertainty.variance-contribution-linear":
        terms=p.get("terms") or []
        if not isinstance(terms,list) or not 1<=len(terms)<=MAX_VARIABLES: raise HTTPException(status_code=400,detail=f"terms must contain 1..{MAX_VARIABLES} items")
        pieces=[]; total=0.0
        for idx,t in enumerate(terms):
            if not isinstance(t,dict): raise HTTPException(status_code=400,detail="each term must be an object")
            name=str(t.get("name") or f"x{idx+1}")[:96]; c=finite(t.get("coefficient",1),"coefficient"); sd=pos(t.get("sd",1),"sd"); v=(c*sd)**2; total+=v; pieces.append({"name":name,"variance":v})
        if total<=0: raise HTTPException(status_code=400,detail="total propagated variance must be positive")
        for item in pieces: item["share"]=item["variance"]/total
        pieces.sort(key=lambda x:x["share"],reverse=True)
        return {"kind":"linear-variance-contribution","sensitivity":{"method":"independent-linear-variance","contributions":pieces},"summary":{"totalVariance":total,"propagatedSd":math.sqrt(total),"dominantTerm":pieces[0]["name"]}}
    if op=="workspace.uncertainty.scenario-envelope":
        scenarios=p.get("scenarios") or []
        if not isinstance(scenarios,list) or not 2<=len(scenarios)<=1000: raise HTTPException(status_code=400,detail="scenarios must contain 2..1000 items")
        clean=[]
        for idx,s in enumerate(scenarios):
            if not isinstance(s,dict): raise HTTPException(status_code=400,detail="each scenario must be an object")
            clean.append({"name":str(s.get("name") or f"scenario-{idx+1}")[:120],"value":finite(s.get("value"),"value")})
        vals=[x["value"] for x in clean]; sm=summary(vals,level); lo=min(clean,key=lambda x:x["value"]); hi=max(clean,key=lambda x:x["value"])
        baseline=p.get("baseline")
        if baseline is not None:
            b=finite(baseline,"baseline"); sm["baseline"]=b; sm["minDeltaFromBaseline"]=lo["value"]-b; sm["maxDeltaFromBaseline"]=hi["value"]-b
        return {"kind":"scenario-envelope","scenarioCount":len(clean),"summary":sm,"interval":sm["interval"],"minimumScenario":lo,"maximumScenario":hi}
    raise HTTPException(status_code=400,detail="Unregistered uncertainty operation")

@app.get('/health')
def health():
    return {"ok":True,"service":"Sustainable Catalyst Workspace Monte Carlo & Uncertainty Quantification Runtime","version":VERSION,"runtime":RUNTIME,"operations":list(OPS),"boundedOperationsOnly":True,"arbitraryCodeExecution":False,"maxDraws":MAX_DRAWS,"maxRows":MAX_ROWS,"maxVariables":MAX_VARIABLES}

@app.post('/v1/execute')
def run(e:Envelope,authorization:str|None=Header(default=None)):
    auth(authorization)
    if e.operation not in OPS: raise HTTPException(status_code=400,detail="Operation is not registered")
    result=execute(e.operation,e.payload)
    return {"schema":"sc-workspace-uncertainty-result/1.0","runtime":RUNTIME,"operation":e.operation,"inputFingerprint":fingerprint(e.payload),"result":result}
