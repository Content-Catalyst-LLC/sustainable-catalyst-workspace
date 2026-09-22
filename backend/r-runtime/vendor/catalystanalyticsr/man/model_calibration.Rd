\name{model_calibration}
\alias{calibration_spec}
\alias{calibrate_model}
\alias{calibration_summary}
\alias{plot_calibration_fit}
\alias{print.catalyst_calibration}
\title{Governed model calibration}
\usage{
calibration_spec(parameters, objective = c("weighted_rmse", "rmse", "mae", "sse"),
  method = c("L-BFGS-B", "Nelder-Mead"), maxit = 250L,
  tolerance = 1e-08, id = "model-calibration", title = "Model calibration",
  metadata = list())
calibrate_model(scenario, observations, spec, include_phase_plane = FALSE,
  include_sensitivity = FALSE)
calibration_summary(x)
plot_calibration_fit(x)
\method{print}{catalyst_calibration}(x, ...)
}
\arguments{
\item{parameters}{Named calibration parameter definitions.}
\item{objective}{Calibration objective.}
\item{method}{Optimization method passed to \code{stats::optim}.}
\item{maxit}{Maximum optimizer iterations.}
\item{tolerance}{Recorded convergence tolerance.}
\item{id}{Stable calibration identifier.}
\item{title}{Human-readable title.}
\item{metadata}{Additional metadata.}
\item{scenario}{Canonical scenario template.}
\item{observations}{Observation data frame with time, metric, observed, and optional weight and split columns.}
\item{spec}{A calibration specification.}
\item{include_phase_plane}{Whether to compute the final phase plane.}
\item{include_sensitivity}{Whether to compute final local sensitivity.}
\item{x}{A calibration object.}
\item{...}{Additional method arguments.}
}
\value{A governed calibration object, summary, or plot.}
\description{Defines bounded parameter estimation, executes calibration through a registered Catalyst model, and preserves fitted values, optimizer evidence, and parameter provenance.}
