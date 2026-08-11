from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
VIEWPORTS=[1600,1440,1280,1024,768,390]
fixture=(ROOT/'tests/fixtures/v0641_layout_fixture.html').read_text()
css=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
fixture=fixture.replace('<link rel="stylesheet" href="../../wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css">', f'<style>{css}</style>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in VIEWPORTS:
        page=browser.new_page(viewport={'width':width,'height':1000})
        page.set_content(fixture, wait_until='load')
        r=page.evaluate('''() => {
          const box=s=>{const e=document.querySelector(s),r=e.getBoundingClientRect();return {w:r.width,sw:e.scrollWidth}};
          return {body:document.documentElement.scrollWidth,hero:box('.scw-platform-hero-grid'),copy:box('.scw-platform-hero-copy'),preview:box('.scw-platform-preview'),research:box('.scw-research-overview'),researchCopy:box('.scw-research-overview>div:first-child'),researchGrid:box('.scw-research-overview-grid')};
        }''')
        if r['body']>width+2: raise SystemExit(f'overflow {width}: {r}')
        if width>980 and r['copy']['w']<300: raise SystemExit(f'hero copy collapsed {width}: {r}')
        if width<=980 and r['copy']['w']<width*0.72: raise SystemExit(f'hero mobile column too narrow {width}: {r}')
        if width>900 and r['researchCopy']['w']<280: raise SystemExit(f'research copy collapsed {width}: {r}')
        if width<=900 and r['researchCopy']['w']<width*0.60: raise SystemExit(f'research mobile column too narrow {width}: {r}')
        print(f"PASS viewport {width}: hero-copy={r['copy']['w']:.1f}px research-copy={r['researchCopy']['w']:.1f}px body={r['body']}")
        page.close()
    browser.close()
