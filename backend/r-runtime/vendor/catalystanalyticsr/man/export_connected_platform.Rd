\name{export_connected_platform}
\alias{export_connected_platform}
\title{Export a connected sustainability platform}
\usage{
export_connected_platform(
  platform,
  dir,
  prefix = "connected-sustainability-platform",
  zip_bundle = TRUE
)
}
\arguments{
  \item{platform}{Connected platform record.}
  \item{dir}{Output directory.}
  \item{prefix}{Bundle directory prefix.}
  \item{zip_bundle}{Create a ZIP archive.}
}
\description{Writes the complete connected-platform record, manifest, graph indexes, registry indexes, decision and publication indexes, workflow index, integrity manifest, and an optional ZIP bundle.}
\value{A named list of generated artifact paths.}
