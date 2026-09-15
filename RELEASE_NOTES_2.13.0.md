# Workspace v2.13.0 — R Statistical & Econometric Runtime

Workspace v2.13.0 activates R as the first dedicated specialist runtime behind the v2.12 polyglot scientific fabric.

## Added

- independent hardened R runtime container using fixed-operation dispatch
- eight bounded R statistical/econometric operations
- descriptive statistics, t-tests and correlation
- linear and logistic regression
- one-way ANOVA
- bounded ARIMA time-series fitting
- econometric OLS with Durbin–Watson, Breusch–Pagan and Jarque–Bera diagnostics
- internal-only Docker runtime network with no published R host port
- server-generated/preserved R runtime bearer credential
- durable statistical model receipts layered on polyglot execution receipts
- R runtime health/status API and WordPress read-only proxy
- migration 013 for statistical model receipts

## Security

The runtime does not accept arbitrary R code, formulas, package names, shell commands, runtime URLs, or credentials. Browser/client code cannot route around the server-configured R service. The R sidecar executes a fixed runner and retains the v2.12 resource/provenance boundary.

## Lineage

- predecessor: v2.12.0
- rollback target: v2.12.0
