\name{export_institutional_governance}
\alias{export_institutional_governance}
\alias{workspace_add_institutional_governance}
\alias{workspace_get_institutional_governance}
\title{Export and store institutional governance workflows}
\usage{
export_institutional_governance(
  workflow,
  dir = ".",
  prefix = "catalyst-institutional-governance",
  zip_bundle = TRUE
)

workspace_add_institutional_governance(workspace, workflow, replace = FALSE)

workspace_get_institutional_governance(workspace, workflow_id)
}
\arguments{
  \item{workflow}{Institutional governance workflow.}
  \item{dir}{Destination directory.}
  \item{prefix}{Bundle prefix.}
  \item{zip_bundle}{Create a ZIP bundle.}
  \item{workspace}{Persistent workspace.}
  \item{replace}{Replace an existing workflow.}
  \item{workflow_id}{Workflow identifier.}
}
\value{Generated paths, an updated workspace, or a stored workflow.}
\description{Exports review, approval, signature, audit, access, and retention records and stores reusable governance workflows in persistent workspaces.}
