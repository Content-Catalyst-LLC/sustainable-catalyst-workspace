from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
from statistics import NormalDist
from typing import Any

import numpy as np
from fastapi import FastAPI, Header, HTTPException
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

SERVICE = "Sustainable Catalyst Workspace Forecasting & Time-Series Runtime"
SERVICE_VERSION = "2.18.0"
RUNTIME = "python-statsmodels-forecasting"
TOKEN = os.getenv("SC_WORKSPACE_FORECAST_RUNTIME_TOKEN", "").strip()
MAX_PAYLOAD = max(1024, min(int(os.getenv("SC_WORKSPACE_FORECAST_MAX_PAYLOAD_BYTES", str(10*1024*1024))), 25*1024*1024))
MAX_POINTS = max(32, min(int(os.getenv("SC_WORKSPACE_FORECAST_MAX_POINTS", "50000")), 100000))
MAX_HORIZON = max(1, min(int(os.getenv("SC_WORKSPACE_FORECAST_MAX_HORIZON", "3650")), 10000))
MAX_SEASONAL_PERIOD = max(2, min(int(os.getenv("SC_WORKSPACE_FORECAST_MAX_SEASONAL_PERIOD", "365")), 2000))

OPERATIONS = {
    "workspace.forecast.naive",
    "workspace.forecast.seasonal-naive",
    "workspace.forecast.linear-trend",
    "workspace.forecast.exponential-smoothing",
    "workspace.forecast.holt-winters",
    "workspace.forecast.arima",
    "workspace.forecast.backtest",
    "workspace.forecast.evaluate",
}
app = FastAPI(title=SERVICE, version=SERVICE_VERSION, docs_url=None, redoc_url=None)

def _auth(authorization: str|None):
    if not TOKEN: raise HTTPException(503,"forecast runtime service credential is not configured")
    if not authorization or not hmac.compare_digest(authorization.strip(), f"Bearer {TOKEN}"):
        raise HTTPException(401,"forecast runtime service authentication failed")

def _f(x:Any, default:float, lo:float, hi:float)->float:
    try: v=float(x)
    except (TypeError,ValueError): v=default
    if not math.isfinite(v): v=default
    return max(lo,min(hi,v))

def _i(x:Any, default:int, lo:int, hi:int)->int:
    try: v=int(x)
    except (TypeError,ValueError): v=default
    return max(lo,min(hi,v))

def _series(payload:dict[str,Any])->tuple[np.ndarray,str]:
    values=payload.get("values")
    if not isinstance(values,list) or not values:
        rows=payload.get("rows")
        col=str(payload.get("valueColumn") or "value").strip()
        if not isinstance(rows,list) or not rows: raise HTTPException(400,"values or rows must contain a non-empty time series")
        values=[r.get(col) if isinstance(r,dict) else None for r in rows]
    if len(values)>MAX_POINTS: raise HTTPException(413,"time-series point limit exceeded")
    out=[]
    for v in values:
        try: n=float(v)
        except (TypeError,ValueError): raise HTTPException(400,"time-series values must be numeric")
        if not math.isfinite(n): raise HTTPException(400,"time-series values must be finite")
        out.append(n)
    if len(out)<6: raise HTTPException(400,"at least six observations are required")
    canonical=json.dumps(out,separators=(",",":"))
    return np.asarray(out,dtype=float), hashlib.sha256(canonical.encode()).hexdigest()

def _metrics(actual, predicted)->dict[str,float]:
    a=np.asarray(actual,dtype=float); p=np.asarray(predicted,dtype=float)
    if len(a)!=len(p) or not len(a): raise HTTPException(400,"actual and predicted series must have equal non-zero length")
    e=a-p; abs_e=np.abs(e)
    nz=np.abs(a)>1e-12
    mape=float(np.mean(abs_e[nz]/np.abs(a[nz]))*100) if np.any(nz) else 0.0
    denom=np.abs(a)+np.abs(p); mask=denom>1e-12
    smape=float(np.mean(2*abs_e[mask]/denom[mask])*100) if np.any(mask) else 0.0
    return {"mae":float(np.mean(abs_e)),"rmse":float(np.sqrt(np.mean(e*e))),"mape":mape,"smape":smape,"bias":float(np.mean(p-a))}

