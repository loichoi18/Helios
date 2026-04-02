package com.helios.metrics.controller;

import com.helios.metrics.model.MetricEvent;
import com.helios.metrics.service.MetricsService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;

@RestController
@RequestMapping("/api/metrics")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class MetricsController {

    private final MetricsService metricsService;

    /** Ingest a single metric snapshot from a service. */
    @PostMapping
    public ResponseEntity<MetricEvent> ingest(@RequestBody @Valid MetricEvent event) {
        return ResponseEntity.accepted().body(metricsService.store(event));
    }

    /** Query metrics for a specific service within a time range. */
    @GetMapping("/query")
    public List<MetricEvent> query(
            @RequestParam String service,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant to) {
        return metricsService.query(service, from, to);
    }

    /** Return all metrics from the last N minutes across all services. */
    @GetMapping("/recent")
    public List<MetricEvent> recent(@RequestParam(defaultValue = "15") int minutes) {
        return metricsService.recent(minutes);
    }

    /** List all known service names. */
    @GetMapping("/services")
    public List<String> services() {
        return metricsService.services();
    }
}
