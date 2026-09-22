\name{export_uncertainty_analysis}
\alias{export_uncertainty_analysis}
\alias{export_stress_test}
\title{Export uncertainty and stress-test bundles}
\description{Writes machine-readable scenario, summary, probability, sensitivity, failure, sample, and manifest files for reproducible review.}
\usage{
export_uncertainty_analysis(x, dir = "catalyst_uncertainty_bundle", prefix = "uncertainty", include_samples = TRUE, zip_bundle = TRUE)
export_stress_test(x, dir = "catalyst_stress_test_bundle", prefix = "stress-test")
}
\arguments{
  \item{x}{A \code{catalyst_uncertainty_run} for uncertainty exports or a \code{catalyst_stress_test} for stress-test exports.}
  \item{dir}{Output directory or parent directory for the generated bundle.}
  \item{prefix}{Stable file or comparison identifier used in generated names.}
  \item{include_samples}{Logical; include sampled inputs and per-sample output tables.}
  \item{zip_bundle}{Logical; create a ZIP archive of the uncertainty bundle.}
}
\value{Invisibly returns generated paths.}