def _intervals(point:np.ndarray, residuals:np.ndarray, levels:list[float])->list[dict[str,Any]]:
    sigma=float(np.std(residuals,ddof=1)) if len(residuals)>1 else 0.0
    result=[]
    for level in levels:
        lv=_f(level,.95,.5,.999)
        z=NormalDist().inv_cdf((1+lv)/2)
        widths=np.asarray([z*sigma*math.sqrt(i+1) for i in range(len(point))])
        result.append({"level":lv,"lower":[float(x) for x in point-widths],"upper":[float(x) for x in point+widths]})
    return result

def _levels(payload):
    raw=payload.get("intervalLevels",[0.8,0.95]); raw=raw if isinstance(raw,list) else [raw]
    return sorted(set(_f(x,.95,.5,.999) for x in raw))[:4]

def _forecast(kind:str, y:np.ndarray, payload:dict[str,Any])->dict[str,Any]:
    h=_i(payload.get("horizon"),12,1,MAX_HORIZON)
    seasonal=_i(payload.get("seasonalPeriod"),12,2,MAX_SEASONAL_PERIOD)
    levels=_levels(payload); params={}; fitted=np.full_like(y,np.nan,dtype=float)
    if kind=="naive":
        point=np.repeat(y[-1],h); fitted[1:]=y[:-1]
    elif kind=="seasonal-naive":
        if len(y)<seasonal+2: raise HTTPException(400,"series is too short for requested seasonal period")
        point=np.asarray([y[len(y)-seasonal+(i%seasonal)] for i in range(h)],dtype=float); fitted[seasonal:]=y[:-seasonal]; params={"seasonalPeriod":seasonal}
    elif kind=="linear-trend":
        t=np.arange(len(y),dtype=float); slope,intercept=np.polyfit(t,y,1); fitted=intercept+slope*t; point=intercept+slope*np.arange(len(y),len(y)+h,dtype=float); params={"slope":float(slope),"intercept":float(intercept)}
    elif kind=="exponential-smoothing":
        alpha=_f(payload.get("alpha"),0.2,0.001,0.999); level=float(y[0]); fitted[0]=level
        for i in range(1,len(y)): fitted[i]=level; level=alpha*float(y[i])+(1-alpha)*level
        point=np.repeat(level,h); params={"alpha":alpha}
    elif kind=="holt-winters":
        trend=str(payload.get("trend") or "add").lower(); trend=trend if trend in {"add","mul"} else None
        seasonal_kind=str(payload.get("seasonal") or "add").lower(); seasonal_kind=seasonal_kind if seasonal_kind in {"add","mul"} else None
        if seasonal_kind and len(y)<2*seasonal: raise HTTPException(400,"Holt-Winters requires at least two seasonal cycles")
        fit=ExponentialSmoothing(y,trend=trend,seasonal=seasonal_kind,seasonal_periods=seasonal if seasonal_kind else None,initialization_method="estimated").fit(optimized=True,use_brute=False)
        fitted=np.asarray(fit.fittedvalues,dtype=float); point=np.asarray(fit.forecast(h),dtype=float); params={"trend":trend or "none","seasonal":seasonal_kind or "none","seasonalPeriod":seasonal if seasonal_kind else 0}
    elif kind=="arima":
        order=payload.get("order",[1,1,0]); order=order if isinstance(order,list) and len(order)==3 else [1,1,0]
        p,d,q=(_i(order[0],1,0,5),_i(order[1],1,0,2),_i(order[2],0,0,5))
        fit=ARIMA(y,order=(p,d,q),enforce_stationarity=False,enforce_invertibility=False).fit(); fitted=np.asarray(fit.predict(start=0,end=len(y)-1),dtype=float); fr=fit.get_forecast(steps=h); point=np.asarray(fr.predicted_mean,dtype=float)
        intervals=[]
        for lv in levels:
            ci=np.asarray(fr.conf_int(alpha=1-lv),dtype=float); intervals.append({"level":lv,"lower":[float(x) for x in ci[:,0]],"upper":[float(x) for x in ci[:,1]]})
        valid=np.isfinite(fitted)
        return {"modelKind":kind,"horizon":h,"forecast":[float(x) for x in point],"fitted":[float(x) if math.isfinite(float(x)) else None for x in fitted],"parameters":{"order":[p,d,q]},"fitMetrics":_metrics(y[valid],fitted[valid]) if np.any(valid) else {},"intervals":intervals}
    elif kind=="autoregression":
        lags=_i(payload.get("lags"),min(12,max(1,len(y)//5)),1,min(365,max(1,len(y)//2-1))); fit=AutoReg(y,lags=lags,old_names=False,trend="ct").fit(); fitted=np.asarray(fit.predict(start=0,end=len(y)-1),dtype=float); point=np.asarray(fit.predict(start=len(y),end=len(y)+h-1,dynamic=False),dtype=float); params={"lags":lags}
    else: raise HTTPException(400,"forecast model is not registered")
    valid=np.isfinite(fitted); resid=y[valid]-fitted[valid]
    return {"modelKind":kind,"horizon":h,"forecast":[float(x) for x in point],"fitted":[float(x) if math.isfinite(float(x)) else None for x in fitted],"parameters":params,"fitMetrics":_metrics(y[valid],fitted[valid]) if np.any(valid) else {},"intervals":_intervals(point,resid,levels)}

def _backtest(y:np.ndarray,payload:dict[str,Any])->dict[str,Any]:
    model=str(payload.get("modelType") or "naive").strip().lower()
    if model not in {"naive","seasonal-naive","linear-trend","exponential-smoothing","autoregression"}: raise HTTPException(400,"backtest modelType is outside the bounded registry")
    test=_i(payload.get("testPoints"),max(2,min(12,len(y)//4)),2,max(2,len(y)//2))
    if len(y)-test<6: raise HTTPException(400,"insufficient training observations for requested backtest")
    actual=[]; pred=[]
    for i in range(len(y)-test,len(y)):
        sub=dict(payload); sub["horizon"]=1; r=_forecast(model,y[:i],sub); pred.append(float(r["forecast"][0])); actual.append(float(y[i]))
    return {"modelKind":model,"evaluationKind":"rolling-origin","trainPoints":len(y)-test,"testPoints":test,"actual":actual,"predicted":pred,"metrics":_metrics(actual,pred)}

@app.get("/health")
def health():
    return {"ok":True,"service":SERVICE,"version":SERVICE_VERSION,"runtime":RUNTIME,"operations":sorted(OPERATIONS),"boundedOperationsOnly":True,"arbitraryCodeExecution":False,"maxPoints":MAX_POINTS,"maxHorizon":MAX_HORIZON,"maxSeasonalPeriod":MAX_SEASONAL_PERIOD}

@app.post("/v1/execute")
def execute(envelope:dict[str,Any], authorization:str|None=Header(default=None)):
    _auth(authorization); raw=json.dumps(envelope,separators=(",",":"),default=str).encode()
    if len(raw)>MAX_PAYLOAD: raise HTTPException(413,"forecast payload limit exceeded")
    op=str(envelope.get("operation") or "")
    if op not in OPERATIONS: raise HTTPException(400,"forecast operation is not registered")
    payload=envelope.get("payload") if isinstance(envelope.get("payload"),dict) else {}
    if op=="workspace.forecast.evaluate":
        result={"modelKind":"evaluation","evaluationKind":"direct","metrics":_metrics(payload.get("actual") or [],payload.get("predicted") or [])}; return {"ok":True,"runtime":RUNTIME,"operation":op,"result":result}
    y,fingerprint=_series(payload); result=_backtest(y,payload) if op=="workspace.forecast.backtest" else _forecast(op.split("workspace.forecast.",1)[1],y,payload)
    result["datasetFingerprint"]=fingerprint; result["frequency"]=str(payload.get("frequency") or "unspecified")[:64]; result["valueColumn"]=str(payload.get("valueColumn") or "value")[:160]; result["timeColumn"]=str(payload.get("timeColumn") or "")[:160]
    return {"ok":True,"runtime":RUNTIME,"operation":op,"result":result}
