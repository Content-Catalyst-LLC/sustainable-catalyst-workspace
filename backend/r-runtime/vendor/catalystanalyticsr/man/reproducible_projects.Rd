\name{reproducible_projects}
\alias{capture_project_environment}
\alias{catalyst_project}
\alias{validate_catalyst_project}
\alias{project_add_scenario}
\alias{project_add_dataset}
\alias{project_add_model}
\alias{project_add_parameter_set}
\alias{project_add_run}
\alias{project_add_indicator}
\alias{project_add_plot}
\alias{project_add_note}
\alias{project_add_review}
\alias{project_snapshot}
\alias{project_fingerprint}
\alias{project_summary}
\alias{project_manifest}
\alias{project_to_json}
\alias{project_from_json}
\alias{print.catalyst_project}
\alias{print.catalyst_project_run}
\title{Reproducible analytical projects}
\description{Create and maintain governed analytical projects containing scenarios, datasets, models, parameter sets, run records, indicators, plots, interpretation notes, review records, snapshots, environment details, and publication history.}
\usage{
capture_project_environment(packages = NULL, include_session = TRUE)

catalyst_project(project_id, title, description = "", owner = "",
  scope = list(), tags = character(), metadata = list())

validate_catalyst_project(project)

project_add_scenario(project, scenario, replace = FALSE)

project_add_dataset(project, dataset, replace = FALSE)

project_add_model(project, model, replace = FALSE)

project_add_parameter_set(project, parameter_set_id, values,
  model_id = NULL, model_version = NULL, description = "",
  assumptions = list(), replace = FALSE)

project_add_run(project, result, run_id, label = run_id,
  scenario_ids = character(), parameter_set_id = NULL, inputs = NULL,
  warnings = character(), errors = character(),
  review_status = "unreviewed", metadata = list(), replace = FALSE)

project_add_indicator(project, indicator, indicator_id, replace = FALSE)

project_add_plot(project, plot_id, path, title = plot_id, caption = "",
  run_id = NULL, replace = FALSE)

project_add_note(project, note_id, text, author = "",
  run_ids = character(), status = "draft")

project_add_review(project, review_id, reviewer, decision = "pending",
  comments = "", scope = "project", run_ids = character())

project_snapshot(project, snapshot_id, note = "")

project_fingerprint(project)

project_summary(project)

project_manifest(project)

project_to_json(project, path, pretty = TRUE)

project_from_json(path)

\method{print}{catalyst_project}(x, ...)

\method{print}{catalyst_project_run}(x, ...)
}
\arguments{
  \item{packages}{Package names for environment capture.}
  \item{include_session}{Whether to include printable session information.}
  \item{project_id}{Stable project identifier.}
  \item{title}{Human-readable project or figure title.}
  \item{description}{Project or parameter-set description.}
  \item{owner}{Responsible analyst or institution.}
  \item{scope}{Geographic, sector, temporal, or decision scope.}
  \item{tags}{Discovery tags.}
  \item{metadata}{Additional metadata.}
  \item{project}{A \code{catalyst_project}.}
  \item{scenario}{A canonical Catalyst scenario.}
  \item{replace}{Whether an existing record may be replaced.}
  \item{dataset}{A governed \code{catalyst_dataset}.}
  \item{model}{A registered model or model manifest.}
  \item{parameter_set_id}{Stable parameter-set identifier.}
  \item{values}{Named parameter values.}
  \item{model_id}{Optional model identifier.}
  \item{model_version}{Optional model version.}
  \item{assumptions}{Associated assumption records.}
  \item{result}{Analytical result object.}
  \item{run_id}{Stable analytical-run identifier.}
  \item{label}{Human-readable run label.}
  \item{scenario_ids}{Project scenarios used by a run.}
  \item{inputs}{Explicit input record.}
  \item{warnings}{Warning messages.}
  \item{errors}{Error messages.}
  \item{review_status}{Review state.}
  \item{indicator}{Indicator result or set.}
  \item{indicator_id}{Stable indicator-artifact identifier.}
  \item{plot_id}{Stable figure identifier.}
  \item{path}{Input figure path or project JSON path.}
  \item{caption}{Figure caption.}
  \item{note_id}{Stable interpretation-note identifier.}
  \item{text}{Interpretation text.}
  \item{author}{Note author.}
  \item{run_ids}{Related run identifiers.}
  \item{status}{Note status.}
  \item{review_id}{Stable review identifier.}
  \item{reviewer}{Reviewer name or institution.}
  \item{decision}{Review decision.}
  \item{comments}{Review comments.}
  \item{snapshot_id}{Stable snapshot identifier.}
  \item{note}{Snapshot note.}
  \item{pretty}{Whether JSON should be pretty printed.}
  \item{x}{Project or run object for printing.}
  \item{...}{Unused.}
}
\value{Constructors and add functions return updated project objects. Validation returns \code{TRUE} invisibly. Summary functions return data frames or JSON-safe manifests. JSON functions return a project or output path.}
\examples{
project <- catalyst_project("demo-project", "Demo project")
project_summary(project)
}
