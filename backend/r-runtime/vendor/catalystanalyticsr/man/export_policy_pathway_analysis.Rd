\name{export_policy_pathway_analysis}
\alias{export_policy_pathway_analysis}
\title{Export optimization and adaptive pathway evidence}
\usage{
export_policy_pathway_analysis(analysis, dir = ".",
  prefix = "catalyst-policy-pathway", zip_bundle = TRUE)
}
\arguments{
  \item{analysis}{A \code{catalyst_policy_pathway_analysis}.}
  \item{dir}{Parent output directory.}
  \item{prefix}{Bundle directory and archive prefix.}
  \item{zip_bundle}{Whether to create a ZIP archive.}
}
\value{A named list of generated file paths.}
\description{Writes canonical JSON, candidate and Pareto tables, feasible-region evidence, pathway sequence, trigger status, robustness, economic analyses, a Markdown brief, and a file-integrity manifest.}
