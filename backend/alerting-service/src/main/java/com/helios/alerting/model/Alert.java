package com.helios.alerting.model;

import lombok.*;
import java.time.Instant;

@Getter
@AllArgsConstructor
@Builder
public class Alert {
    private final String ruleName;
    private final Severity severity;
    private final Instant firedAt;
    private final String message;
    private final String serviceName;

    public enum Severity { INFO, WARNING, CRITICAL }
}
