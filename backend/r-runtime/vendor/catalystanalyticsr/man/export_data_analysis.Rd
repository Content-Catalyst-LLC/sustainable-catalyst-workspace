\name{export_data_analysis}
\alias{export_data_analysis}
\title{Export a governed data-and-indicator analysis bundle}
\usage{
export_data_analysis(
  dataset,
  indicators = NULL,
  dir,
  analysis_id = NULL,
  group_by = character(),
  na_rm = FALSE,
  zip = TRUE,
  overwrite = FALSE,
  quiet = FALSE
)
}
\arguments{
  \item{dataset}{A \code{catalyst_dataset}.}
  \item{indicators}{Indicator result, result set, ids, or definitions.}
  \item{dir}{Parent output directory.}
  \item{analysis_id}{Stable bundle identifier.}
  \item{group_by}{Optional grouping fields.}
  \item{na_rm}{Remove missing values in supported aggregates.}
  \item{zip}{Create a ZIP archive.}
  \item{overwrite}{Replace an existing bundle.}
  \item{quiet}{Suppress informational messages.}
}
\value{
Invisibly returns bundle paths, manifest, and written-file inventory.
}
\description{
Writes source records, dataset metadata, quality flags, transformation history,
indicator definitions, calculated values, trace records, and a file inventory.
}
