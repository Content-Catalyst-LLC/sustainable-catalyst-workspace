from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]; V=[(1440,1000),(1024,800),(834,1112),(768,1024),(430,900),(390,844)]
f=(R/'tests/fixtures/v078_accessibility_performance_final_audit_fixture.html').read_text();css=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.78.0.css').read_text();f=f.replace('<link rel="stylesheet" href="../../wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.78.0.css">',f'<style>{css}</style>')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w,h in V:
  page=b.new_page(viewport={'width':w,'height':h});page.set_content(f)
  x=page.evaluate("""() => {const panel=document.querySelector('.scw-final-audit').getBoundingClientRect(),sections=[...document.querySelectorAll('.scw-final-audit-grid>section')].map(x=>x.getBoundingClientRect()),buttons=[...document.querySelectorAll('.scw-final-audit .scw-button')].map(x=>x.getBoundingClientRect());return {body:document.documentElement.scrollWidth,panel:panel.width,minSection:Math.min(...sections.map(x=>x.width)),minH:Math.min(...buttons.map(x=>x.height))}}""")
  if x['body']>w+2: raise SystemExit(f'overflow {w}: {x}')
  if x['panel']<min(w*.7,300) or x['minSection']<min(w*.4,250): raise SystemExit(f'collapse {w}: {x}')
  if w<=520 and x['minH']<43.5: raise SystemExit(f'touch {w}: {x}')
  print(f"PASS {w}x{h}: panel={x['panel']:.1f}px section={x['minSection']:.1f}px action={x['minH']:.1f}px body={x['body']}")
  page.close()
 b.close()
