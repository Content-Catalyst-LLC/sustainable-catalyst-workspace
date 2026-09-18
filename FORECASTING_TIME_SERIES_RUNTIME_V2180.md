# Workspace v2.18.0 — Forecasting & Time-Series Runtime

v2.18 adds a dedicated internal forecasting runtime with eight bounded operations: naive, seasonal-naive, linear trend, exponential smoothing, Holt-Winters, ARIMA, rolling-origin backtesting, and direct forecast evaluation. Forecast outputs retain dataset fingerprints, model parameters, horizon, frequency, fit/evaluation metrics, interval bands, result artifacts, and durable receipts. Arbitrary code execution is not accepted.
