args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("expected input and output JSON paths")
input_path <- args[[1]]
output_path <- args[[2]]

`%||%` <- function(x, y) if (is.null(x)) y else x

doc <- jsonlite::fromJSON(input_path, simplifyVector = TRUE, simplifyDataFrame = TRUE)
op <- as.character(doc$operation %||% "")
payload <- doc$payload

allowed_ops <- c(
  "workspace.polyglot.r.describe",
  "workspace.polyglot.r.t-test",
  "workspace.polyglot.r.correlation",
  "workspace.polyglot.r.linear-model",
  "workspace.polyglot.r.logistic-model",
  "workspace.polyglot.r.anova",
  "workspace.polyglot.r.arima",
  "workspace.polyglot.r.econometric-ols"
)
if (!(op %in% allowed_ops)) stop("R operation is not registered")

safe_name <- function(x) {
  is.character(x) && length(x) == 1 && grepl("^[A-Za-z][A-Za-z0-9_]{0,63}$", x)
}

rows_to_frame <- function(rows) {
  if (is.null(rows)) stop("rows are required")
  if (is.data.frame(rows)) return(rows)
  frame <- as.data.frame(rows, stringsAsFactors = FALSE, check.names = FALSE)
  if (nrow(frame) > 50000) stop("R row limit exceeded")
  if (ncol(frame) > 256) stop("R column limit exceeded")
  frame
}

require_column <- function(df, name) {
  if (!safe_name(name) || !(name %in% colnames(df))) stop(paste("invalid column", name))
  name
}

require_predictors <- function(df, predictors) {
  predictors <- as.character(predictors %||% character(0))
  if (length(predictors) < 1 || length(predictors) > 64) stop("predictors must contain 1-64 columns")
  for (p in predictors) require_column(df, p)
  unique(predictors)
}

finite_numeric <- function(x, label) {
  x <- suppressWarnings(as.numeric(x))
  x <- x[is.finite(x)]
  if (length(x) < 2) stop(paste(label, "requires at least two finite numeric values"))
  x
}

coef_table <- function(model) {
  tab <- summary(model)$coefficients
  out <- vector("list", nrow(tab))
  for (i in seq_len(nrow(tab))) {
    out[[i]] <- list(
      term = rownames(tab)[[i]],
      estimate = unname(tab[i, 1]),
      stdError = unname(tab[i, 2]),
      statistic = unname(tab[i, 3]),
      pValue = unname(tab[i, 4])
    )
  }
  out
}

lm_result <- function(df, outcome, predictors, econometric = FALSE) {
  outcome <- require_column(df, outcome)
  predictors <- require_predictors(df, predictors)
  if (!is.numeric(df[[outcome]])) df[[outcome]] <- suppressWarnings(as.numeric(df[[outcome]]))
  model <- stats::lm(stats::reformulate(predictors, response = outcome), data = df, na.action = stats::na.omit)
  s <- summary(model)
  result <- list(
    kind = if (econometric) "econometric-ols" else "linear-model",
    outcome = outcome,
    predictors = predictors,
    coefficients = coef_table(model),
    metrics = list(
      n = length(stats::residuals(model)),
      rSquared = unname(s$r.squared),
      adjustedRSquared = unname(s$adj.r.squared),
      sigma = unname(s$sigma),
      aic = unname(stats::AIC(model)),
      bic = unname(stats::BIC(model))
    )
  )
  if (econometric) {
    e <- stats::residuals(model)
    fitted <- stats::fitted(model)
    dw <- if (sum(e^2) > 0) sum(diff(e)^2) / sum(e^2) else NA_real_
    aux <- stats::lm(I(e^2) ~ fitted)
    bp_stat <- length(e) * summary(aux)$r.squared
    bp_p <- stats::pchisq(bp_stat, df = 1, lower.tail = FALSE)
    centered <- e - mean(e)
    m2 <- mean(centered^2)
    skew <- if (m2 > 0) mean(centered^3) / (m2^(3/2)) else NA_real_
    kurt <- if (m2 > 0) mean(centered^4) / (m2^2) else NA_real_
    jb <- if (is.finite(skew) && is.finite(kurt)) length(e) / 6 * (skew^2 + ((kurt - 3)^2) / 4) else NA_real_
    result$diagnostics <- list(
      durbinWatson = unname(dw),
      breuschPagan = list(statistic = unname(bp_stat), pValue = unname(bp_p)),
      jarqueBera = list(statistic = unname(jb), pValue = if (is.finite(jb)) unname(stats::pchisq(jb, df = 2, lower.tail = FALSE)) else NA_real_)
    )
  }
  result
}

