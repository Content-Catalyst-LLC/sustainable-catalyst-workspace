.catalyst_model_governance_schema_version <- function() "1.0.0"
.model_lifecycle_states <- function() c("experimental", "under_review", "validated_for_specified_use", "deprecated", "archived")

#' Create a governed parameter card
#'
#' @param id Stable parameter identifier.
#' @param title Human-readable title.
#' @param description Parameter meaning.
#' @param unit Unit of measure.
#' @param default Default value.
#' @param lower Optional lower bound.
#' @param upper Optional upper bound.
#' @param source Evidence or methodology source.
#' @param calibrated Whether the parameter is estimated through calibration.
#' @param sensitivity Sensitivity classification.
#' @param review_status Review status.
#' @return A parameter-card record.
#' @export
parameter_card <- function(id, title, description, unit = "unspecified", default = NA_real_, lower = NA_real_, upper = NA_real_, source = list(), calibrated = FALSE, sensitivity = "unknown", review_status = "unreviewed") {
  .validate_dataset_id(id, "id"); .assert_single_string(title, "title"); .assert_single_string(description, "description")
  .assert_single_string(unit, "unit"); .assert_flag(calibrated, "calibrated"); .assert_single_string(sensitivity, "sensitivity"); .assert_single_string(review_status, "review_status")
  if (!is.list(source)) stop("`source` must be a list.", call. = FALSE)
  list(schema_version = "1.0.0", id = id, title = title, description = description, unit = unit, default = default, bounds = list(lower = lower, upper = upper), source = source, calibrated = calibrated, sensitivity = sensitivity, review_status = review_status)
}

#' Create a governed assumption record
#'
#' @param id Stable assumption identifier.
#' @param statement Assumption statement.
#' @param rationale Rationale.
#' @param evidence_refs Evidence identifiers.
#' @param owner Responsible owner.
#' @param status Status.
#' @param review_due Optional review date.
#' @return An assumption record.
#' @export
assumption_record <- function(id, statement, rationale = "", evidence_refs = character(), owner = "unassigned", status = "open", review_due = NA_character_) {
  .validate_dataset_id(id, "id"); .assert_single_string(statement, "statement"); .assert_single_string(rationale, "rationale", allow_empty = TRUE); .assert_single_string(owner, "owner"); .assert_single_string(status, "status")
  list(schema_version = "1.0.0", id = id, statement = statement, rationale = rationale, evidence_refs = as.character(evidence_refs), owner = owner, status = status, review_due = review_due)
}

#' Create a known model limitation
#'
#' @param id Stable limitation identifier.
#' @param title Limitation title.
#' @param description Detailed limitation.
#' @param severity Severity.
#' @param affected_uses Affected uses.
#' @param mitigation Mitigation or interpretation guidance.
#' @param status Status.
#' @return A limitation record.
#' @export
limitation_record <- function(id, title, description, severity = c("low", "moderate", "high", "critical"), affected_uses = character(), mitigation = "", status = "open") {
  severity <- match.arg(severity); .validate_dataset_id(id, "id"); .assert_single_string(title, "title"); .assert_single_string(description, "description"); .assert_single_string(mitigation, "mitigation", allow_empty = TRUE); .assert_single_string(status, "status")
  list(schema_version = "1.0.0", id = id, title = title, description = description, severity = severity, affected_uses = as.character(affected_uses), mitigation = mitigation, status = status)
}

#' Create a model card
#'
#' @param model Registered model id or model object.
#' @param intended_uses Intended uses.
#' @param prohibited_uses Prohibited uses.
#' @param owner Model owner.
#' @param methodology_refs Methodology references.
#' @param parameters Parameter cards.
#' @param assumptions Assumption records.
#' @param limitations Limitation records.
#' @param calibration_evidence Calibration evidence references.
#' @param validation_evidence Validation evidence references.
#' @param status Lifecycle status.
#' @return A `catalyst_model_card`.
#' @export
model_card <- function(model = "khncpa", intended_uses, prohibited_uses, owner = "unassigned", methodology_refs = character(), parameters = list(), assumptions = list(), limitations = list(), calibration_evidence = character(), validation_evidence = character(), status = "experimental") {
  model <- .resolve_catalyst_model(model, NULL)
  if (!status %in% .model_lifecycle_states()) stop("Invalid model lifecycle status.", call. = FALSE)
  .assert_single_string(owner, "owner")
  structure(list(
    schema_version = "1.0.0", model = list(id = model$id, version = model$version, title = model$title, description = model$description),
    intended_uses = as.character(intended_uses), prohibited_uses = as.character(prohibited_uses), owner = owner,
    methodology_refs = as.character(methodology_refs), parameters = parameters, assumptions = assumptions, limitations = limitations,
    evidence = list(calibration = as.character(calibration_evidence), validation = as.character(validation_evidence)),
    lifecycle_status = status, created_at = .utc_now(), updated_at = .utc_now()
  ), class = "catalyst_model_card")
}

