from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]; V=[(1440,1000),(1024,800),(834,1112),(768,1024),(430,900),(390,844)]
f=(R/'tests/fixtures/v074_api_embed_hardening_fixture.html').read_text(); css=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.74.0.css').read_text(); f=f.replace('<link rel="stylesheet" href="../../wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.74.0.css">',f'<style>{css}</style>')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w,h in V:
  page=b.new_page(viewport={'width':w,'height':h}); page.set_content(f,wait_until='load'); x=page.evaluate('''() => {const s=document.querySelector('.scw-api-safety').getBoundingClientRect(),m=document.querySelector('.scw-api-safety-metrics').getBoundingClientRect(),buttons=[...document.querySelectorAll('.scw-api-actions .scw-button')].map(b=>b.getBoundingClientRect());return {body:document.documentElement.scrollWidth,s:s.width,m:m.width,minH:Math.min(...buttons.map(x=>x.height)),count:buttons.length}}''');
  if x['body']>w+2: raise SystemExit(f'overflow {w}: {x}')
  if x['s']<min(w*.7,300) or x['m']<220: raise SystemExit(f'collapse {w}: {x}')
  if w<=620 and x['minH']<43.5: raise SystemExit(f'touch target {w}: {x}')
  print(f"PASS {w}x{h}: safety={x['s']:.1f}px metrics={x['m']:.1f}px action={x['minH']:.1f}px body={x['body']}")
  page.close()
 b.close()
