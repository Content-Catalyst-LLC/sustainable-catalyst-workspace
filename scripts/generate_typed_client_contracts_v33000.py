#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLIENT=ROOT/'frontend/typed-client/src/00-generated-contracts.ts'
WP=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-typed-client-v33000.js'
def build():
    source=CLIENT.read_text()
    marker='export const SCW_TYPED_ENDPOINTS = '
    start=source.index(marker)+len(marker)
    end=source.index(' as const;',start)
    eps=json.loads(source[start:end])
    ts="export const SCW_TYPED_CONTRACT_VERSION = '3.30.0';\nexport const SCW_TYPED_ENDPOINTS = "+json.dumps(eps,indent=2)+" as const;\nexport type SCWTypedEndpointKey = keyof typeof SCW_TYPED_ENDPOINTS;\n"
    js="window.SCW_TYPED_CONTRACT_VERSION='3.30.0';\nwindow.SCW_TYPED_ENDPOINTS="+json.dumps(eps,separators=(',',':'))+";\n"
    return eps,ts,js
p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); a=p.parse_args()
eps,ts,js=build()
if a.check:
    assert CLIENT.read_text()==ts,'typed client TS is stale'
    assert WP.read_text()==js,'WordPress typed client is stale'
    print('PASS: Workspace v3.30.0 typed client contract check endpoints=%d'%len(eps))
else:
    CLIENT.write_text(ts); WP.write_text(js)
    print('PASS: Workspace v3.30.0 typed client generated endpoints=%d'%len(eps))
