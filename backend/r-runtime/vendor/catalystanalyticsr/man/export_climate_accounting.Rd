\name{export_climate_accounting}
\alias{export_climate_accounting}
\title{Export climate and natural-capital accounting}
\usage{
export_climate_accounting(
  analysis,
  dir,
  prefix = analysis$id,
  zip_bundle = TRUE,
  overwrite = FALSE,
  quiet = FALSE
)
}
\arguments{
  \item{analysis}{A \code{catalyst_climate_accounting}.}
  \item{dir}{Parent output directory.}
  \item{prefix}{Stable bundle prefix.}
  \item{zip_bundle}{Create a ZIP archive.}
  \item{overwrite}{Replace an existing bundle.}
  \item{quiet}{Suppress informational messages.}
}
\value{
Invisibly returns bundle paths, manifest, and written files.
}
\description{
Writes inventory records, carbon pathways, Kaya contributions,
natural-capital accounts, boundary assessment, review boundaries, and a
human-readable brief.
}
