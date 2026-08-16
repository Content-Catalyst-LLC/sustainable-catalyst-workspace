from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
VIEWPORTS=[1440,1024,768,390]
fixture=(ROOT/'tests/fixtures/v2_0_4_visual_regression_fixture.html').read_text()
receipts=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in VIEWPORTS:
        page=browser.new_page(viewport={'width':width,'height':1000})
        page.set_content(fixture,wait_until='load')
        data=page.evaluate('''() => {
          const root=document.querySelector('.scw-shell.scw-root');
          const lanes=document.querySelector('.scw-project-cockpit-lanes');
          const card=document.querySelector('.scw-work-mode-card');
          const copy=card.querySelector('.scw-work-mode-card-copy');
          const primary=document.querySelector('.scw-button-primary');
          const buttons=[...document.querySelectorAll('.scw-button')];
          const secondary=buttons.find(x=>x.textContent==='Secondary action');
          const disabled=buttons.find(x=>x.textContent==='Disabled');
          const connected=document.querySelector('.scw-connected-knowledge .scw-collab-contract-actions');
          const cs=e=>getComputedStyle(e);
          const cols=cs(lanes).gridTemplateColumns.split(' ').filter(Boolean).length;
          return {
            viewport:innerWidth,
            rootClass:root.className,
            rootClientWidth:root.clientWidth,
            rootScrollWidth:root.scrollWidth,
            documentScrollWidth:document.documentElement.scrollWidth,
            lanesDisplay:cs(lanes).display,
            columns:cols,
            cardDisplay:cs(card).display,
            cardBackground:cs(card).backgroundColor,
            cardColor:cs(card).color,
            cardMinHeight:parseFloat(cs(card).minHeight)||0,
            copyDisplay:cs(copy).display,
            primaryBackground:cs(primary).backgroundColor,
            primaryColor:cs(primary).color,
            secondaryBackground:cs(secondary).backgroundColor,
            secondaryColor:cs(secondary).color,
            secondaryHeight:secondary.getBoundingClientRect().height,
            disabledBackground:cs(disabled).backgroundColor,
            connectedDisplay:cs(connected).display,
            connectedClientWidth:connected.clientWidth,
            connectedScrollWidth:connected.scrollWidth
          };
        }''')
        expected_cols=1 if width<=760 else 2
        if data['rootClass']!='scw-shell scw-root': raise SystemExit(f'root scope {width}: {data}')
        if data['lanesDisplay']!='grid' or data['cardDisplay']!='grid': raise SystemExit(f'grid lost {width}: {data}')
        if data['columns']!=expected_cols: raise SystemExit(f'columns {width}: {data}')
        if data['cardBackground']=='rgb(196, 0, 0)': raise SystemExit(f'theme leaked into cards {width}: {data}')
        if data['secondaryBackground']!='rgb(255, 255, 255)': raise SystemExit(f'secondary theme leak {width}: {data}')
        if data['primaryBackground'] not in ('rgb(240, 0, 0)','rgb(255, 0, 0)'): raise SystemExit(f'primary hierarchy {width}: {data}')
        if data['disabledBackground']!='rgb(241, 241, 237)': raise SystemExit(f'disabled state {width}: {data}')
        if data['connectedDisplay']!='grid': raise SystemExit(f'connected grid {width}: {data}')
        if data['connectedScrollWidth']>data['connectedClientWidth']+1: raise SystemExit(f'connected overflow {width}: {data}')
        if data['rootScrollWidth']>data['rootClientWidth']+1: raise SystemExit(f'root overflow {width}: {data}')
        if data['documentScrollWidth']>width+2: raise SystemExit(f'document overflow {width}: {data}')
        min_h=44 if width<=760 else 40
        if data['secondaryHeight']<min_h: raise SystemExit(f'control target {width}: {data}')
        receipts.append(data)
        print(f"PASS viewport {width}: cols={data['columns']} secondary={data['secondaryHeight']:.1f}px body={data['documentScrollWidth']}")
        page.close()
    browser.close()
out=ROOT/'RENDERED_VISUAL_REGRESSION_RECEIPT_2.0.4.json'
out.write_text(json.dumps({'release':'2.0.4','hostileThemeFixture':True,'viewports':VIEWPORTS,'matrix':receipts,'result':'pass'},indent=2)+'\n')
print('PASS - v2.0.4 rendered visual regression matrix')
