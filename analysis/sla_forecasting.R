# helios/analysis/sla_forecasting.R
# ──────────────────────────────────────────────────────────────────────────────
# ARIMA-based SLA compliance forecasting.
#
# Reads 90 days of daily SLA % data, fits auto.arima with weekly seasonality,
# and produces a 30-day forward forecast with 80% and 95% confidence intervals.
#
# Output: analysis/output/sla_forecast.png
#
# Usage:
#   Rscript sla_forecasting.R
# ──────────────────────────────────────────────────────────────────────────────

suppressPackageStartupMessages({
  library(forecast)
  library(ggplot2)
  library(dplyr)
  library(lubridate)
  library(readr)
})

# ── 1. Load data ──────────────────────────────────────────────────────────────

sla_raw <- read_csv("data/metrics_sample.csv", show_col_types = FALSE) |>
  mutate(date = as_date(date)) |>
  arrange(date)

cat(sprintf("Loaded %d daily SLA observations (%s → %s)\n",
            nrow(sla_raw), min(sla_raw$date), max(sla_raw$date)))

# ── 2. Build time series (frequency = 7 for weekly seasonality) ───────────────

sla_ts <- ts(sla_raw$sla_percent, frequency = 7)

# ── 3. Fit ARIMA ──────────────────────────────────────────────────────────────

cat("Fitting auto.arima (stepwise=FALSE for exhaustive search)…\n")
fit <- auto.arima(
  sla_ts,
  seasonal    = TRUE,
  stepwise    = FALSE,   # exhaustive search for best model
  approximation = FALSE,
  ic          = "aicc"   # corrected AIC avoids overfitting on small samples
)

cat("Best model: ", as.character(fit), "\n")
cat(sprintf("AICc: %.2f  |  BIC: %.2f\n", fit$aicc, fit$bic))

# ── 4. Diagnostic checks ─────────────────────────────────────────────────────

# Ljung-Box test on residuals: p > 0.05 → no significant autocorrelation left
lb <- Box.test(residuals(fit), lag = 14, type = "Ljung-Box")
cat(sprintf("Ljung-Box Q(14) p-value: %.4f %s\n",
            lb$p.value,
            ifelse(lb$p.value > 0.05, "(✓ residuals look white noise)", "(⚠ autocorrelation remains)")))

# ── 5. Forecast 30 days ahead ─────────────────────────────────────────────────

fc <- forecast(fit, h = 30, level = c(80, 95))

# ── 6. Plot ───────────────────────────────────────────────────────────────────

dir.create("output", showWarnings = FALSE)

p <- autoplot(fc) +
  geom_hline(
    yintercept = 99.9,
    linetype = "dashed",
    colour = "#f85149",
    linewidth = 0.7
  ) +
  geom_hline(
    yintercept = 99.0,
    linetype = "dotted",
    colour = "#d29922",
    linewidth = 0.6
  ) +
  annotate("text", x = length(sla_ts) + 28, y = 99.92,
           label = "99.9% SLO", colour = "#f85149", size = 3.2, hjust = 1) +
  annotate("text", x = length(sla_ts) + 28, y = 99.02,
           label = "99% floor", colour = "#d29922", size = 3.2, hjust = 1) +
  scale_y_continuous(limits = c(98.5, 100.1), labels = function(x) paste0(x, "%")) +
  labs(
    title    = "30-Day SLA Compliance Forecast",
    subtitle = sprintf("Model: %s | AICc: %.1f", as.character(fit), fit$aicc),
    x        = "Day",
    y        = "SLA Compliance (%)",
    caption  = "Shaded bands: 80% and 95% prediction intervals"
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title    = element_text(face = "bold"),
    plot.subtitle = element_text(colour = "grey50", size = 10),
    panel.grid.minor = element_blank()
  )

ggsave("output/sla_forecast.png", p, width = 10, height = 5.5, dpi = 180)
cat("Saved: output/sla_forecast.png\n")

# ── 7. Print forecast table ───────────────────────────────────────────────────

fc_df <- data.frame(
  day     = seq_len(30),
  point   = as.numeric(fc$mean),
  lo_80   = fc$lower[, 1],
  hi_80   = fc$upper[, 1],
  lo_95   = fc$lower[, 2],
  hi_95   = fc$upper[, 2]
)

below_slo <- fc_df |> filter(lo_95 < 99.9) |> nrow()
cat(sprintf("\nForecast: %d of 30 days have 95%% CI lower bound < 99.9%% SLO\n", below_slo))
print(head(fc_df, 10), digits = 4)
