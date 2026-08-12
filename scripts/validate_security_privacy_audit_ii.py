from pathlib import Path
import re, sys
R=Path(__file__).resolve().parents[1]
PLUGIN=R/'wordpress/sustainable-catalyst-workspace'
PHP=(PLUGIN/'includes/class-sc-workspace.php').read_text()
MAIN=(PLUGIN/'sustainable-catalyst-workspace.php').read_text()

def fail(msg): raise SystemExit('FAIL - Security & Privacy Audit II source gate: '+msg)
def check(cond,msg):
    if not cond: fail(msg)
# Authenticated data routes must not become public.
for route in ["'/cloud-projects'","'/cloud-projects/(?P<project_id>","'/cloud-notebooks'","'/cloud-notebooks/(?P<notebook_id>"]:
    start=PHP.find(route)
    check(start>=0,'missing '+route)
    nxt=PHP.find('register_rest_route(',start+1)
    window=PHP[start:nxt if nxt>=0 else len(PHP)]
    check('cloud_permission' in window,'authenticated route lost cloud_permission: '+route)
    check("'permission_callback' => '__return_true'" not in window,'authenticated route became public: '+route)
check("'/security-privacy-audit-ii-contract'" in PHP and "'methods' => 'GET'" in PHP,'Audit II contract missing')
# Every anonymous Workspace REST route must remain a GET metadata/contract endpoint.
route_matches=list(re.finditer(r"register_rest_route\('sc-workspace/v1', '([^']+)'",PHP))
for i,m in enumerate(route_matches):
    route=m.group(1); end=route_matches[i+1].start() if i+1<len(route_matches) else len(PHP); block=PHP[m.start():end]
    if "'permission_callback' => '__return_true'" in block:
        check(route=='/health' or route.endswith('-contract'),'unexpected anonymous data route: '+route)
        check("'methods' => 'GET'" in block,'anonymous contract route is not GET-only: '+route)
    if route.startswith('/cloud-'):
        check('cloud_permission' in block,'cloud route lacks authenticated permission: '+route)
# Cookie-authenticated cloud writes must carry a WordPress REST nonce and same-origin credentials.
current_shell=(PLUGIN/'assets/js/workspace-v0.79.0.js').read_text(errors='ignore')
check("'X-WP-Nonce': String(IDENTITY_CONFIG.restNonce)" in current_shell,'cloud request nonce header missing')
check("credentials: 'same-origin'" in current_shell,'cloud request same-origin credential policy missing')
# Current executable JS only: all unversioned helpers plus the current cumulative shell.
assets=PLUGIN/'assets/js'
js=[p for p in assets.glob('sc-workspace-*.js')]+[assets/'workspace-v0.79.0.js']
for p in js:
    t=p.read_text(errors='ignore')
    for pattern,label in [(r'\beval\s*\(','eval'),(r'new\s+Function\s*\(','new Function'),(r'document\.write\s*\(','document.write')]:
        if re.search(pattern,t): fail(f'{label} found in {p.name}')
# Obvious embedded secrets/private keys in current executable sources/PHP.
secret_patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,}["\']',r'(?i)authorization\s*[:=]\s*["\']Bearer\s+[A-Za-z0-9._\-]{12,}']
for p in js+[PLUGIN/'sustainable-catalyst-workspace.php',PLUGIN/'includes/class-sc-workspace.php']:
    t=p.read_text(errors='ignore')
    for pattern in secret_patterns:
        if re.search(pattern,t): fail('secret-like literal found in '+p.name)
# Current network behavior is same-origin cloud REST only. Any new fetch requires explicit audit.
fetches=[]
for p in js:
    t=p.read_text(errors='ignore')
    if re.search(r'\bfetch\s*\(',t): fetches.append((p.name,t))
check(len(fetches)==1 and fetches[0][0]=='workspace-v0.79.0.js','unexpected fetch-bearing current asset')
current=fetches[0][1]
check("fetch(cloudRestUrl(path), { credentials: 'same-origin'" in current,'cloud fetch is not same-origin credential-scoped')
# External executable endpoints are not allowed in fetch/XHR/WebSocket/EventSource strings.
for p in js:
    t=p.read_text(errors='ignore')
    for m in re.finditer(r'(fetch|XMLHttpRequest|WebSocket|EventSource)[^\n]{0,180}https?://',t): fail('external network literal near '+p.name)
# target=_blank must use noopener in PHP surfaces.
for p in PLUGIN.rglob('*.php'):
    for line in p.read_text(errors='ignore').splitlines():
        if 'target="_blank"' in line and 'rel="noopener' not in line: fail('target=_blank without noopener in '+p.name)
check('Version: 0.79.0' in MAIN,'plugin version mismatch')
print('PASS - v0.79.0 inherited Security & Privacy Audit II source gates')
