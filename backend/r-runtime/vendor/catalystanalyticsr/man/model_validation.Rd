\name{model_validation}
\alias{validation_split}
\alias{model_error_metrics}
\alias{residual_diagnostics}
\alias{validate_model_fit}
\alias{solver_benchmark}
\alias{stability_assessment}
\alias{plot_residual_diagnostics}
\alias{plot_solver_benchmark}
\alias{print.catalyst_model_validation}
\title{Historical, holdout, and numerical model validation}
\usage{
validation_split(observations, holdout_fraction = 0.25, time_field = "time", entity_fields = character())
model_error_metrics(observed, predicted, weights = NULL)
residual_diagnostics(fitted)
validate_model_fit(calibration, observations = NULL, thresholds = list())
solver_benchmark(scenario, methods = c("rk4", "euler"), step_sizes = c(1, 0.5),
  metrics = c("K", "H", "N", "C", "gdp", "emissions"),
  reference_method = "rk4", reference_step = NULL)
stability_assessment(scenario, perturbation_fraction = 0.01, tolerance = 0.1,
  invariant_states = c("K", "H", "N", "P", "A"))
plot_residual_diagnostics(x)
plot_solver_benchmark(x)
\method{print}{catalyst_model_validation}(x, ...)
}
\arguments{
\item{observations}{Observation data frame.}
\item{holdout_fraction}{Fraction assigned to holdout.}
\item{time_field}{Time-field name.}
\item{entity_fields}{Optional entity fields.}
\item{observed}{Observed numeric values.}
\item{predicted}{Predicted numeric values.}
\item{weights}{Optional positive weights.}
\item{fitted}{Fitted observation table.}
\item{calibration}{A model calibration.}
\item{thresholds}{Named acceptance thresholds.}
\item{scenario}{Canonical scenario.}
\item{methods}{Integration methods.}
\item{step_sizes}{Numerical time steps.}
\item{metrics}{Metrics compared across solvers.}
\item{reference_method}{Reference method.}
\item{reference_step}{Reference time step.}
\item{perturbation_fraction}{Fractional initial-state perturbation.}
\item{tolerance}{Stability tolerance.}
\item{invariant_states}{States required to remain finite and non-negative.}
\item{x}{Validation or solver-benchmark object.}
\item{...}{Additional method arguments.}
}
\value{Validation partitions, metrics, diagnostics, benchmarks, assessments, or plots.}
\description{Supports historical fit, holdout validation, residual diagnostics, error metrics, solver comparisons, stability tests, invariants, and boundary conditions.}