result <- switch(op,
  "workspace.polyglot.r.describe" = {
    df <- rows_to_frame(payload$rows)
    requested <- as.character(payload$columns %||% colnames(df))
    requested <- requested[requested %in% colnames(df)]
    stats_out <- list()
    for (name in requested) {
      if (!is.numeric(df[[name]])) next
      x <- finite_numeric(df[[name]], name)
      q <- stats::quantile(x, probs = c(0.25, 0.5, 0.75), names = FALSE, na.rm = TRUE)
      stats_out[[name]] <- list(n = length(x), mean = mean(x), sd = stats::sd(x), min = min(x), q1 = q[[1]], median = q[[2]], q3 = q[[3]], max = max(x))
    }
    list(kind = "describe", columns = stats_out, rowCount = nrow(df))
  },
  "workspace.polyglot.r.t-test" = {
    df <- rows_to_frame(payload$rows)
    column <- require_column(df, as.character(payload$column %||% ""))
    alternative <- as.character(payload$alternative %||% "two.sided")
    if (!(alternative %in% c("two.sided", "less", "greater"))) stop("unsupported alternative")
    conf <- as.numeric(payload$confLevel %||% 0.95)
    if (!is.finite(conf) || conf <= 0.5 || conf >= 0.9999) stop("invalid confidence level")
    group <- as.character(payload$groupBy %||% "")
    if (nzchar(group)) {
      group <- require_column(df, group)
      levels <- unique(as.character(df[[group]]))
      levels <- levels[!is.na(levels)]
      if (length(levels) != 2) stop("grouped t-test requires exactly two groups")
      a <- finite_numeric(df[df[[group]] == levels[[1]], column], "group A")
      b <- finite_numeric(df[df[[group]] == levels[[2]], column], "group B")
      tt <- stats::t.test(a, b, alternative = alternative, conf.level = conf)
      list(kind = "t-test", column = column, groups = levels, estimate = unname(tt$estimate), statistic = unname(tt$statistic), parameter = unname(tt$parameter), pValue = unname(tt$p.value), confInt = unname(tt$conf.int))
    } else {
      x <- finite_numeric(df[[column]], column)
      mu <- as.numeric(payload$mu %||% 0)
      tt <- stats::t.test(x, mu = mu, alternative = alternative, conf.level = conf)
      list(kind = "t-test", column = column, mu = mu, estimate = unname(tt$estimate), statistic = unname(tt$statistic), parameter = unname(tt$parameter), pValue = unname(tt$p.value), confInt = unname(tt$conf.int))
    }
  },
  "workspace.polyglot.r.correlation" = {
    df <- rows_to_frame(payload$rows)
    x_name <- require_column(df, as.character(payload$x %||% ""))
    y_name <- require_column(df, as.character(payload$y %||% ""))
    method <- as.character(payload$method %||% "pearson")
    if (!(method %in% c("pearson", "spearman", "kendall"))) stop("unsupported correlation method")
    pair <- stats::na.omit(data.frame(x = as.numeric(df[[x_name]]), y = as.numeric(df[[y_name]])))
    if (nrow(pair) < 3) stop("correlation requires at least three complete pairs")
    ct <- stats::cor.test(pair$x, pair$y, method = method, exact = FALSE)
    list(kind = "correlation", x = x_name, y = y_name, method = method, n = nrow(pair), estimate = unname(ct$estimate), statistic = unname(ct$statistic), pValue = unname(ct$p.value), confInt = if (!is.null(ct$conf.int)) unname(ct$conf.int) else NULL)
  },
  "workspace.polyglot.r.linear-model" = {
    df <- rows_to_frame(payload$rows)
    lm_result(df, as.character(payload$outcome %||% ""), payload$predictors, FALSE)
  },
  "workspace.polyglot.r.logistic-model" = {
    df <- rows_to_frame(payload$rows)
    outcome <- require_column(df, as.character(payload$outcome %||% ""))
    predictors <- require_predictors(df, payload$predictors)
    y <- df[[outcome]]
    if (is.logical(y)) y <- as.integer(y)
    y <- suppressWarnings(as.numeric(y))
    if (!all(stats::na.omit(y) %in% c(0, 1))) stop("logistic outcome must be binary 0/1")
    df[[outcome]] <- y
    model <- stats::glm(stats::reformulate(predictors, response = outcome), data = df, family = stats::binomial(), na.action = stats::na.omit)
    s <- summary(model)
    list(kind = "logistic-model", outcome = outcome, predictors = predictors, coefficients = coef_table(model), metrics = list(n = stats::nobs(model), deviance = unname(stats::deviance(model)), nullDeviance = unname(model$null.deviance), aic = unname(stats::AIC(model)), bic = unname(stats::BIC(model)), converged = isTRUE(model$converged)))
  },
  "workspace.polyglot.r.anova" = {
    df <- rows_to_frame(payload$rows)
    outcome <- require_column(df, as.character(payload$outcome %||% ""))
    factor_name <- require_column(df, as.character(payload$factor %||% ""))
    df[[factor_name]] <- as.factor(df[[factor_name]])
    model <- stats::aov(stats::reformulate(factor_name, response = outcome), data = df, na.action = stats::na.omit)
    tab <- summary(model)[[1]]
    list(kind = "anova", outcome = outcome, factor = factor_name, dfBetween = unname(tab[1, "Df"]), dfWithin = unname(tab[2, "Df"]), sumSqBetween = unname(tab[1, "Sum Sq"]), sumSqWithin = unname(tab[2, "Sum Sq"]), fValue = unname(tab[1, "F value"]), pValue = unname(tab[1, "Pr(>F)"]))
  },
  "workspace.polyglot.r.arima" = {
    df <- rows_to_frame(payload$rows)
    column <- require_column(df, as.character(payload$column %||% ""))
    x <- finite_numeric(df[[column]], column)
    if (length(x) < 8) stop("ARIMA requires at least eight observations")
    order <- as.integer(payload$order %||% c(1, 0, 0))
    if (length(order) != 3 || any(order < 0) || any(order > 5) || sum(order) > 10) stop("invalid bounded ARIMA order")
    include_mean <- isTRUE(payload$includeMean %||% TRUE)
    model <- stats::arima(x, order = order, include.mean = include_mean, method = "ML")
    list(kind = "arima", column = column, order = as.list(order), coefficients = as.list(unname(model$coef)), coefficientNames = names(model$coef), sigma2 = unname(model$sigma2), aic = unname(model$aic), n = length(x))
  },
  "workspace.polyglot.r.econometric-ols" = {
    df <- rows_to_frame(payload$rows)
    lm_result(df, as.character(payload$outcome %||% ""), payload$predictors, TRUE)
  },
  stop("unsupported R operation")
)

out <- list(
  ok = TRUE,
  schema = "sc-workspace-r-runtime-result/1.0",
  runtime = "r-statistical-econometric",
  runtimeVersion = paste(R.version$major, R.version$minor, sep = "."),
  operation = op,
  boundedOperationsOnly = TRUE,
  arbitraryCodeExecution = FALSE,
  result = result
)
jsonlite::write_json(out, output_path, auto_unbox = TRUE, digits = 15, na = "null", null = "null", pretty = FALSE)
