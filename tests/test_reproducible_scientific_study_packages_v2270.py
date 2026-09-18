from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def test_v227_release_contract():
    m=json.loads((ROOT/'release-manifest-v2.27.0.json').read_text())
    assert m['version']=='2.27.0' and m['deterministicManifest'] is True
    assert (ROOT/'backend/app/study_packages.py').exists()
