#!/usr/bin/env python3
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
import argparse, contextlib, functools, hashlib, json, threading
VERSION="3.70.0"; MANIFEST_SCHEMA="sc-workspace-runtime-asset-manifest/1.0"; REPORT_SCHEMA="sc-workspace-standalone-production-certification-report/1.0"
FORBIDDEN=("wp-content","wp-json","wp-admin","sc-workspace-wordpress-host-adapter","sc-workspace-wordpress-transport-adapter","sc-workspace-wordpress-auth-adapter","sc-workspace-wordpress-thin-adapter")
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(name,ok,detail=""):
 print(f"{name}={'PASS' if ok else 'FAIL'}"+(f" :: {detail}" if detail and not ok else "")); return {"name":name,"ok":bool(ok),"detail":str(detail or "")}
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
@contextlib.contextmanager
def server(root):
 h=functools.partial(Quiet,directory=str(root)); s=ThreadingHTTPServer(("127.0.0.1",0),h); t=threading.Thread(target=s.serve_forever,daemon=True); t.start()
 try:
  host,port=s.server_address; yield f"http://{host}:{port}"
 finally:
  s.shutdown(); s.server_close(); t.join(timeout=5)
def fetch(url):
 req=Request(url,headers={"User-Agent":"Sustainable-Catalyst-Workspace-Certification/3.70.0","Accept":"application/json"})
 with urlopen(req,timeout=15) as r:
  if r.status!=200: raise RuntimeError(f"HTTP {r.status}: {url}")
  return r.read()
def certify(root,backend_url=""):
 root=root.resolve(); gates=[]; m=json.loads((root/"asset-manifest-v3700.json").read_text())
 gates.append(emit("WORKSPACE_V3700_STANDALONE_MANIFEST",m.get("schema")==MANIFEST_SCHEMA and m.get("version")==VERSION and m.get("host")=="standalone" and m.get("wordpressRequired") is False))
 missing=[]; bad=[]
 for aid,e in m.get("assets",{}).items():
  p=root/"assets"/e["file"]
  if not p.is_file(): missing.append(f"{aid}:{e['file']}"); continue
  if e.get("sha256") and digest(p)!=e["sha256"]: bad.append(aid)
 gates.append(emit("WORKSPACE_V3700_STANDALONE_ASSET_COMPLETENESS",not missing,";".join(missing)))
 gates.append(emit("WORKSPACE_V3700_STANDALONE_ASSET_INTEGRITY",not bad,";".join(bad)))
 hits=[]
 for p in [root/"index.html",root/"config.js",root/"bootstrap.js"]+[root/"assets"/e["file"] for e in m.get("assets",{}).values()]:
  if p.is_file():
   txt=p.read_text(errors="ignore").lower()
   for mark in FORBIDDEN:
    if mark in txt: hits.append(f"{p.name}:{mark}")
 gates.append(emit("WORKSPACE_V3700_WORDPRESS_ABSENT",not hits,";".join(hits)))
 bt=(root/"bootstrap.js").read_text(); gates.append(emit("WORKSPACE_V3700_MANIFEST_DRIVEN_BOOT","sc-workspace-runtime-asset-manifest-v3700.js" in bt and "manifest.loadOrder" in bt and "manifest.assets[id]" in bt))
 cfg=(root/"config.js").read_text(); gates.append(emit("WORKSPACE_V3700_DIRECT_BACKEND_CONFIG","workspaceVersion: '3.70.0'" in cfg and "https://workspace-api.sustainablecatalyst.com" in cfg and "wordpressRequired: false" in cfg))
 idx=(root/"index.html").read_text(); gates.append(emit("WORKSPACE_V3700_FRONTEND_IDENTITY",'data-version="3.70.0"' in idx and "workspace-standalone-shell-v3700.css" in idx))
 with server(root) as base:
  urls=["/","/index.html","/config.js","/bootstrap.js","/asset-manifest-v3700.json","/assets/sc-workspace-runtime-asset-manifest-v3700.js","/assets/sc-workspace-application-kernel-v3700.js","/assets/sc-workspace-v3-stable-research-os-baseline-v3700.js"]; served=[]
  for u in urls:
   try: served.append((u,len(fetch(base+u))))
   except Exception as e: served.append((u,0,str(e)))
 gates.append(emit("WORKSPACE_V3700_STATIC_HTTP_SERVE",all(len(x)==2 and x[1]>0 for x in served),json.dumps(served)))
 backend=None
 if backend_url:
  try:
   health=json.loads(fetch(backend_url.rstrip("/")+"/health")); base=json.loads(fetch(backend_url.rstrip("/")+"/v1/workspace-v3-stable-baseline")); backend={"healthVersion":health.get("version"),"baselineVersion":base.get("version"),"baselineValid":base.get("baselineValid")}; gates.append(emit("WORKSPACE_V3700_LIVE_BACKEND",health.get("ok") is True and health.get("version")==VERSION and base.get("version")==VERSION and base.get("baselineValid") is True,json.dumps(backend,sort_keys=True)))
  except Exception as e: backend={"error":str(e)}; gates.append(emit("WORKSPACE_V3700_LIVE_BACKEND",False,str(e)))
 passed=all(g["ok"] for g in gates); return {"schema":REPORT_SCHEMA,"version":VERSION,"passed":passed,"gateCount":len(gates),"gates":gates,"backendProbe":backend,"frontendHost":"https://workspace.sustainablecatalyst.com","apiBase":"https://workspace-api.sustainablecatalyst.com","wordpressRequired":False}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--root",default=None); ap.add_argument("--backend-url",default=""); ap.add_argument("--write-report",default=""); a=ap.parse_args(); root=Path(a.root).resolve() if a.root else Path(__file__).resolve().parent; report=certify(root,a.backend_url)
 if a.write_report: Path(a.write_report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 if not report["passed"]: raise SystemExit(1)
 print("WORKSPACE_V3700_STANDALONE_PRODUCTION_CERTIFICATION=PASS")
if __name__=="__main__": main()