#' Create a model governance record
#'
#' @param card A `catalyst_model_card`.
#' @param reviewers Reviewer records or names.
#' @param approvals Approval records.
#' @param notes Review notes.
#' @param effective_date Effective date.
#' @return A `catalyst_model_governance` record.
#' @export
model_governance_record <- function(card, reviewers = list(), approvals = list(), notes = list(), effective_date = NA_character_) {
  if (!inherits(card, "catalyst_model_card")) stop("`card` must be a model card.", call. = FALSE)
  structure(list(
    schema_version = .catalyst_model_governance_schema_version(), governance_id = paste0(card$model$id, "-", card$model$version, "-governance"),
    model_card = card, lifecycle_status = card$lifecycle_status, reviewers = reviewers, approvals = approvals, notes = notes,
    transition_history = list(list(from = NA_character_, to = card$lifecycle_status, reviewer = "system", note = "Initial governance record", date = .utc_now())),
    effective_date = effective_date, updated_at = .utc_now()
  ), class = "catalyst_model_governance")
}

.allowed_transition <- function(from, to) {
  allowed <- list(
    experimental = c("under_review", "archived"),
    under_review = c("experimental", "validated_for_specified_use", "deprecated", "archived"),
    validated_for_specified_use = c("under_review", "deprecated", "archived"),
    deprecated = c("under_review", "archived"),
    archived = character()
  )
  to %in% allowed[[from]]
}

#' Transition a model governance lifecycle state
#'
#' @param governance A governance record.
#' @param to_status Target lifecycle state.
#' @param reviewer Reviewer responsible for the transition.
#' @param note Transition rationale.
#' @param date Transition date.
#' @param approval Optional approval record.
#' @return Updated governance record.
#' @export
transition_model_status <- function(governance, to_status, reviewer, note, date = .utc_now(), approval = NULL) {
  if (!inherits(governance, "catalyst_model_governance")) stop("`governance` must be a governance record.", call. = FALSE)
  .assert_single_string(to_status, "to_status"); .assert_single_string(reviewer, "reviewer"); .assert_single_string(note, "note")
  if (!to_status %in% .model_lifecycle_states()) stop("Invalid target lifecycle status.", call. = FALSE)
  from <- governance$lifecycle_status
  if (!.allowed_transition(from, to_status)) stop(sprintf("Lifecycle transition from `%s` to `%s` is not allowed.", from, to_status), call. = FALSE)
  if (to_status == "validated_for_specified_use" && (length(governance$model_card$evidence$calibration) == 0L || length(governance$model_card$evidence$validation) == 0L)) {
    stop("Validated status requires calibration and validation evidence.", call. = FALSE)
  }
  governance$lifecycle_status <- to_status
  governance$model_card$lifecycle_status <- to_status
  governance$model_card$updated_at <- date
  governance$transition_history[[length(governance$transition_history) + 1L]] <- list(from = from, to = to_status, reviewer = reviewer, note = note, date = date)
  governance$notes[[length(governance$notes) + 1L]] <- list(reviewer = reviewer, note = note, date = date)
  if (!is.null(approval)) governance$approvals[[length(governance$approvals) + 1L]] <- approval
  governance$updated_at <- date
  governance
}

#' Summarize model governance readiness
#'
#' @param x A governance record.
#' @return One-row governance summary.
#' @export
model_governance_summary <- function(x) {
  if (!inherits(x, "catalyst_model_governance")) stop("`x` must be a governance record.", call. = FALSE)
  data.frame(
    governance_id = x$governance_id, model_id = x$model_card$model$id, model_version = x$model_card$model$version,
    lifecycle_status = x$lifecycle_status, parameter_cards = length(x$model_card$parameters), assumptions = length(x$model_card$assumptions),
    open_limitations = sum(vapply(x$model_card$limitations, function(item) !identical(item$status, "closed"), logical(1))),
    reviewers = length(x$reviewers), approvals = length(x$approvals), transitions = length(x$transition_history),
    calibration_evidence = length(x$model_card$evidence$calibration), validation_evidence = length(x$model_card$evidence$validation), stringsAsFactors = FALSE
  )
}

#' @export
print.catalyst_model_card <- function(x, ...) {
  cat(sprintf("<catalyst_model_card %s@%s>\n", x$model$id, x$model$version))
  cat(sprintf("  status: %s\n", x$lifecycle_status))
  cat(sprintf("  limitations: %d\n", length(x$limitations)))
  invisible(x)
}

#' @export
print.catalyst_model_governance <- function(x, ...) {
  summary <- model_governance_summary(x)
  cat(sprintf("<catalyst_model_governance %s>\n", x$governance_id))
  cat(sprintf("  lifecycle: %s\n", summary$lifecycle_status))
  cat(sprintf("  approvals: %d\n", summary$approvals))
  invisible(x)
}
