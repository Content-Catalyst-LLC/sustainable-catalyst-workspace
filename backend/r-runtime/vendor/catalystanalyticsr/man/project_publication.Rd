\name{project_publication}
\alias{decision_studio_handoff}
\alias{knowledge_library_handoff}
\alias{export_project_publication}
\title{Analytical publication and platform handoffs}
\description{Create portable publication bundles and governed first-party handoffs for Decision Studio and Knowledge Library using the shared platform-handoff contract.}
\usage{
decision_studio_handoff(project)

knowledge_library_handoff(project)

export_project_publication(project, dir = ".",
  prefix = "catalyst-analytical-project",
  formats = c("json", "csv", "markdown", "html", "quarto"),
  include_results = TRUE, include_plots = TRUE, zip_bundle = TRUE)
}
\arguments{
  \item{project}{A \code{catalyst_project}.}
  \item{dir}{Parent export directory.}
  \item{prefix}{Bundle directory and archive prefix.}
  \item{formats}{One or more of \code{json}, \code{csv}, \code{markdown}, \code{html}, and \code{quarto}.}
  \item{include_results}{Whether complete run result payloads are included.}
  \item{include_plots}{Whether registered plot files are copied.}
  \item{zip_bundle}{Whether to create a ZIP archive.}
}
\value{Handoff functions return JSON-safe records. The export function returns named output paths.}
\examples{
project <- catalyst_project("publication-demo", "Publication demo")
decision_studio_handoff(project)
knowledge_library_handoff(project)
}
