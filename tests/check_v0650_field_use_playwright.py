from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
VIEWPORTS=[(1600,1000),(1440,1000),(1280,900),(1024,800),(834,1112),(768,1024),(430,900),(390,844),(844,390)]
fixture=(ROOT/'tests/fixtures/v0650_field_use_fixture.html').read_text()
css=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.65.0.css').read_text()
fixture=fixture.replace('<link rel="stylesheet" href="../../wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.65.0.css">',f'<style>{css}</style>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in VIEWPORTS:
        page=browser.new_page(viewport={'width':width,'height':height})
        page.set_content(fixture,wait_until='load')
        r=page.evaluate('''() => {const q=s=>document.querySelector(s),box=s=>{const e=q(s),r=e.getBoundingClientRect();return {w:r.width,h:r.height,sw:e.scrollWidth,sh:e.scrollHeight}};return {body:document.documentElement.scrollWidth,hero:box('.scw-platform-hero-copy'),preview:box('.scw-platform-preview'),research:box('.scw-research-overview>div:first-child'),table:box('.wide-table'),button:box('.scw-experience-action'),dialog:box('.scw-experience-dialog-panel')};}''')
        if r['body']>width+2: raise SystemExit(f'page overflow {width}x{height}: {r}')
        if width>980 and r['hero']['w']<300: raise SystemExit(f'hero collapsed {width}x{height}: {r}')
        if width<=980 and r['hero']['w']<width*.70: raise SystemExit(f'hero narrow {width}x{height}: {r}')
        if width<=900 and r['research']['w']<width*.55: raise SystemExit(f'research narrow {width}x{height}: {r}')
        if width<=620 and r['button']['h']<43.5: raise SystemExit(f'touch target too short {width}x{height}: {r}')
        if width<=760 and not (r['table']['sw']>r['table']['w'] and r['body']<=width+2): raise SystemExit(f'table not bounded {width}x{height}: {r}')
        if height<700 and r['dialog']['h']>height-20: raise SystemExit(f'short dialog overflow {width}x{height}: {r}')
        print(f"PASS {width}x{height}: hero={r['hero']['w']:.1f}px research={r['research']['w']:.1f}px button={r['button']['h']:.1f}px body={r['body']}")
        page.close()
    browser.close()
