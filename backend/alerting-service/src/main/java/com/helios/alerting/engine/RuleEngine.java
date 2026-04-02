package com.helios.alerting.engine;

import com.helios.alerting.model.Alert;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Core evaluation engine: applies a set of AlertRules to a sliding metric window
 * and returns all currently-firing alerts.
 */
@Component
@Slf4j
public class RuleEngine {

    private final List<AlertRule> rules;

    public RuleEngine() {
        // Rules are hardcoded here for clarity; in production these would be loaded
        // from a YAML file or a database, making them operator-configurable at runtime.
        this.rules = List.of(
            AlertRule.builder()
                .name("high-p99-latency")
                .metric("p99Latency")
                .threshold(500.0)
                .severity(Alert.Severity.CRITICAL)
                .messageTemplate("p99 latency is {value}ms — SLO threshold is {threshold}ms")
                .build(),

            AlertRule.builder()
                .name("elevated-error-rate")
                .metric("errorRate")
                .threshold(0.05)
                .severity(Alert.Severity.WARNING)
                .messageTemplate("Error rate is {value} — threshold is {threshold}")
                .build(),

            AlertRule.builder()
                .name("high-p95-latency")
                .metric("p95Latency")
                .threshold(300.0)
                .severity(Alert.Severity.WARNING)
                .messageTemplate("p95 latency is {value}ms — warning threshold is {threshold}ms")
                .build()
        );
    }

    /**
     * Evaluate all rules against the provided metric window.
     *
     * @param serviceName The service being evaluated
     * @param window      Recent metric snapshots as key→value maps
     * @return List of firing alerts (empty = healthy)
     */
    public List<Alert> evaluate(String serviceName, List<Map<String, Double>> window) {
        List<Alert> fired = rules.stream()
                .filter(rule -> rule.isBreaching(window))
                .map(rule -> {
                    double current = window.stream()
                            .mapToDouble(m -> m.getOrDefault(rule.getMetric(), 0.0))
                            .average()
                            .orElse(0.0);
                    log.warn("ALERT fired: rule={} service={} value={}",
                             rule.getName(), serviceName, current);
                    return Alert.builder()
                            .ruleName(rule.getName())
                            .severity(rule.getSeverity())
                            .firedAt(Instant.now())
                            .message(rule.buildMessage(current))
                            .serviceName(serviceName)
                            .build();
                })
                .collect(Collectors.toList());

        if (!fired.isEmpty()) {
            log.info("Evaluation complete: {} alert(s) firing for service={}",
                     fired.size(), serviceName);
        }
        return fired;
    }
}
