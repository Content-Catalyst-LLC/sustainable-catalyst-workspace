\name{export_model_validation}
\alias{export_model_validation}
\title{Export model validation and governance evidence}
\usage{
export_model_validation(x, dir = ".", prefix = "catalyst-model-validation",
  include_history = TRUE, zip_bundle = TRUE)
}
\arguments{
\item{x}{A model-validation analysis.}
\item{dir}{Parent output directory.}
\item{prefix}{Bundle directory and ZIP prefix.}
\item{include_history}{Whether to include optimizer history.}
\item{zip_bundle}{Whether to create a ZIP archive.}
}
\value{Named paths to exported files.}
\description{Exports calibration parameters, fitted observations, historical and holdout metrics, residual diagnostics, solver and stability evidence, governance records, a Markdown brief, and a file-integrity manifest.}
