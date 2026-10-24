"""Reproduce verified Wexford heat-map inputs without uploading raw research.

All archives are owner-supplied, hash-pinned and extracted into a NEW private
output directory. No network, production access, manuscript overwrite or GIS
redistribution. Requires the separately pinned Lab source checkout.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

PINS={
 'emp075':'708949c511eef5b70023048a9601ce43a0858295e7eb08c919ed9c4f722f4e08',
 'emp03g4':'c89035bdd7c5101c7ce417e1c0bf17cee04c6463eef4d3c535ed404f6fe291dd',
 'emp071':'24177b690e909e6bf3c557a474ded0faa2b6e391fe55b0a19db332c940cf63b9'}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser()
 for name in PINS:p.add_argument('--'+name,required=True,type=Path)
 p.add_argument('--lab-source-app',required=True,type=Path)
 p.add_argument('--output-dir',required=True,type=Path)
 args=p.parse_args();out=args.output_dir.resolve()
 if out.exists():raise RuntimeError('Use a new output directory; existing research is never overwritten.')
 for name,expected in PINS.items():
  if digest(getattr(args,name))!=expected:raise RuntimeError('Archive hash mismatch: '+name)
 lab=args.lab_source_app.resolve()
 if not (lab/'visualization.py').is_file():raise RuntimeError('Pinned Lab backend/app directory required.')
 out.mkdir(mode=0o700,parents=True);root=out/'research';root.mkdir(mode=0o700)
 inventory={}
 for name in PINS:
  target=root/name;target.mkdir(mode=0o700)
  with zipfile.ZipFile(getattr(args,name)) as z:
   if z.testzip():raise RuntimeError('Archive CRC failure: '+name)
   if sum(i.file_size for i in z.infolist())>100_000_000:raise RuntimeError('Unexpected research archive size.')
   for item in z.infolist():
    path=(target/item.filename).resolve()
    if target not in path.parents or (item.external_attr>>16)&0o170000==0o120000:
     raise RuntimeError('Unsafe research archive member.')
    if item.is_dir():path.mkdir(mode=0o700,parents=True,exist_ok=True);continue
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True);path.write_bytes(z.read(item));path.chmod(0o600)
  checked=[];absent=[]
  if name=='emp075':
   rows=list(csv.DictReader((target/'SHA256_MANIFEST.csv').open()))
   for row in rows:
    file=target/row['relative_path']
    if file.stat().st_size!=int(row['bytes']) or digest(file)!=row['sha256']:raise RuntimeError('Manifest mismatch')
    checked.append(row['relative_path'])
  elif name=='emp03g4':
   for file,expected in json.loads((target/'SHA256_MANIFEST.json').read_text()).items():
    if digest(target/file)!=expected:raise RuntimeError('Spatial manifest mismatch')
    checked.append(file)
  else:
   for row in csv.DictReader((target/'SHA256_MANIFEST.csv').open()):
    file=target/row['file']
    if not file.exists():absent.append(row['file']);continue
    if digest(file)!=row['sha256']:raise RuntimeError('EMP071 manifest mismatch')
    checked.append(row['file'])
   if absent!=['figures/EMP071_screening_context_MAP_INTERNAL.png']:raise RuntimeError('Unexpected missing source file')
  inventory[name]={'archive_sha256':PINS[name],'verified_files':checked,'excluded_manifest_entries':absent}
 stat=root/'statistical-rerun';stat.mkdir(mode=0o700)
 original=root/'emp075/02_REPRODUCIBILITY/analysis.py'
 if digest(original)!='006d8e12fb1f48c8b78dfde54e970ac3837e033806b4b693c40c25e98d6f0220':raise RuntimeError('Unreviewed statistical code')
 shutil.copy2(original,stat/'analysis.py')
 source=root/'emp071/EMP071_raw_spatial.py'
 if digest(source)!='898bac9b3d4aa7619c588f74548a6090b94c5760b32fdff863ff0df5b41bf58a':raise RuntimeError('Unreviewed spatial code')
 fragment=out/'spatial-stage.py';fragment.write_text(source.read_text().split('# figure one:')[0])
 (root/'spatial-rerun').mkdir(mode=0o700)
 env={**os.environ,'MPLCONFIGDIR':str(out/'matplotlib'),'EMP07_INPUT_DIR':str(root/'emp03g4'),
      'EMP07_OUTPUT_DIR':str(root/'spatial-rerun'),'RS_RESEARCH_WORKDIR':str(root),
      'RS_LAB_SOURCE_APP':str(lab),'RS_REPRO_OUTPUT':str(out)}
 with (out/'execution.log').open('w') as log:
  for script in [stat/'analysis.py',fragment,Path(__file__).with_name('wexford_heatmap_derivation.py')]:
   subprocess.run([sys.executable,str(script.resolve())],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
 (out/'source-verification.json').write_text(json.dumps(inventory,indent=2))
 print('PASS: verified source manifests, spatial/statistical table parity and 36 detectability cells. Outputs: '+str(out))

if __name__=='__main__':main()
