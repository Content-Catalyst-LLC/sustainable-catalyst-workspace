\name{workspace_policy_evaluations}
\alias{workspace_add_policy_evaluation}
\alias{workspace_get_policy_evaluation}
\title{Workspace policy-evaluation library}
\description{
Stores and retrieves governed policy-evaluation summaries in persistent
analytical workspaces.
}
\usage{
workspace_add_policy_evaluation(workspace, analysis, replace = FALSE)

workspace_get_policy_evaluation(workspace, evaluation_id)
}
\arguments{
  \item{workspace}{A workspace.}
  \item{analysis}{A policy-evaluation analysis.}
  \item{replace}{Replace an existing record.}
  \item{evaluation_id}{Evaluation identifier.}
}
\value{
An updated workspace or stored evaluation record.
}
\keyword{utilities}
