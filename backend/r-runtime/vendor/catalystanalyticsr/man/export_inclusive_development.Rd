\name{export_inclusive_development}
\alias{export_inclusive_development}
\title{Export an Inclusive-Development Analysis}
\usage{
export_inclusive_development(
  x,
  dir = ".",
  prefix = "inclusive-development",
  zip_bundle = TRUE
)
}
\arguments{
  \item{x}{A \code{catalyst_inclusive_development} object.}
  \item{dir}{Output directory.}
  \item{prefix}{File prefix and bundle-directory name.}
  \item{zip_bundle}{Whether to create a ZIP bundle.}
}
\value{A named list of written paths.}
\description{Writes machine-readable analysis, tabular accounts, calculation trace, a Markdown brief, and an integrity manifest.}
