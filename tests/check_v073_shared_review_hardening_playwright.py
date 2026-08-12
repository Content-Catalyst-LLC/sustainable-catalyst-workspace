from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
VIEWPORTS=[(1440,1000),(1024,800),(834,1112),(768,1024),(430,900),(390,844)]
fixture=(ROOT/'tests/fixtures/v073_shared_review_hardening_fixture.html').read_text()
css=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.73.0.css').read_text()
fixture=fixture.replace('<link rel="stylesheet" href="../../wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.73.0.css">',f'<style>{css}</style>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in VIEWPORTS:
        page=browser.new_page(viewport={'width':width,'height':height})
        page.set_content(fixture,wait_until='load')
        r=page.evaluate('''() => {
          const panel=document.querySelector('.scw-shared-review-panel').getBoundingClientRect();
          const integrity=document.querySelector('.scw-review-integrity').getBoundingClientRect();
          const ack=document.querySelector('.scw-review-owner-ack').getBoundingClientRect();
          const buttons=[...document.querySelectorAll('.scw-handoff-actions .scw-button')].map(x=>x.getBoundingClientRect());
          return {body:document.documentElement.scrollWidth,panelW:panel.width,integrityW:integrity.width,ackW:ack.width,minButtonH:Math.min(...buttons.map(x=>x.height)),buttonCount:buttons.length};
        }''')
        if r['body']>width+2: raise SystemExit(f'page overflow {width}x{height}: {r}')
        if r['panelW']<min(width*.70,300): raise SystemExit(f'review panel too narrow {width}x{height}: {r}')
        if r['integrityW']<220 or r['ackW']<220: raise SystemExit(f'review integrity content collapsed {width}x{height}: {r}')
        if r['buttonCount']!=2: raise SystemExit(f'missing review actions {width}x{height}: {r}')
        if width<=760 and r['minButtonH']<43.5: raise SystemExit(f'narrow review action too short {width}x{height}: {r}')
        print(f"PASS {width}x{height}: panel={r['panelW']:.1f}px integrity={r['integrityW']:.1f}px ack={r['ackW']:.1f}px action={r['minButtonH']:.1f}px body={r['body']}")
        page.close()
    browser.close()
