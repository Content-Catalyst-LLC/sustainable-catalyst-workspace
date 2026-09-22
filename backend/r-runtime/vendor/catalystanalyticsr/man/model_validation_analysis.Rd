\name{model_validation_analysis}
\alias{model_validation_analysis}
\alias{model_validation_summary}
\alias{print.catalyst_model_validation_analysis}
\title{Integrated calibration, validation, and governance analysis}
\usage{
model_validation_analysis(calibration, validation, solver = NULL, stability = NULL,
  governance, analysis_id = "model-validation",
  title = "Calibration, validation, and model governance", metadata = list())
model_validation_summary(x)
\method{print}{catalyst_model_validation_analysis}(x, ...)
}
\arguments{
\item{calibration}{A model calibration.}
\item{validation}{A model validation.}
\item{solver}{Optional solver benchmark.}
\item{stability}{Optional stability assessment.}
\item{governance}{Model governance record.}
\item{analysis_id}{Stable analysis identifier.}
\item{title}{Human-readable title.}
\item{metadata}{Additional metadata.}
\item{x}{A model-validation analysis.}
\item{...}{Additional method arguments.}
}
\value{An integrated model-validation analysis or summary.}
\description{Combines parameter estimation, fit evidence, numerical testing, limitations, model cards, and lifecycle governance.}
