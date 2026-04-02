package com.helios.metrics.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;

import java.time.Instant;

@Entity
@Table(name = "metric_events",
       indexes = {
           @Index(name = "idx_service_timestamp", columnList = "serviceName, timestamp"),
       })
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MetricEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Column(nullable = false)
    private String serviceName;

    @NotNull
    @Column(nullable = false)
    private Instant timestamp;

    /** p50 latency in milliseconds */
    @Min(0)
    private double p50Latency;

    /** p95 latency in milliseconds */
    @Min(0)
    private double p95Latency;

    /** p99 latency in milliseconds */
    @Min(0)
    private double p99Latency;

    /** Error rate as a fraction 0.0 – 1.0 */
    @Min(0) @Max(1)
    private double errorRate;

    /** Requests per second */
    @Min(0)
    private double requestRate;

    /** Source host or pod identifier */
    private String sourceHost;
}
