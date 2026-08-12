from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
VIEWPORTS=[(1440,1000),(1024,800),(834,1112),(768,1024),(430,900),(390,844)]
fixture=(ROOT/'tests/fixtures/v072_workflow_guidance_fixture.html').read_text()
css=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.73.0.css').read_text()
fixture=fixture.replace('<link rel="stylesheet" href="../../wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.73.0.css">',f'<style>{css}</style>')
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width,height in VIEWPORTS:
  page=browser.new_page(viewport={'width':width,'height':height}); page.set_content(fixture,wait_until='load')
  r=page.evaluate('''() => {const a=document.querySelector('.scw-workflow-guidance').getBoundingClientRect(),c=document.querySelector('.scw-workflow-guidance-copy').getBoundingClientRect(),b=document.querySelector('.scw-workflow-guidance .scw-button').getBoundingClientRect(),p=document.querySelector('.scw-project-research-guidance').getBoundingClientRect(),pb=document.querySelector('.scw-project-research-guidance .scw-button').getBoundingClientRect();return {body:document.documentElement.scrollWidth,aW:a.width,copyW:c.width,buttonW:b.width,buttonH:b.height,pW:p.width,pButtonH:pb.height};}''')
  if r['body']>width+2: raise SystemExit(f'page overflow {width}x{height}: {r}')
  if r['copyW']<200: raise SystemExit(f'guidance copy collapsed {width}x{height}: {r}')
  if width<=760 and (r['buttonH']<43.5 or r['pButtonH']<43.5): raise SystemExit(f'narrow guidance action too short {width}x{height}: {r}')
  if r['aW']<min(width*.70,300) or r['pW']<min(width*.70,300): raise SystemExit(f'guidance panel too narrow {width}x{height}: {r}')
  print(f"PASS {width}x{height}: guidance={r['aW']:.1f}px copy={r['copyW']:.1f}px action={r['buttonH']:.1f}px body={r['body']}")
  page.close()
 browser.close()
