\name{econometrics_policy_evaluation}
\alias{causal_assumption}
\alias{regression_spec}
\alias{validate_regression_spec}
\alias{fit_policy_regression}
\alias{panel_regression}
\alias{regression_diagnostics}
\alias{difference_in_differences}
\alias{event_study}
\alias{interrupted_time_series}
\alias{synthetic_control}
\alias{policy_effect_summary}
\alias{policy_evaluation_analysis}
\alias{policy_evaluation_summary}
\alias{plot_policy_effects}
\alias{plot_event_study}
\alias{plot_synthetic_control}
\alias{print.catalyst_policy_regression}
\alias{print.catalyst_policy_evaluation_analysis}
\title{Econometrics and policy evaluation}
\description{
Governed regression, panel, quasi-experimental, synthetic-control,
diagnostic, and policy-effect workflows with explicit causal-assumption
and human-review boundaries.
}
\usage{
causal_assumption(
  id,
  label,
  statement,
  status = c("required", "supported", "challenged", "failed", "not_assessed"),
  evidence = list(),
  limitations = character()
)

regression_spec(
  id,
  title,
  outcome,
  predictors,
  unit_id = NULL,
  time_id = NULL,
  weights = NULL,
  cluster = NULL,
  confidence_level = 0.95,
  assumptions = list(),
  description = "",
  metadata = list()
)

validate_regression_spec(spec, data = NULL)

fit_policy_regression(
  data,
  spec,
  fixed_effects = c("none", "unit", "time", "two_way"),
  covariance = c("classical", "hc1", "cluster")
)

panel_regression(
  data,
  spec,
  effects = c("two_way", "unit", "time"),
  covariance = c("cluster", "hc1", "classical")
)

regression_diagnostics(model)

difference_in_differences(
  data,
  outcome,
  treatment,
  post,
  unit_id,
  time_id,
  covariates = character(),
  cluster = unit_id,
  confidence_level = 0.95,
  assumptions = list(),
  id = "difference-in-differences",
  title = "Difference-in-differences evaluation"
)

event_study(
  data,
  outcome,
  treated,
  event_time,
  unit_id,
  time_id,
  reference_period = -1,
  window = NULL,
  covariates = character(),
  cluster = unit_id,
  confidence_level = 0.95,
  assumptions = list(),
  id = "event-study",
  title = "Event-study evaluation"
)

interrupted_time_series(
  data,
  outcome,
  time,
  intervention_time,
  covariates = character(),
  confidence_level = 0.95,
  assumptions = list(),
  id = "interrupted-time-series",
  title = "Interrupted time-series evaluation"
)

synthetic_control(
  data,
  outcome,
  unit_id,
  time_id,
  treated_unit,
  intervention_time,
  donor_units = NULL,
  confidence_level = 0.95,
  assumptions = list(),
  id = "synthetic-control",
  title = "Synthetic-control evaluation"
)

policy_effect_summary(evaluation)

policy_evaluation_analysis(
  id,
  title,
  evaluations,
  assumptions = list(),
  decision_context = "",
  review_status = c("draft", "under_review", "approved_for_specified_use"),
  metadata = list()
)

policy_evaluation_summary(analysis)

plot_policy_effects(analysis)

plot_event_study(evaluation)

plot_synthetic_control(evaluation)

\method{print}{catalyst_policy_regression}(x, ...)

\method{print}{catalyst_policy_evaluation_analysis}(x, ...)
}
\arguments{
  \item{id}{Stable identifier.}
  \item{label}{Human-readable label.}
  \item{statement}{Explicit identifying assumption.}
  \item{status}{Assumption status.}
  \item{evidence}{Evidence references or notes.}
  \item{limitations}{Known limitations.}
  \item{title}{Human-readable title.}
  \item{outcome}{Outcome column.}
  \item{predictors}{Predictor columns.}
  \item{unit_id}{Panel-unit column.}
  \item{time_id}{Time column.}
  \item{weights}{Observation-weight column.}
  \item{cluster}{Cluster column.}
  \item{confidence_level}{Confidence level.}
  \item{assumptions}{Causal-assumption records.}
  \item{description}{Method description.}
  \item{metadata}{Additional metadata.}
  \item{spec}{Regression specification.}
  \item{data}{Analysis data frame.}
  \item{fixed_effects}{Fixed-effects structure.}
  \item{covariance}{Uncertainty estimator.}
  \item{effects}{Panel effects.}
  \item{model}{Policy-regression result.}
  \item{treatment}{Treatment-group indicator.}
  \item{post}{Post-intervention indicator.}
  \item{covariates}{Optional covariates.}
  \item{treated}{Treatment-group indicator.}
  \item{event_time}{Relative event-time column.}
  \item{reference_period}{Omitted event period.}
  \item{window}{Lead/lag window.}
  \item{time}{Time-index column.}
  \item{intervention_time}{First intervention or post period.}
  \item{treated_unit}{Treated unit.}
  \item{donor_units}{Donor units.}
  \item{evaluation}{Econometric evaluation.}
  \item{evaluations}{Named econometric evaluations.}
  \item{decision_context}{Decision context.}
  \item{review_status}{Review status.}
  \item{analysis}{Policy-evaluation analysis.}
  \item{x}{Object to print.}
  \item{...}{Additional arguments.}
}
\value{
Governed econometric records, summaries, or plots.
}
\seealso{
\code{export_policy_evaluation()}
}
\keyword{models}
