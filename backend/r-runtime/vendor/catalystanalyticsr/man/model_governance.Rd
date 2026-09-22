\name{model_governance}
\alias{parameter_card}
\alias{assumption_record}
\alias{limitation_record}
\alias{model_card}
\alias{model_governance_record}
\alias{transition_model_status}
\alias{model_governance_summary}
\alias{print.catalyst_model_card}
\alias{print.catalyst_model_governance}
\title{Model cards and lifecycle governance}
\usage{
parameter_card(id, title, description, unit = "unspecified", default = NA_real_,
  lower = NA_real_, upper = NA_real_, source = list(), calibrated = FALSE,
  sensitivity = "unknown", review_status = "unreviewed")
assumption_record(id, statement, rationale = "", evidence_refs = character(),
  owner = "unassigned", status = "open", review_due = NA_character_)
limitation_record(id, title, description, severity = c("low", "moderate", "high", "critical"),
  affected_uses = character(), mitigation = "", status = "open")
model_card(model = "khncpa", intended_uses, prohibited_uses, owner = "unassigned",
  methodology_refs = character(), parameters = list(), assumptions = list(),
  limitations = list(), calibration_evidence = character(), validation_evidence = character(),
  status = "experimental")
model_governance_record(card, reviewers = list(), approvals = list(), notes = list(), effective_date = NA_character_)
transition_model_status(governance, to_status, reviewer, note, date = .utc_now(), approval = NULL)
model_governance_summary(x)
\method{print}{catalyst_model_card}(x, ...)
\method{print}{catalyst_model_governance}(x, ...)
}
\arguments{
\item{id}{Stable record identifier.}
\item{title}{Human-readable title.}
\item{description}{Detailed description.}
\item{unit}{Unit of measure.}
\item{default}{Default parameter value.}
\item{lower}{Lower bound.}
\item{upper}{Upper bound.}
\item{source}{Source record.}
\item{calibrated}{Whether the parameter is calibrated.}
\item{sensitivity}{Sensitivity classification.}
\item{review_status}{Review status.}
\item{statement}{Assumption statement.}
\item{rationale}{Assumption rationale.}
\item{evidence_refs}{Evidence references.}
\item{owner}{Responsible owner.}
\item{status}{Record or lifecycle status.}
\item{review_due}{Optional review date.}
\item{severity}{Limitation severity.}
\item{affected_uses}{Uses affected by a limitation.}
\item{mitigation}{Mitigation guidance.}
\item{model}{Registered model or model id.}
\item{intended_uses}{Intended model uses.}
\item{prohibited_uses}{Prohibited model uses.}
\item{methodology_refs}{Methodology references.}
\item{parameters}{Parameter cards.}
\item{assumptions}{Assumption records.}
\item{limitations}{Limitation records.}
\item{calibration_evidence}{Calibration evidence references.}
\item{validation_evidence}{Validation evidence references.}
\item{card}{A model card.}
\item{reviewers}{Reviewer records.}
\item{approvals}{Approval records.}
\item{notes}{Review notes.}
\item{effective_date}{Effective date.}
\item{governance}{Governance record.}
\item{to_status}{Target lifecycle state.}
\item{reviewer}{Responsible reviewer.}
\item{note}{Transition rationale.}
\item{date}{Transition timestamp.}
\item{approval}{Optional approval record.}
\item{x}{A governance record.}
\item{...}{Additional method arguments.}
}
\value{Governed parameter, assumption, limitation, model-card, lifecycle, or summary records.}
\description{Documents model use boundaries and manages transitions among experimental, under-review, validated-for-specified-use, deprecated, and archived states.}
