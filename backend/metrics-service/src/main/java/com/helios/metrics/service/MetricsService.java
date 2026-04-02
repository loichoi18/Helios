package com.helios.metrics.service;

import com.helios.metrics.model.MetricEvent;
import com.helios.metrics.repository.MetricsRepository;
import com.helios.metrics.websocket.MetricsBroadcaster;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.Random;

@Service
@RequiredArgsConstructor
@Slf4j
public class MetricsService {

    private final MetricsRepository repository;
    private final MetricsBroadcaster broadcaster;
    private final Random random = new Random();

    @Transactional
    public MetricEvent store(MetricEvent event) {
        event.setTimestamp(Instant.now());
        MetricEvent saved = repository.save(event);
        broadcaster.broadcast(saved);   // push to all WebSocket subscribers
        log.info("Stored metric: service={} p99={}ms errorRate={}",
                 saved.getServiceName(), saved.getP99Latency(), saved.getErrorRate());
        return saved;
    }

    @Transactional(readOnly = true)
    public List<MetricEvent> query(String service, Instant from, Instant to) {
        return repository.findByServiceNameAndTimestampBetweenOrderByTimestampAsc(
                service, from, to);
    }

    @Transactional(readOnly = true)
    public List<MetricEvent> recent(int minutes) {
        return repository.findAllSince(Instant.now().minusSeconds(minutes * 60L));
    }

    @Transactional(readOnly = true)
    public List<String> services() {
        return repository.findDistinctServiceNames();
    }

    /**
     * Simulates incoming metrics from a set of fictional services every 5 seconds.
     * Remove this in a real deployment and replace with actual instrumented services.
     */
    @Scheduled(fixedDelay = 5_000)
    @Transactional
    public void simulateIncomingMetrics() {
        String[] services = {"canvas-renderer", "export-service", "auth-service", "asset-cdn"};
        for (String svc : services) {
            double baseLatency = switch (svc) {
                case "canvas-renderer" -> 120;
                case "export-service"  -> 350;
                case "auth-service"    -> 45;
                default                -> 80;
            };
            // Occasionally inject a latency spike to trigger alerts
            boolean spike = random.nextDouble() < 0.05;
            double p99 = baseLatency * (spike ? 5 + random.nextDouble() * 3 : 1 + random.nextDouble() * 0.4);

            MetricEvent event = MetricEvent.builder()
                    .serviceName(svc)
                    .p50Latency(p99 * 0.4)
                    .p95Latency(p99 * 0.75)
                    .p99Latency(p99)
                    .errorRate(spike ? 0.05 + random.nextDouble() * 0.1 : random.nextDouble() * 0.005)
                    .requestRate(100 + random.nextDouble() * 400)
                    .sourceHost("sim-pod-" + random.nextInt(5))
                    .build();
            store(event);
        }
    }
}
