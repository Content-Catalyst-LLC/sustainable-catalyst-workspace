\name{core_computational_provider}
\alias{catalyst_core_provider_manifest}
\alias{core_analytical_request}
\alias{as_core_analytical_request}
\alias{validate_core_analytical_request}
\alias{core_execution_plan}
\alias{workspace_core_execution_envelope}
\alias{core_analytical_result}
\alias{validate_core_analytical_result}
\alias{core_request_to_json}
\alias{core_request_from_json}
\alias{core_result_to_json}
\alias{core_result_from_json}
\alias{print.catalyst_core_analytical_request}
\alias{print.catalyst_core_analytical_result}
\title{Platform Core computational-provider contract}
\description{Provider-side contracts that let Platform Core 3.1+ declare analytical work and let Workspace execute Catalyst Analytics R as a governed R runtime provider.}
\usage{
catalyst_core_provider_manifest()

core_analytical_request(request_key, analysis_type, input_refs = character(),
  parameters = list(), reproducibility = list(), method_ref = NULL,
  session_ref = NULL, external_execution_ref = NULL, provenance = list(),
  visibility = c("internal", "public"))

as_core_analytical_request(x)
validate_core_analytical_request(request, require_executable = FALSE)
core_execution_plan(request)
workspace_core_execution_envelope(request, resource_policy = list(), environment = list())

core_analytical_result(request, result_ref, output_refs = character(),
  estimate_refs = character(), uncertainty_refs = character(),
  diagnostic_refs = character(), artifact_refs = character(),
  environment_ref = NULL, external_execution_ref = NULL,
  status = c("recorded", "completed", "failed"), provenance = list(),
  native_result = NULL, warnings = character(), errors = character())

validate_core_analytical_result(result)
core_request_to_json(request, path = NULL, pretty = TRUE)
core_request_from_json(json)
core_result_to_json(result, path = NULL, pretty = TRUE)
core_result_from_json(json)
}
\arguments{
  \item{request_key}{Stable Core analytical request key.}
  \item{analysis_type}{A capability declared by Catalyst Analytics R.}
  \item{input_refs}{Core or Workspace object references, resolved by Workspace.}
  \item{parameters}{Provider parameters.}
  \item{reproducibility}{Seeds, snapshots, code references, or other reproducibility metadata.}
  \item{method_ref}{Optional governed method reference from the capability registry.}
  \item{session_ref}{Optional Platform Core session reference.}
  \item{external_execution_ref}{Optional Workspace execution reference.}
  \item{provenance}{Provenance metadata.}
  \item{visibility}{Internal or public visibility.}
  \item{x}{Request-like object to normalize.}
  \item{request}{Core analytical request.}
  \item{require_executable}{Require the capability to be fully executable in this release.}
  \item{resource_policy}{Workspace resource policy metadata.}
  \item{environment}{Requested runtime environment capture.}
  \item{result_ref}{Stable result reference.}
  \item{output_refs,estimate_refs,uncertainty_refs,diagnostic_refs,artifact_refs}{References to governed Core objects or artifacts.}
  \item{environment_ref}{Workspace runtime-environment reference.}
  \item{status}{Result status.}
  \item{native_result}{Optional JSON-safe provider-native summary.}
  \item{warnings,errors}{Provider warnings or errors.}
  \item{result}{Core analytical result.}
  \item{path}{Optional JSON output path.}
  \item{pretty}{Pretty-print JSON.}
  \item{json}{JSON text or path.}
  \item{...}{Unused print-method arguments.}
}
\details{Platform Core does not execute R. Workspace resolves input references, controls authentication, runtime isolation, resources, job persistence, and environment capture. Catalyst Analytics R provides a whitelist of analytical capabilities and methods and returns references that Core can bind into provenance, diagnostics, uncertainty, evidence, visualization, and reproducibility records.}
\value{Provider manifests, request/result envelopes, execution plans, Workspace envelopes, JSON text, or validated objects depending on the function.}
