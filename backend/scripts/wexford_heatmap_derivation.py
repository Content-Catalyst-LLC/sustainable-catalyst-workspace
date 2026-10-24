"""Private Wexford reproduction from checked source archives; no demo values."""
from pathlib import Path
import csv,hashlib,importlib,importlib.util,json,sys,types,os
import numpy as np,pandas as pd
root=Path(os.environ['RS_RESEARCH_WORKDIR']);stats=root/'statistical-rerun';spatial=root/'spatial-rerun';baseline=root/'emp03g4'
checks={}
for name in ['sample_size_sensitivity.csv','minimum_detectable_effects.csv','pseudoreplication_design_effect.csv']:
 a=pd.read_csv(root/'emp075/02_REPRODUCIBILITY'/name);b=pd.read_csv(stats/name)
 pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-12,atol=1e-12);checks[name]='numeric parity at 1e-12'
for name in ['EMP071_strata_grid_summary.csv','EMP071_mapped_soil_setting_area.csv','EMP072_verification_design_matrix.csv']:
 a=pd.read_csv(root/'emp071'/name);b=pd.read_csv(spatial/name)
 pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-12,atol=1e-12);checks[name]='parity with original EMP07.1 outputs'
# Authorized original statistical code, already inspected; all writes remain in rerun directory.
spec=importlib.util.spec_from_file_location('emp073_verified',stats/'analysis.py');stat=importlib.util.module_from_spec(spec);spec.loader.exec_module(stat)
old=Path(os.environ['RS_LAB_SOURCE_APP'])
pkg=types.ModuleType('lab_verified');pkg.__path__=[str(old)];sys.modules['lab_verified']=pkg
lab=importlib.import_module('lab_verified.visualization')
# Recompute a finer regular sensitivity grid using exactly the source's noncentral-t power functions.
effects=[round(x,2) for x in np.arange(.10,.501,.05)];sds=[.15,.30,.45,.60]
grid=[[stat.min_n(lambda n,d=effect,s=sd:stat.power_two_arm(n,d,s)) for effect in effects] for sd in sds]
assert grid[1][3]==24
for yi,sd in enumerate(sds):
 for xi,d in enumerate(effects):
  n=grid[yi][xi];assert stat.power_two_arm(n,d,sd)>=.8
  assert n==3 or stat.power_two_arm(n-1,d,sd)<.8
power=lab.build_spec({'method':'EMP073.power_two_arm.noncentral_t','outputs':{'xValues':effects,'yValues':sds,'zMatrix':grid},
 'visualization':{'type':'heatmap','title':'Detectability | independent plots required per arm',
 'xLabel':'Assumed treatment difference (t CO2e/ha)','yLabel':'Assumed plot SD (t CO2e/ha)',
 'zLabel':'Independent plots per arm','description':'Recomputed from EMP073 analysis.py, alpha 0.05, two-sided, power 0.80; effects and SDs are sensitivity assumptions, not measured Wexford parameters. Minimum search begins at n=3, exactly as the source.'}})
cl=pd.read_csv(baseline/'wexford_rainfall_temperature_2025.csv')
assert len(cl)==2363
xs=sorted(cl.east.unique().tolist());ys=sorted(cl.north.unique().tolist())
assert np.allclose(np.diff(xs),1000) and np.allclose(np.diff(ys),1000)
xidx={x:i for i,x in enumerate(xs)};yidx={y:i for i,y in enumerate(ys)}
cells=[{'x':float(r.east),'y':float(r.north),'z':float(r.annual_mm),'xIndex':xidx[r.east],'yIndex':yidx[r.north]} for r in cl.itertuples()]
# The existing Lab grid grammar is used without filling missing county cells.
# No scientific interpolation is performed or attributed to a live module.
env={'schema':'sc-lab-scientific-visualization/1.0','version':lab.VERSION,'kind':'heatmap','visualizationType':'heatmap',
 'method':'EMP071.spatial_context.source_grid','title':'Wexford environmental heterogeneity | 2025 rainfall',
 'description':'Source grid values from the manifest-verified EMP03G4 input, checked with the EMP071 spatial pipeline. Irish Grid TM65 EPSG:29903; 1 km centers selected by the source study boundary. Empty cells masked; no interpolation. Soil contexts are predictive-map classes, not verified field sites. 2025 is one year, not a climate normal.',
 'xLabel':'Easting (m), EPSG:29903','yLabel':'Northing (m), EPSG:29903',
 'spatialReference':{'crs':'EPSG:29903','cell_size_m':1000,'coverage':'source-selected climate centers; boundary provenance/rights conditional'},
 'xValues':xs,'yValues':ys,'cells':cells,
 'domain':{'x':[min(xs),max(xs)],'y':[min(ys),max(ys)],'z':[min(c['z'] for c in cells),max(c['z'] for c in cells)]}}
out=Path(os.environ['RS_REPRO_OUTPUT'])
for name,obj in [('verified-environmental-heatmap',env),('verified-detectability-heatmap',power)]:
 (out/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False))
checks['detectability_grid']={'cells':len(effects)*len(sds),'central_n':grid[1][3],'minimum_and_power_checks':'all cells passed','status':'design sensitivity, not empirical variance'}
checks['environmental_grid']={'cells':len(cells),'rainfall_mean_mm':float(cl.annual_mm.mean()),'temperature_mean_c':float(cl.mean_temp_2025_c.mean()),'status':'source-grid descriptive values; no field weathering inference'}
checks['source_files']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [baseline/'wexford_rainfall_temperature_2025.csv',root/'emp075/02_REPRODUCIBILITY/analysis.py',root/'emp071/EMP071_raw_spatial.py']}
(out/'verified-heatmap-reproduction.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
