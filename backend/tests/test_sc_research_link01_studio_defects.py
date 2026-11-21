"""SC-RESEARCH-LINK-01 follow-up: Publication Studio defects found in production acceptance.

1. A step-up refusal sends the person to Sustainable Catalyst Identity (the code travels on the error; the message is
   human text and never contained the code).
2. Typed declarations, notes and the disclosure acknowledgement survive panel re-renders and the sign-in round trip.
3. "Release for citation" is a POST (api() only POSTs when given a body).

The page script is plain browser JavaScript inlined into the Studio page; these tests run the real functions in Node
with minimal stubs for fetch, location and sessionStorage.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"
OUTPUTS = (APP / "reporting_outputs_ui.js").read_text()
PUBLICATION = (APP / "reporting_publication_ui.js").read_text()


def _function(src: str, name: str) -> str:
    start = src.index(f"async function {name}(") if f"async function {name}(" in src else src.index(f"function {name}(")
    depth, i = 0, src.index("{", start)
    while True:
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        if depth == 0:
            return src[start:i + 1]
        i += 1


def _drafts_block() -> str:
    start = OUTPUTS.index("const OUT=")
    return OUTPUTS[start:OUTPUTS.index("async function readPacket(")]


HARNESS = r"""
const store=new Map();
globalThis.sessionStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)};
let assigned=null,lastStatus=null,requests=[];
globalThis.location={pathname:'/v1/private-research/reporting-studio/publication',search:'?project=p1',assign:u=>{assigned=u}};
function status(s){lastStatus=s} function signInPrompt(){}
let reply=null;
globalThis.fetch=async(url,opt)=>{requests.push({url,method:(opt&&opt.method)||'GET',body:opt&&opt.body});
 return {ok:reply.status<400,status:reply.status,text:async()=>JSON.stringify(reply.body)}};
__API__
__DRAFTS__
__STEPUP__
function node(prop){const n={value:'',checked:false,listeners:{},addEventListener(t,f){this.listeners[t]=f}};return n}
(async()=>{
 const out={};
 for(const [shape,body] of [['detail',{detail:{code:'step-up-required',message:'Sign in again (password and second factor) to authorize.',loginUrl:'/v1/auth/login?stepUp=true'}}],
                            ['flattened',{ok:false,code:'step-up-required',message:'Sign in again (password and second factor) to authorize.'}]]){
  reply={status:403,body};assigned=null;
  let err;try{await api('/decide',{decision:'approve'})}catch(e){err=e}
  stepUp(err);out[shape]={code:err.code,status:err.status,message:err.message,assigned,lastStatus};
 }
 reply={status:403,body:{detail:'Only the owner may do this.'}};
 let other;try{await api('/decide',{})}catch(e){other=e}
 try{stepUp(other);out.otherRethrown=false}catch(e){out.otherRethrown=e===other}
 const spoof=Object.assign(Error('HTTP 403: step-up-required'),{status:403});
 try{stepUp(spoof);out.messageOnlyRethrown=false}catch(e){out.messageOnlyRethrown=e===spoof}

 // Drafts: typed text survives a re-render (new nodes) and a reload (fresh memory, same tab storage).
 OUT.drafts=null;store.clear();
 const a=keepDraft('self:r1',node()),ack=keepDraft('ack:r1',node(),'checked'),b=keepDraft('self:r2',node());
 a.value='I checked the exact revision and its single source.';a.listeners.input();
 ack.checked=true;ack.listeners.change();
 b.value='Second declaration text, typed but not yet sent.';b.listeners.input();
 const rerender=keepDraft('self:r2',node());
 OUT.drafts=null;  // page reload after the Identity step-up
 const reloaded=[keepDraft('self:r1',node()).value,keepDraft('ack:r1',node(),'checked').checked,keepDraft('self:r2',node()).value];
 dropDrafts('self:r1','ack:r1');
 OUT.drafts=null;
 out.drafts={rerender:rerender.value,reloaded,afterDrop:[keepDraft('self:r1',node()).value,keepDraft('self:r2',node()).value],
  stored:store.get(DRAFT_KEY)};
 dropDrafts('self:r2');out.drafts.clearedStorage=store.has(DRAFT_KEY);

 // api() with an empty body object is a POST.
 reply={status:200,body:{ok:true}};requests=[];
 await api('/release',{});out.release=requests[0];
 process.stdout.write(JSON.stringify(out));
})().catch(e=>{console.error(e);process.exit(1)});
"""


@pytest.fixture(scope="module")
def run():
    node = shutil.which("node")
    if not node:
        pytest.skip("node is required to run the page script")
    script = (HARNESS.replace("__API__", _function(PUBLICATION, "api"))
              .replace("__DRAFTS__", _drafts_block())
              .replace("__STEPUP__", _function(OUTPUTS, "stepUp")))
    done = subprocess.run([node, "-e", script], capture_output=True, text=True, timeout=30)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


@pytest.mark.parametrize("shape", ["detail", "flattened"])
def test_step_up_refusal_redirects_to_identity_and_returns_here(run, shape):
    r = run[shape]
    assert r["code"] == "step-up-required" and r["status"] == 403
    assert "step-up-required" not in r["message"]  # the old test of the message could never match
    assert r["assigned"] == ("/v1/auth/login?stepUp=true&returnTo="
                             "%2Fv1%2Fprivate-research%2Freporting-studio%2Fpublication%3Fproject%3Dp1")
    assert "declarations are kept" in r["lastStatus"]


def test_other_refusals_are_reported_not_redirected(run):
    assert run["otherRethrown"] is True
    assert run["messageOnlyRethrown"] is True  # only the server's code, never message text, triggers sign-in


def test_unsaved_declarations_survive_rerender_and_sign_in_and_clear_after_use(run):
    d = run["drafts"]
    assert d["rerender"] == "Second declaration text, typed but not yet sent."
    assert d["reloaded"] == ["I checked the exact revision and its single source.", True,
                             "Second declaration text, typed but not yet sent."]
    assert d["afterDrop"] == ["", "Second declaration text, typed but not yet sent."]
    assert "I checked" not in d["stored"]
    assert d["clearedStorage"] is False


def test_drafts_live_only_in_this_tab():
    block = _drafts_block()
    assert "sessionStorage" in block and "localStorage" not in OUTPUTS


def test_release_for_citation_posts(run):
    assert run["release"]["method"] == "POST" and run["release"]["body"] == "{}"
    call = re.search(r"act\('Release for citation',async\(\)=>\{await api\((.*?)\);status", OUTPUTS).group(1)
    assert call.endswith("/release'),{}")


def test_every_ui_mutation_sends_a_body():
    """POST-only routes in the page are always called with a body, so api() issues POST."""
    found = 0
    for m in re.finditer(r"'[^']*/(release|submit|decide|attach|revoke|publish|withdraw|unlist|relist)'(\)?)(.)", OUTPUTS):
        found += 1
        assert m.group(3) == ",", OUTPUTS[max(0, m.start() - 80):m.end() + 10]
    assert found >= 5
