#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in [ROOT/'backend/migrations/018_forecasting_time_series_runtime.sql',ROOT/'backend/forecast-runtime/service.py',ROOT/'backend/deploy_workspace_backend_v2_18_0_vps.sh',ROOT/'schemas/sc-workspace-forecasting-runtime-v1.schema.json',ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.18.0.css',ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.18.0.js']:
    assert p.exists(), p
service=(ROOT/'backend/forecast-runtime/service.py').read_text()
for op in ['naive','seasonal-naive','linear-trend','exponential-smoothing','holt-winters','arima','backtest','evaluate']: assert f'workspace.forecast.{op}' in service
main=(ROOT/'backend/app/main.py').read_text(); assert 'forecastingTimeSeriesRuntime' in main and 'forecastPredictionIntervals' in main
plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); assert 'Version: 2.18.0' in plugin
print('PASS — Workspace v2.18.0 Forecasting & Time-Series Runtime validated')
