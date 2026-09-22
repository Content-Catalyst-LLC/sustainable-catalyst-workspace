\name{policy_optimization}
\alias{decision_variable}
\alias{policy_objective}
\alias{policy_constraint}
\alias{policy_optimization_spec}
\alias{validate_policy_optimization_spec}
\alias{evaluate_policy_candidates}
\alias{optimize_policy}
\alias{policy_pareto_frontier}
\alias{policy_feasible_region}
\alias{target_seeking_scenario}
\alias{cost_effectiveness_analysis}
\alias{marginal_abatement_curve}
\alias{adaptive_trigger}
\alias{policy_stage}
\alias{policy_pathway}
\alias{validate_policy_pathway}
\alias{policy_sequence}
\alias{evaluate_policy_pathway}
\alias{robust_pathway_analysis}
\alias{policy_pathway_analysis}
\alias{policy_optimization_summary}
\alias{plot_policy_pareto}
\alias{plot_marginal_abatement}
\alias{plot_policy_pathway}
\alias{print.catalyst_policy_optimization}
\alias{print.catalyst_policy_pathway}
\title{Optimization and adaptive policy pathway contracts}
\usage{
decision_variable(id, label, target, lower, upper, initial = NULL,
  step = NULL, type = c("continuous", "integer"), unit = "",
  description = "")

policy_objective(id, label, metric,
  direction = c("minimize", "maximize", "target"), weight = 1,
  target = NULL, tolerance = NULL, unit = "")

policy_constraint(id, label, metric,
  operator = c("<=", ">=", "==", "between"), value = NULL,
  lower = NULL, upper = NULL, tolerance = 1e-08, hard = TRUE)

policy_optimization_spec(id, title, variables, objectives,
  constraints = list(), method = c("grid", "random_search"),
  max_evaluations = 1000L, seed = 1L, description = "",
  metadata = list())

validate_policy_optimization_spec(spec)

evaluate_policy_candidates(spec, evaluator, candidates = NULL)

optimize_policy(spec, evaluator, candidates = NULL)

policy_pareto_frontier(x)

policy_feasible_region(x)

target_seeking_scenario(scenario, spec, evaluator, candidates = NULL,
  id = NULL, title = NULL)

cost_effectiveness_analysis(data, option_col = "option",
  cost_col = "cost", effect_col = "effect", baseline_effect = 0)

marginal_abatement_curve(data, option_col = "option",
  cost_col = "cost", abatement_col = "abatement")

adaptive_trigger(id, label, metric,
  operator = c(">", ">=", "<", "<=", "=="), threshold, action,
  review_period = 1, description = "")

policy_stage(id, label, start, end, actions = list(), triggers = list(),
  decision_gate = TRUE)

policy_pathway(id, title, stages, description = "",
  objectives = list(), metadata = list())

validate_policy_pathway(pathway)

policy_sequence(pathway)

evaluate_policy_pathway(pathway, evidence, time_col = "time")

robust_pathway_analysis(pathways, performance, objectives,
  regret_tolerance = 0.25)

policy_pathway_analysis(optimization, pathway = NULL,
  pathway_evaluation = NULL, robust_analysis = NULL,
  cost_effectiveness = NULL, marginal_abatement = NULL)

policy_optimization_summary(x)

plot_policy_pareto(x, x_metric, y_metric)

plot_marginal_abatement(x, option_col = "option")

plot_policy_pathway(pathway)

\method{print}{catalyst_policy_optimization}(x, ...)

\method{print}{catalyst_policy_pathway}(x, ...)
}
\arguments{
  \item{id}{Stable record, analysis, scenario, trigger, stage, or pathway identifier.}
  \item{label}{Human-readable label.}
  \item{target}{Nested scenario field for a decision variable, or a numeric target for a target objective.}
  \item{lower, upper}{Variable or constraint bounds.}
  \item{initial}{Initial or reference variable value.}
  \item{step}{Grid-search step.}
  \item{type}{Continuous or integer decision-variable type.}
  \item{unit}{Unit label.}
  \item{description}{Purpose or method note.}
  \item{metric}{Evaluator metric name.}
  \item{direction}{Objective direction.}
  \item{weight}{Relative objective weight.}
  \item{tolerance}{Numerical or reporting tolerance.}
  \item{operator}{Constraint or trigger operator.}
  \item{value}{Scalar constraint value.}
  \item{hard}{Whether violation removes a candidate from the feasible region.}
  \item{title}{Human-readable title.}
  \item{variables}{Decision-variable records.}
  \item{objectives}{Objective records.}
  \item{constraints}{Constraint records.}
  \item{method}{Candidate generation method.}
  \item{max_evaluations}{Maximum candidate evaluations.}
  \item{seed}{Reproducible random seed.}
  \item{metadata}{Additional metadata.}
  \item{spec}{Optimization specification.}
  \item{evaluator}{Function mapping decisions to named numeric metrics.}
  \item{candidates}{Optional candidate data frame.}
  \item{x}{Optimization, marginal-abatement, or print-method object.}
  \item{scenario}{Canonical scenario template.}
  \item{data}{Option-level data frame.}
  \item{option_col, cost_col, effect_col, abatement_col}{Column names used by economic analyses.}
  \item{baseline_effect}{Baseline effect for incremental analysis.}
  \item{threshold}{Adaptive trigger threshold.}
  \item{action}{Action recommendation attached to a trigger.}
  \item{review_period}{Review interval.}
  \item{start, end}{Policy-stage boundaries.}
  \item{actions}{Planned stage actions.}
  \item{triggers}{Adaptive trigger records.}
  \item{decision_gate}{Whether the stage boundary requires human review.}
  \item{stages}{Ordered policy stages.}
  \item{pathway}{Policy pathway.}
  \item{evidence}{Time-indexed evidence data frame.}
  \item{time_col}{Evidence time-column name.}
  \item{pathways}{Policy pathways.}
  \item{performance}{Pathway-by-scenario performance data.}
  \item{regret_tolerance}{Maximum accepted normalized worst-case regret.}
  \item{optimization}{Policy optimization result.}
  \item{pathway_evaluation}{Optional adaptive-trigger evaluation.}
  \item{robust_analysis}{Optional robust pathway analysis.}
  \item{cost_effectiveness}{Optional cost-effectiveness table.}
  \item{marginal_abatement}{Optional marginal-abatement table.}
  \item{x_metric, y_metric}{Metrics plotted on the Pareto axes.}
  \item{...}{Additional print arguments.}
}
\value{Governed optimization, feasibility, Pareto, economic, pathway, robustness, summary, or plot records depending on the function.}
\description{Defines reproducible policy optimization and adaptive pathway records. Optimization results and trigger evaluations remain analytical recommendations requiring human review.}
