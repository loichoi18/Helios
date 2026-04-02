package com.helios.alerting.engine;

import com.helios.alerting.model.Alert;
import lombok.*;

import java.util.List;
import java.util.Map;

/**
 * A threshold-based alert rule loaded from YAML config.
 * Example rule:
 *   name: high-p99-latency
 *   metric: p99Latency
 *   threshold: 500.0
 *   severity: CRITICAL
 *   message: "p99 latency exceeded {threshold}ms (current: {value}ms)"
 */
@Getter
@Builder
@AllArgsConstructor
public class AlertRule {

    private final String name;
    private final String metric;       // field name on MetricSnapshot
    private final double threshold;
    private final Alert.Severity severity;
    private final String messageTemplate;

    /**
     * Evaluate this rule against a window of recent metric snapshots.
     * Returns true if the rule is breaching (average over window exceeds threshold).
     */
    public boolean isBreaching(List<Map<String, Double>> window) {
        if (window.isEmpty()) return false;
        double avg = window.stream()
                .filter(m -> m.containsKey(metric))
                .mapToDouble(m -> m.get(metric))
                .average()
                .orElse(0.0);
        return avg > threshold;
    }

    public String buildMessage(double currentValue) {
        return messageTemplate
                .replace("{threshold}", String.valueOf(threshold))
                .replace("{value}", String.format("%.2f", currentValue));
    }
}
