\name{data_intake}
\alias{dataset_source}
\alias{as_catalyst_dataset}
\alias{read_catalyst_data}
\alias{validate_catalyst_dataset}
\alias{dataset_fingerprint}
\alias{dataset_manifest}
\alias{data_quality_report}
\alias{add_dataset_transformation}
\alias{register_unit_conversion}
\alias{list_unit_conversions}
\alias{convert_dataset_unit}
\alias{print.catalyst_dataset}
\title{Governed data intake and dataset contracts}
\usage{
dataset_source(
  id,
  title,
  publisher = "",
  url = "",
  license = "",
  retrieved_at = .utc_now(),
  citation = "",
  metadata = list()
)

as_catalyst_dataset(
  data,
  id,
  title = id,
  time_field = NULL,
  entity_fields = character(),
  units = list(),
  source = NULL,
  geography = list(),
  sector = list(),
  currency = list(code = NULL, price_year = NULL),
  required_fields = character(),
  missing_policy = c("flag", "error", "drop"),
  transformations = list(),
  metadata = list()
)

read_catalyst_data(path, format = c("auto", "csv", "json"), ...)

validate_catalyst_dataset(dataset, strict = FALSE)

dataset_fingerprint(dataset)

dataset_manifest(dataset, include_data = FALSE)

data_quality_report(dataset)

add_dataset_transformation(
  dataset,
  operation,
  description,
  fields = character(),
  parameters = list(),
  actor = "",
  occurred_at = .utc_now()
)

register_unit_conversion(
  from,
  to,
  multiplier,
  offset = 0,
  dimension,
  reciprocal = TRUE,
  overwrite = FALSE
)

list_unit_conversions()

convert_dataset_unit(dataset, field, to_unit)

\method{print}{catalyst_dataset}(x, ...)
}
\arguments{
  \item{id}{Stable dataset or source identifier.}
  \item{title}{Human-readable title.}
  \item{publisher}{Publisher or originating institution.}
  \item{url}{Optional source URL.}
  \item{license}{License or usage statement.}
  \item{retrieved_at}{UTC retrieval timestamp.}
  \item{citation}{Optional citation text.}
  \item{metadata}{Additional named metadata.}
  \item{data}{A data frame.}
  \item{time_field}{Optional time-column name.}
  \item{entity_fields}{Columns defining entities such as countries or sectors.}
  \item{units}{Named field-to-unit mapping.}
  \item{source}{A documented source record.}
  \item{geography}{Geographic-scope metadata.}
  \item{sector}{Sector-scope metadata.}
  \item{currency}{Currency and price-year metadata.}
  \item{required_fields}{Required dataset fields.}
  \item{missing_policy}{How missing values are handled.}
  \item{transformations}{Existing transformation-history records.}
  \item{path}{Local CSV or JSON path.}
  \item{format}{Input format or automatic detection.}
  \item{...}{Additional arguments or print arguments.}
  \item{dataset}{A \code{catalyst_dataset}.}
  \item{strict}{Treat quality warnings as validation errors.}
  \item{include_data}{Include source records in the manifest.}
  \item{operation}{Stable transformation identifier.}
  \item{description}{Transformation description.}
  \item{fields}{Affected dataset fields.}
  \item{parameters}{Transformation parameters.}
  \item{actor}{Actor or process identifier.}
  \item{occurred_at}{UTC transformation timestamp.}
  \item{from}{Source unit.}
  \item{to}{Destination unit.}
  \item{multiplier}{Linear conversion multiplier.}
  \item{offset}{Linear conversion offset.}
  \item{dimension}{Measurement dimension.}
  \item{reciprocal}{Register the reversible conversion.}
  \item{overwrite}{Replace an existing conversion.}
  \item{field}{Numeric field to convert.}
  \item{to_unit}{Destination unit.}
  \item{x}{Dataset to print.}
}
\value{
Dataset constructors and readers return a \code{catalyst_dataset}. Validation
returns invisibly. Manifest, quality, and conversion functions return the
records described in their names.
}
\description{
Imports CSV or JSON records into a versioned dataset contract that preserves
source, units, geography, currency, data-quality flags, transformation history,
and a stable fingerprint.
}
