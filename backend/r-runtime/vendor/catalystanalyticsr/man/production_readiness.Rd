\name{production_readiness}
\alias{catalyst_api_manifest}
\alias{catalyst_compatibility_manifest}
\alias{catalyst_release_readiness}
\alias{validate_release_readiness}
\title{Stable API and production release governance}
\usage{
catalyst_api_manifest(include_experimental = TRUE)

catalyst_compatibility_manifest()

catalyst_release_readiness(checks = NULL, evidence = list())

validate_release_readiness(x, require_ready = FALSE)
}
\arguments{
\item{include_experimental}{Include exported APIs not classified as stable.}
\item{checks}{Optional named logical vector overriding default readiness gates.}
\item{evidence}{Optional named list of evidence references.}
\item{x}{A release-readiness record.}
\item{require_ready}{Require every readiness gate to pass.}
}
\value{A machine-readable API, compatibility, or release-readiness record.}
\description{Declares the stable v1.1 public API, compatibility policy, and production release gates.}
