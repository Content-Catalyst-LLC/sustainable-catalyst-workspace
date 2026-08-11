from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
VIEWPORTS=[(1440,1000),(1024,800),(834,1112),(768,1024),(430,900),(390,844)]
fixture=(ROOT/'tests/fixtures/v070_beta_iii_fixture.html').read_text()
css=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.70.0.css').read_text()
fixture=fixture.replace('<link rel="stylesheet" href="../../wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.70.0.css">',f'<style>{css}</style>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in VIEWPORTS:
        page=browser.new_page(viewport={'width':width,'height':height})
        page.set_content(fixture,wait_until='load')
        r=page.evaluate('''() => {const cards=[...document.querySelectorAll('.scw-beta-iii-step')];const first=cards[0].getBoundingClientRect();const second=cards[1].getBoundingClientRect();const fourth=cards[3].getBoundingClientRect();const button=document.querySelector('.scw-beta-iii-actions .scw-button').getBoundingClientRect();return {body:document.documentElement.scrollWidth,cards:cards.length,firstW:first.width,firstY:first.y,secondY:second.y,fourthY:fourth.y,buttonH:button.height};}''')
        if r['body']>width+2: raise SystemExit(f'page overflow {width}x{height}: {r}')
        if r['cards']!=9: raise SystemExit(f'journey card count {width}x{height}: {r}')
        if width>980 and abs(r['firstY']-r['secondY'])>2: raise SystemExit(f'expected multi-column desktop grid {width}: {r}')
        if width<=640 and not (r['secondY']>r['firstY'] and r['firstW']>width*.70): raise SystemExit(f'expected single-column narrow grid {width}: {r}')
        if width<=640 and r['buttonH']<43.5: raise SystemExit(f'touch target too short {width}: {r}')
        print(f"PASS {width}x{height}: cards={r['cards']} first={r['firstW']:.1f}px button={r['buttonH']:.1f}px body={r['body']}")
        page.close()
    browser.close()
