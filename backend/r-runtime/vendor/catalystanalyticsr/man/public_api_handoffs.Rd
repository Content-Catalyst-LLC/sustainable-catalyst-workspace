\name{public_api_handoffs}
\alias{api_endpoint}
\alias{catalyst_public_api_manifest}
\alias{api_request}
\alias{validate_api_request}
\alias{api_response}
\alias{validate_api_response}
\alias{dispatch_api_request}
\alias{site_intelligence_handoff}
\alias{research_lab_handoff}
\alias{workbench_handoff}
\alias{catalyst_canvas_handoff}
\alias{workspace_handoff}
\alias{platform_handoff}
\alias{validate_platform_handoff}
\alias{handoff_to_json}
\alias{handoff_from_json}
\alias{print.catalyst_api_request}
\alias{print.catalyst_api_response}
\alias{print.catalyst_platform_handoff}
\title{Public API contracts and first-party platform handoffs}
\description{Create versioned public API envelopes, dispatch supported in-process requests, and build governed handoffs for Sustainable Catalyst products.}
\usage{
api_endpoint(id, method, path, title, description = "",
  request_schema = NULL,
  response_schema = "catalyst_api_response@1.0.0",
  access = c("public", "authenticated", "institutional"),
  side_effects = FALSE)

catalyst_public_api_manifest()

api_request(endpoint, payload = list(), request_id = NULL,
  actor = list(), context = list())

validate_api_request(request)

api_response(request, data = list(),
  status = c("ok", "accepted", "error"), warnings = character(),
  errors = character())

validate_api_response(response)

dispatch_api_request(request, stop_on_error = FALSE)

site_intelligence_handoff(project, dataset_ids = NULL,
  indicators = character(),
  refresh_policy = c("pinned_snapshot", "latest_approved"))

research_lab_handoff(project,
  job_type = c("calibration", "uncertainty", "batch_simulation", "benchmark"),
  scenario_ids = NULL, resources = list())

workbench_handoff(project, formulas = list(), calculators = list())

catalyst_canvas_handoff(project, objectives = list(), stakeholders = list())

workspace_handoff(project, runtime = "r", provider = "catalystanalyticsr",
  resources = list(), execution_policy = list())

platform_handoff(project,
  target = c("site_intelligence", "research_lab", "workbench",
    "catalyst_canvas", "decision_studio", "knowledge_library", "workspace"),
  options = list())

validate_platform_handoff(handoff)

handoff_to_json(handoff, path = NULL, pretty = TRUE)

handoff_from_json(json)

\method{print}{catalyst_api_request}(x, ...)

\method{print}{catalyst_api_response}(x, ...)

\method{print}{catalyst_platform_handoff}(x, ...)
}
\arguments{
  \item{id}{Stable endpoint identifier.}
  \item{method}{HTTP-style method label.}
  \item{path}{Versioned route path.}
  \item{title}{Human-readable title.}
  \item{description}{Human-readable description.}
  \item{request_schema}{Request contract identifier.}
  \item{response_schema}{Response contract identifier.}
  \item{access}{Access classification.}
  \item{side_effects}{Whether the endpoint mutates durable state.}
  \item{endpoint}{Endpoint identifier.}
  \item{payload}{Request payload.}
  \item{request_id}{Optional request identifier.}
  \item{actor}{Actor metadata.}
  \item{context}{Request context.}
  \item{request}{API request or request identifier.}
  \item{data}{Response data.}
  \item{status}{Response status.}
  \item{warnings}{Warning messages.}
  \item{errors}{Error messages.}
  \item{response}{API response record.}
  \item{stop_on_error}{Whether endpoint errors should be thrown.}
  \item{project}{A reproducible project.}
  \item{dataset_ids}{Project dataset identifiers.}
  \item{indicators}{Requested indicators.}
  \item{refresh_policy}{Site Intelligence refresh policy.}
  \item{job_type}{Research Lab job type.}
  \item{scenario_ids}{Project scenario identifiers.}
  \item{resources}{Requested compute resource metadata.}
  \item{formulas}{Named Workbench formula records.}
  \item{calculators}{Optional calculator records.}
  \item{objectives}{Canvas objectives.}
  \item{stakeholders}{Canvas stakeholder records.}
  \item{runtime}{Workspace runtime language identifier.}
  \item{provider}{Workspace analytical provider identifier.}
  \item{execution_policy}{Workspace execution-policy metadata.}
  \item{target}{Sustainable Catalyst target product.}
  \item{options}{Target-specific options.}
  \item{handoff}{Platform handoff record.}
  \item{pretty}{Pretty-print JSON.}
  \item{json}{JSON text or a JSON file path.}
  \item{x}{Object to print.}
  \item{...}{Additional print arguments.}
}
\value{Constructors and dispatch return governed list records. JSON helpers return text or paths. Validators return invisibly.}
\examples{
manifest <- catalyst_public_api_manifest()
request <- api_request("health")
dispatch_api_request(request)
}
