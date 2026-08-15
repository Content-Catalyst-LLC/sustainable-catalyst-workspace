from pathlib import Path
import re
from release_lineage import current_release
R=Path(__file__).resolve().parents[1]
PLUGIN=R/'wordpress/sustainable-catalyst-workspace'; CUR=current_release(R)
PHP=(PLUGIN/'includes/class-sc-workspace.php').read_text(); MAIN=CUR.plugin_main.read_text()
def fail(msg): raise SystemExit('FAIL - Security & Privacy Audit II source gate: '+msg)
def check(cond,msg):
    if not cond: fail(msg)
for route in ["'/cloud-projects'","'/cloud-projects/(?P<project_id>","'/cloud-notebooks'","'/cloud-notebooks/(?P<notebook_id>"]:
    start=PHP.find(route); check(start>=0,'missing '+route); nxt=PHP.find('register_rest_route(',start+1); window=PHP[start:nxt if nxt>=0 else len(PHP)]
    check('cloud_permission' in window,'authenticated route lost cloud_permission: '+route); check("'permission_callback' => '__return_true'" not in window,'authenticated route became public: '+route)
check("'/security-privacy-audit-ii-contract'" in PHP and "'methods' => 'GET'" in PHP,'Audit II contract missing')
route_matches=list(re.finditer(r"register_rest_route\('sc-workspace/v1', '([^']+)'",PHP))
for i,m in enumerate(route_matches):
    route=m.group(1); end=route_matches[i+1].start() if i+1<len(route_matches) else len(PHP); block=PHP[m.start():end]
    if "'permission_callback' => '__return_true'" in block:
        check(route=='/health' or route.endswith('-contract'),'unexpected anonymous data route: '+route); check("'methods' => 'GET'" in block,'anonymous contract route is not GET-only: '+route)
    if route.startswith('/cloud-'): check('cloud_permission' in block,'cloud route lacks authenticated permission: '+route)
current_shell=CUR.script_path.read_text(errors='ignore')
check("'X-WP-Nonce': String(IDENTITY_CONFIG.restNonce)" in current_shell,'cloud request nonce header missing'); check("credentials: 'same-origin'" in current_shell,'cloud request same-origin credential policy missing')
assets=PLUGIN/'assets/js'; js=[p for p in assets.glob('sc-workspace-*.js')]+[CUR.script_path]
for p in js:
    t=p.read_text(errors='ignore')
    for pattern,label in [(r'\beval\s*\(','eval'),(r'new\s+Function\s*\(','new Function'),(r'document\.write\s*\(','document.write')]:
        if re.search(pattern,t): fail(f'{label} found in {p.name}')
secret_patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,}["\']',r'(?i)authorization\s*[:=]\s*["\']Bearer\s+[A-Za-z0-9._\-]{12,}']
for p in js+[CUR.plugin_main,PLUGIN/'includes/class-sc-workspace.php']:
    t=p.read_text(errors='ignore')
    for pattern in secret_patterns:
        if re.search(pattern,t): fail('secret-like literal found in '+p.name)
fetches=[]
for p in js:
    t=p.read_text(errors='ignore')
    if re.search(r'\bfetch\s*\(',t): fetches.append((p.name,t))
check(len(fetches)==1 and fetches[0][0]==CUR.script_name,'unexpected fetch-bearing current asset')
check("fetch(cloudRestUrl(path), { credentials: 'same-origin'" in fetches[0][1],'cloud fetch is not same-origin credential-scoped')
for p in js:
    t=p.read_text(errors='ignore')
    if re.search(r'(fetch|XMLHttpRequest|WebSocket|EventSource)[^\n]{0,180}https?://',t): fail('external network literal near '+p.name)
for p in PLUGIN.rglob('*.php'):
    for line in p.read_text(errors='ignore').splitlines():
        if 'target="_blank"' in line and 'rel="noopener' not in line: fail('target=_blank without noopener in '+p.name)
check(f'Version: {CUR.version}' in MAIN,'plugin version mismatch')
print(f'PASS - inherited Security & Privacy Audit II source gates under current v{CUR.version}')
