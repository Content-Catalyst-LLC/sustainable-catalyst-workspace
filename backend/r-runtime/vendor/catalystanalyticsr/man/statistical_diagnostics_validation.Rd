\name{statistical_diagnostics_validation}
\alias{statistical_diagnostics_manifest}
\alias{statistical_diagnostic}
\alias{statistical_assumption}
\alias{statistical_robustness_evidence}
\alias{statistical_model_comparison}
\alias{statistical_validation_bundle}
\alias{validate_statistical_validation_bundle}
\alias{statistical_validation_from_model}
\alias{statistical_validation_from_regression}
\alias{statistical_validation_to_json}
\alias{statistical_validation_from_json}
\title{Statistical diagnostics and validation evidence contract}
\description{Creates machine-readable diagnostic, assumption, robustness, model-comparison, and validation-evidence objects for Platform Core and Workspace. Diagnostic evidence never automatically certifies statistical significance, scientific validity, causal identification, or a preferred model.}
\usage{
statistical_diagnostics_manifest()
statistical_diagnostic(id, diagnostic_type, name, observed = NULL, reference = NULL, operator = NULL, p_value = NULL, method_ref = NULL, units = NULL, evidence_refs = character(), notes = character())
statistical_assumption(id, label, statement, status, evidence_refs = character(), limitations = character())
statistical_robustness_evidence(id, method_ref, target_ref, result = list(), evidence_refs = character(), limitations = character())
statistical_model_comparison(id, model_refs, criteria = list(), evidence_refs = character(), notes = character())
statistical_validation_bundle(id, analysis_ref, model_ref = NULL, diagnostics = list(), assumptions = list(), robustness = list(), comparisons = list(), source_status = NULL, limitations = character(), review_status = c("unreviewed", "in_review", "reviewed"), provenance = list())
validate_statistical_validation_bundle(x)
statistical_validation_from_model(validation, analysis_ref = NULL)
statistical_validation_from_regression(model, analysis_ref = NULL)
statistical_validation_to_json(x, path = NULL, pretty = TRUE)
statistical_validation_from_json(json)
}
\value{Machine-readable statistical diagnostics and validation evidence objects.}
\details{The v2.2.0 contract separates reported diagnostics and threshold evidence from scientific-validity judgments. Human review remains mandatory.}
\keyword{models}
\keyword{statistics}
\keyword{diagnostics}
