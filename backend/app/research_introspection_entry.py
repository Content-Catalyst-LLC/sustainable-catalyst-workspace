"""Private ASGI entry only. Never mount on the public Workspace router/ingress."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .research_session_introspection import router
from .config import get_settings
from .migrate_security import require_schema

@asynccontextmanager
async def lifespan(app):
    settings = get_settings()
    if not settings.session_revocation_enforced:
        raise RuntimeError("Private introspection requires enforced revocation")
    # The private service must validate the original Workspace cookie with
    # the original dedicated signing key; never bootstrap an identity from
    # a generic service token fallback.
    from pathlib import Path
    from .session_auth import _secret
    if not (getattr(settings, "session_signing_secret", "").strip() or
            getattr(settings, "session_signing_secret_file", "").strip()):
        raise RuntimeError("Private introspection requires the Workspace signing key")
    if len(_secret()) < 32:
        raise RuntimeError("Private introspection signing key unavailable")
    require_schema()
    yield

app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
@app.middleware("http")
async def private_boundary(request:Request,call_next):
    if request.url.path!="/internal/v1/workspace/session/introspect":
        return JSONResponse({"detail":"Not found"},status_code=404,headers={"Cache-Control":"no-store"})
    if request.method!="POST":
        return JSONResponse({"detail":"Method not allowed"},status_code=405,headers={"Cache-Control":"no-store"})
    if request.headers.get("content-type","").split(";")[0]!="application/json":
        return JSONResponse({"detail":"JSON required"},status_code=415,headers={"Cache-Control":"no-store"})
    length=request.headers.get("content-length","")
    if not length.isdigit() or int(length)>12288:
        return JSONResponse({"detail":"Bounded content length required"},status_code=413,headers={"Cache-Control":"no-store"})
    if len(await request.body())>12288:
        return JSONResponse({"detail":"Request too large"},status_code=413,headers={"Cache-Control":"no-store"})
    response=await call_next(request)
    response.headers["Cache-Control"]="no-store"
    response.headers["Pragma"]="no-cache"
    response.headers["X-Content-Type-Options"]="nosniff"
    return response
app.include_router(router)
