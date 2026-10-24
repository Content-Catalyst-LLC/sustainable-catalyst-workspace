# Private research reproduction

Use Python 3.12 with the scientific environment from the original research plus GeoPandas, Shapely, pyogrio, pyproj, python-docx, nbformat and nbclient. This run used NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, Matplotlib 3.11.2, GeoPandas 1.2.0, Shapely 2.2.0, pyogrio 0.13.0 and pyproj 3.8.0. These are local execution records, not a full dependency/security certification.

Check out Lab commit `0acccadd611c2714c0f464b91882d71cc6db42cc` separately. Obtain the three owner-supplied archives; no data download, raw GIS commit or redistribution is performed by this script.

```sh
python scripts/reproduce_wexford_heatmaps.py \
 --emp075 /private/path/Wexford_EMP075_Final_Submission_Certification.zip \
 --emp03g4 /private/path/Wexford_EMP03G4_Integrated_Baseline.zip \
 --emp071 /private/path/Wexford_EMP07_1_2_Original_Research_Design.zip \
 --lab-source-app /private/path/pinned-lab/backend/app \
 --output-dir /private/path/new-heatmap-reproduction
```

The runner validates pinned archive SHA256, CRC and internal manifests; copies source scripts into a new private working directory; executes the reviewed statistical script and spatial computation stage; checks table parity and every minimum-replication cell; and emits native heat-map JSON plus evidence. The statistical grid uses real EMP073 code with **assumed** effects and SDs, not field estimates. The environmental grid preserves 2025 source centers without interpolation. The intentionally excluded internal-map manifest entry remains documented. National raw source preprocessing, source licensing and empirical field validity remain outside this proof.

Stage only the reviewed generated JSON artifacts in a disposable Workspace project using the existing private file API. Declare units, scientific status and source citations in the report, then save immutable revisions and export. Do not stage or publish raw source archives solely to update a tracker. The bridge does not execute this reproduction runner from a browser request.
