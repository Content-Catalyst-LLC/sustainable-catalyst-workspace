from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
VIEWPORTS=[(1440,1000),(1024,800),(834,1112),(768,1024),(430,900),(390,844)]
fixture=(ROOT/'tests/fixtures/v071_first_run_fixture.html').read_text()
css=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.71.0.css').read_text()
fixture=fixture.replace('<link rel="stylesheet" href="../../wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.71.0.css">',f'<style>{css}</style>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in VIEWPORTS:
        page=browser.new_page(viewport={'width':width,'height':height})
        page.set_content(fixture,wait_until='load')
        r=page.evaluate('''() => {const panel=document.querySelector('.scw-first-run').getBoundingClientRect();const copy=document.querySelector('.scw-first-run-copy').getBoundingClientRect();const form=document.querySelector('.scw-first-run-form').getBoundingClientRect();const title=document.querySelector('.scw-first-run-form input[type="text"]').getBoundingClientRect();const buttons=[...document.querySelectorAll('.scw-first-run-actions .scw-button')].map(x=>x.getBoundingClientRect().height);const cards=[...document.querySelectorAll('.scw-first-run-starters label')].map(x=>x.getBoundingClientRect());return {body:document.documentElement.scrollWidth,panelW:panel.width,copyY:copy.y,formY:form.y,copyW:copy.width,formW:form.width,inputW:title.width,buttons,cards:cards.length};}''')
        if r['body']>width+2: raise SystemExit(f'page overflow {width}x{height}: {r}')
        if r['cards']!=5: raise SystemExit(f'starter count {width}x{height}: {r}')
        if width>900 and abs(r['copyY']-r['formY'])>2: raise SystemExit(f'expected two-column onboarding {width}: {r}')
        if width<=900 and not r['formY']>r['copyY']: raise SystemExit(f'expected stacked onboarding {width}: {r}')
        if r['inputW']>r['formW']+2: raise SystemExit(f'input overflow {width}: {r}')
        if width<=480 and min(r['buttons'])<43.5: raise SystemExit(f'touch target too short {width}: {r}')
        print(f"PASS {width}x{height}: panel={r['panelW']:.1f}px copy={r['copyW']:.1f}px form={r['formW']:.1f}px input={r['inputW']:.1f}px")
        page.close()
    browser.close()
