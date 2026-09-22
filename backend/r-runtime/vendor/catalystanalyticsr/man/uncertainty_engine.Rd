\name{uncertainty_engine}
\alias{uncertainty_spec}
\alias{validate_uncertainty_spec}
\alias{sample_uncertainty}
\alias{run_uncertainty}
\alias{uncertainty_summary}
\alias{uncertainty_probabilities}
\alias{global_sensitivity}
\alias{local_sensitivity}
\alias{plot_uncertainty}
\alias{plot_tornado}
\alias{stress_shock}
\alias{stress_case}
\alias{run_stress_tests}
\alias{stress_test_summary}
\alias{plot_stress_test}
\title{Uncertainty, sensitivity, and stress testing}
\description{Defines governed uncertainty distributions, samples scenario ensembles, summarizes uncertainty and sensitivity, and evaluates named stress cases.}
\usage{
uncertainty_spec(target, distribution = c("uniform", "normal", "lognormal", "triangular", "beta", "discrete", "fixed"), parameters = list(), id = NULL, label = NULL, enabled = TRUE)
validate_uncertainty_spec(spec, scenario = NULL)
sample_uncertainty(scenario, n = 1000L, method = c("monte_carlo", "latin_hypercube"), seed = 42L, uncertainty = NULL)
run_uncertainty(scenario, n = 1000L, sampling = c("monte_carlo", "latin_hypercube"), seed = 42L, metrics = NULL, thresholds = list(), method = NULL, continue_on_error = TRUE)
uncertainty_summary(x)
uncertainty_probabilities(x)
global_sensitivity(x, method = c("spearman", "pearson"))
local_sensitivity(scenario, targets = NULL, change = 0.01, metrics = NULL, method = NULL)
plot_uncertainty(x, metric = NULL, type = c("distribution", "interval"))
plot_tornado(x, metric = NULL, method = c("spearman", "pearson"))
stress_shock(target, value, mode = c("set", "add", "multiply"))
stress_case(id, title, shocks, description = "")
run_stress_tests(scenario, cases, metrics = NULL, method = NULL)
stress_test_summary(x)
plot_stress_test(x, metric = NULL, type = c("delta", "terminal"))
}
\arguments{
  \item{target}{A two-part canonical scenario path under \code{parameters}, \code{policy}, \code{initial_state}, or \code{constraints}.}
  \item{distribution}{Uncertainty distribution name.}
  \item{parameters}{Named list of distribution parameters.}
  \item{id}{Stable identifier for an uncertainty specification or stress case.}
  \item{label}{Human-readable uncertainty label.}
  \item{enabled}{Logical; whether an uncertainty specification participates in sampling.}
  \item{spec}{An uncertainty specification list.}
  \item{scenario}{A canonical \code{catalyst_scenario}.}
  \item{n}{Number of sampled realizations.}
  \item{method}{Sampling, correlation, or numerical-integration method, depending on the function.}
  \item{seed}{Integer random seed used for reproducible sampling.}
  \item{uncertainty}{Optional uncertainty specifications overriding the scenario records.}
  \item{sampling}{Sampling design: Monte Carlo or Latin hypercube.}
  \item{metrics}{Terminal indicators retained in an ensemble or comparison.}
  \item{thresholds}{Optional named threshold rules used for probability calculations.}
  \item{continue_on_error}{Logical; continue after an individual sampled realization fails.}
  \item{x}{A \code{catalyst_uncertainty_run} or \code{catalyst_stress_test}, depending on the function.}
  \item{targets}{Scenario target paths used for local sensitivity analysis.}
  \item{change}{Relative perturbation size for local sensitivity analysis.}
  \item{metric}{Indicator selected for plotting.}
  \item{type}{Plot type.}
  \item{value}{Numeric shock value.}
  \item{mode}{Shock application mode: set, add, or multiply.}
  \item{title}{Human-readable stress-case title.}
  \item{shocks}{Non-empty list of shock records.}
  \item{description}{Optional stress-case explanation.}
  \item{cases}{Non-empty list of named stress cases.}
}
\value{The constructor and analysis functions return uncertainty specifications, sampled data frames, \code{catalyst_uncertainty_run} objects, sensitivity tables, stress-case records, or \code{catalyst_stress_test} objects. Plot functions return ggplot objects.}
