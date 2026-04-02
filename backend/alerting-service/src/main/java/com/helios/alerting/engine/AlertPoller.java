package com.helios.alerting.engine;

import com.helios.alerting.model.Alert;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Periodically polls the metrics service, evaluates alert rules,
 * and logs any firing alerts. In a real deployment this would
 * dispatch to SNS / PagerDuty / Slack.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class AlertPoller {

    private final RuleEngine ruleEngine;
    private final RestClient.Builder restClientBuilder;

    private static final String METRICS_URL =
            "${METRICS_SERVICE_URL:http://localhost:8080}/api/metrics/recent?minutes=5";

    @Scheduled(fixedDelay = 60_000)
    public void poll() {
        try {
            RestClient client = restClientBuilder.build();

            // Fetch recent metric events grouped per service
            Map<?, ?>[] events = client.get()
                    .uri(METRICS_URL)
                    .retrieve()
                    .body(Map[].class);

            if (events == null || events.length == 0) return;

            // Group by service name
            Map<String, List<Map<String, Double>>> byService = new HashMap<>();
            for (Map<?, ?> evt : events) {
                String svc = (String) evt.get("serviceName");
                Map<String, Double> numeric = new HashMap<>();
                numeric.put("p99Latency",  toDouble(evt.get("p99Latency")));
                numeric.put("p95Latency",  toDouble(evt.get("p95Latency")));
                numeric.put("errorRate",   toDouble(evt.get("errorRate")));
                numeric.put("requestRate", toDouble(evt.get("requestRate")));
                byService.computeIfAbsent(svc, k -> new java.util.ArrayList<>()).add(numeric);
            }

            // Evaluate rules per service
            byService.forEach((service, window) -> {
                List<Alert> alerts = ruleEngine.evaluate(service, window);
                alerts.forEach(a ->
                    log.warn("🔔 ALERT [{}] {} — {}", a.getSeverity(), a.getRuleName(), a.getMessage())
                );
            });

        } catch (Exception e) {
            log.error("Alert polling error: {}", e.getMessage());
        }
    }

    private double toDouble(Object val) {
        if (val == null) return 0.0;
        if (val instanceof Number n) return n.doubleValue();
        return 0.0;
    }
}
