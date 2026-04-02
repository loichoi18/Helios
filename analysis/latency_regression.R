# helios/analysis/latency_regression.R
# ──────────────────────────────────────────────────────────────────────────────
# Multiple linear regression: what factors drive p99 latency?
#
# Predictors: request_rate, deploy_count, hour_of_day, is_weekend, error_rate
# Response:   p99_latency (ms)
#
# Output:
#   - Model summary printed to console
#   - Coefficient plot saved to output/latency_regression_coefs.png
#   - Residual diagnostics saved to output/latency_residuals.png
# ──────────────────────────────────────────────────────────────────────────────

suppressPackageStartupMessages({
  library(tidyverse)
  library(broom)
  library(corrplot)
  library(scales)
})

# ── 1. Load & prepare data ────────────────────────────────────────────────────

metrics <- read_csv("data/metrics_sample.csv", show_col_types = FALSE) |>
  mutate(
    date       = as_datetime(date),
    hour_of_day = hour(date),
    is_weekend  = as.integer(wday(date) %in% c(1, 7)),
    # Bin request rate into log scale to handle skew
    log_rps    = log1p(request_rate)
  ) |>
  filter(!is.na(p99_latency), p99_latency > 0)

cat(sprintf("Dataset: %d observations\n", nrow(metrics)))
cat(sprintf("p99 latency — mean: %.0fms  sd: %.0fms  max: %.0fms\n",
            mean(metrics$p99_latency),
            sd(metrics$p99_latency),
            max(metrics$p99_latency)))

# ── 2. Correlation matrix ─────────────────────────────────────────────────────

dir.create("output", showWarnings = FALSE)

num_vars <- metrics |>
  select(p99_latency, request_rate, deploy_count, hour_of_day, is_weekend, error_rate)

cor_matrix <- cor(num_vars, use = "complete.obs")
cat("\nCorrelation matrix:\n")
print(round(cor_matrix, 3))

png("output/correlation_matrix.png", width = 700, height = 600, res = 120)
corrplot(cor_matrix,
         method = "color", type = "upper",
         tl.col = "black", tl.srt = 45,
         addCoef.col = "black", number.cex = 0.75,
         title = "Helios Metric Correlations", mar = c(0, 0, 2, 0))
dev.off()
cat("Saved: output/correlation_matrix.png\n")

# ── 3. Fit linear model ───────────────────────────────────────────────────────

model <- lm(
  p99_latency ~ log_rps + deploy_count + hour_of_day + is_weekend + error_rate,
  data = metrics
)

cat("\n── Model Summary ────────────────────────────────────────────────────────\n")
summary(model)

tidy_model <- tidy(model, conf.int = TRUE)
glance_model <- glance(model)

cat(sprintf("\nR² = %.4f  |  Adj R² = %.4f  |  F-statistic p = %.2e\n",
            glance_model$r.squared,
            glance_model$adj.r.squared,
            glance_model$p.value))

# ── 4. Coefficient plot ───────────────────────────────────────────────────────

coef_plot <- tidy_model |>
  filter(term != "(Intercept)") |>
  mutate(
    term      = recode(term,
                       log_rps      = "Log(Request Rate)",
                       deploy_count = "Deploy Count",
                       hour_of_day  = "Hour of Day",
                       is_weekend   = "Is Weekend",
                       error_rate   = "Error Rate"),
    significant = p.value < 0.05
  ) |>
  ggplot(aes(x = estimate, y = reorder(term, estimate), colour = significant)) +
  geom_vline(xintercept = 0, linetype = "dashed", colour = "grey50") +
  geom_errorbarh(aes(xmin = conf.low, xmax = conf.high), height = 0.2, linewidth = 0.8) +
  geom_point(size = 3) +
  scale_colour_manual(values = c("FALSE" = "grey60", "TRUE" = "#f85149"),
                      labels = c("p ≥ 0.05", "p < 0.05")) +
  labs(
    title    = "Predictors of p99 Latency",
    subtitle = sprintf("Multiple linear regression | R² = %.3f", glance_model$r.squared),
    x        = "Coefficient estimate (ms per unit increase)",
    y        = NULL,
    colour   = "Significance"
  ) +
  theme_minimal(base_size = 12) +
  theme(legend.position = "bottom", plot.title = element_text(face = "bold"))

ggsave("output/latency_regression_coefs.png", coef_plot, width = 8, height = 4.5, dpi = 180)
cat("Saved: output/latency_regression_coefs.png\n")

# ── 5. Residual diagnostics ───────────────────────────────────────────────────

png("output/latency_residuals.png", width = 900, height = 700, res = 120)
par(mfrow = c(2, 2))
plot(model, which = 1:4)
dev.off()
cat("Saved: output/latency_residuals.png\n")

# ── 6. Key insights ───────────────────────────────────────────────────────────

cat("\n── Key Insights ─────────────────────────────────────────────────────────\n")
sig <- tidy_model |> filter(p.value < 0.05, term != "(Intercept)") |> arrange(desc(abs(estimate)))
for (i in seq_len(nrow(sig))) {
  row <- sig[i, ]
  direction <- if (row$estimate > 0) "increases" else "decreases"
  cat(sprintf("• %s %s p99 by %.1fms per unit (p=%.4f)\n",
              row$term, direction, abs(row$estimate), row$p.value))
}
