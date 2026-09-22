\name{export_policy_evaluation}
\alias{export_policy_evaluation}
\title{Export econometric policy-evaluation evidence}
\description{
Writes machine-readable results, effect tables, assumptions, diagnostics,
a human-readable brief, an integrity manifest, and an optional ZIP bundle.
}
\usage{
export_policy_evaluation(
  analysis,
  dir = ".",
  prefix = "catalyst-policy-evaluation",
  zip_bundle = TRUE
)
}
\arguments{
  \item{analysis}{A policy-evaluation analysis.}
  \item{dir}{Parent output directory.}
  \item{prefix}{Bundle directory name.}
  \item{zip_bundle}{Create a ZIP archive.}
}
\value{
A named list of generated paths.
}
\keyword{utilities}
