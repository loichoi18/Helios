package com.helios.metrics.repository;

import com.helios.metrics.model.MetricEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

@Repository
public interface MetricsRepository extends JpaRepository<MetricEvent, Long> {

    List<MetricEvent> findByServiceNameAndTimestampBetweenOrderByTimestampAsc(
            String serviceName, Instant from, Instant to);

    @Query("""
           SELECT m FROM MetricEvent m
           WHERE m.timestamp >= :from
           ORDER BY m.timestamp ASC
           """)
    List<MetricEvent> findAllSince(@Param("from") Instant from);

    @Query("""
           SELECT DISTINCT m.serviceName FROM MetricEvent m
           """)
    List<String> findDistinctServiceNames();

    @Query("""
           SELECT AVG(m.errorRate) FROM MetricEvent m
           WHERE m.serviceName = :service
             AND m.timestamp BETWEEN :from AND :to
           """)
    double avgErrorRate(
            @Param("service") String service,
            @Param("from") Instant from,
            @Param("to") Instant to);
}
