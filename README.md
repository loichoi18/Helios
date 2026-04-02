# ☀️ Helios — Cloud-Native SRE & Observability Platform

> A production-grade reliability platform that ingests service metrics, detects anomalies, executes automated runbooks, and forecasts SLA compliance — built across a Java microservice backend, a real-time JavaScript dashboard, and a Python-powered DevOps/SRE automation layer.

[![CI/CD](https://github.com/your-username/helios/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/helios/actions)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)](./backend)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![AWS](https://img.shields.io/badge/cloud-AWS-orange)](./infra)
[![Python](https://img.shields.io/badge/python-3.11-blue)](./sre)
[![Java](https://img.shields.io/badge/java-21-red)](./backend)

---

## 🏗️ Architecture

```
                         ┌─────────────────────────────────────────────────────┐
                         │                    AWS Cloud                        │
  ┌──────────┐           │  ┌─────────────┐   ┌──────────────────────────────┐│
  │ Services │──metrics──┼─▶│   Python    │   │     Java Microservices       ││
  │  (Mock)  │           │  │  Exporter   │──▶│  ┌──────────┐ ┌───────────┐ ││
  └──────────┘           │  │ (Prometheus)│   │  │ Metrics  │ │ Alerting  │ ││
                         │  └─────────────┘   │  │   API    │ │  Engine   │ ││
  ┌──────────┐           │                    │  └────┬─────┘ └─────┬─────┘ ││
  │  GitHub  │──push ────┼─▶ CI/CD Pipeline   │       │             │       ││
  │  Actions │           │  (GitHub Actions)  │  ┌────▼─────────────▼─────┐ ││
  └──────────┘           │                    │  │      PostgreSQL (RDS)   │ ││
                         │  ┌─────────────┐   │  └────────────────────────┘ ││
  ┌──────────┐           │  │  Terraform  │──▶└──────────────────────────────┘│
  │   SRE    │           │  │    (IaC)    │                                    │
  │ Runbooks │           │  └─────────────┘   ┌──────────────────────────────┐│
  └──────────┘           │                    │  React Dashboard (S3 + CDN)  ││
                         │  ┌─────────────┐   │  Real-time metrics, heatmaps ││
                         │  │ R Notebooks │   │  SLA tracker, alert feed     ││
                         │  │ (SLA/ARIMA) │   └──────────────────────────────┘│
                         │  └─────────────┘                                   │
                         └─────────────────────────────────────────────────────┘
```

---

## 🗂️ Repository Structure

```
helios/
│
├── backend/                        # ☕ Java 21 — Spring Boot Microservices
│   ├── metrics-service/            #   Ingests & stores time-series metrics
│   │   ├── src/main/java/…
│   │   │   ├── MetricsController.java
│   │   │   ├── MetricsService.java
│   │   │   ├── MetricsRepository.java
│   │   │   └── model/MetricEvent.java
│   │   └── Dockerfile
│   ├── alerting-service/           #   Rule-based alert evaluation engine
│   │   ├── src/main/java/…
│   │   │   ├── AlertEvaluator.java
│   │   │   ├── RuleEngine.java
│   │   │   └── NotificationDispatcher.java
│   │   └── Dockerfile
│   └── api-gateway/                #   Single entry point (Spring Cloud Gateway)
│       └── src/main/java/…
│
├── frontend/                       # ⚡ JavaScript — React + Recharts Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── MetricsDashboard.jsx
│   │   │   ├── LatencyHeatmap.jsx
│   │   │   ├── SLAGauge.jsx
│   │   │   ├── AlertFeed.jsx
│   │   │   └── ServiceGraph.jsx
│   │   ├── hooks/
│   │   │   ├── useMetricsWebSocket.js   # Live metrics via WebSocket
│   │   │   └── useSLAStatus.js
│   │   └── App.jsx
│   └── package.json
│
├── sre/                            # 🐍 Python 3.11 — SRE Tooling & Automation
│   ├── exporter/
│   │   └── prometheus_exporter.py  #   Custom Prometheus metrics exporter
│   ├── anomaly_detection/
│   │   ├── detector.py             #   Isolation Forest anomaly detection
│   │   └── train_model.py          #   scikit-learn model training pipeline
│   ├── runbooks/
│   │   ├── runbook_executor.py     #   Automated incident runbook runner
│   │   ├── runbooks/
│   │   │   ├── high_latency.yaml
│   │   │   ├── error_spike.yaml
│   │   │   └── disk_pressure.yaml
│   │   └── slack_notifier.py       #   Slack webhook alert dispatcher
│   ├── chaos/
│   │   └── chaos_runner.py         #   Controlled fault injection (latency/errors)
│   └── requirements.txt
│
├── analysis/                       # 📊 R — Statistical SLA Analysis
│   ├── sla_forecasting.Rmd         #   ARIMA time-series SLA forecast notebook
│   ├── latency_regression.R        #   Linear regression on latency vs. traffic
│   ├── incident_correlation.R      #   Correlation analysis: deploys vs. incidents
│   └── data/                       #   Sample CSVs for reproducibility
│       ├── metrics_sample.csv
│       └── incidents_sample.csv
│
├── infra/                          # 🏗️ Terraform — AWS Infrastructure as Code
│   ├── main.tf                     #   Root module
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── ecs/                    #   ECS Fargate cluster + task definitions
│   │   ├── rds/                    #   PostgreSQL on RDS
│   │   ├── alb/                    #   Application Load Balancer
│   │   ├── cloudwatch/             #   Log groups, alarms, dashboards
│   │   └── s3_cdn/                 #   Frontend static hosting + CloudFront
│   └── environments/
│       ├── dev/
│       └── prod/
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  #   Build, test, lint on every PR
│       ├── cd-backend.yml          #   Deploy Java services to ECS on merge
│       ├── cd-frontend.yml         #   Deploy React app to S3/CloudFront
│       └── sre-checks.yml          #   Run Python anomaly checks post-deploy
│
├── docker-compose.yml              # Local dev: all services + Prometheus + Grafana
└── README.md
```

---

## 🔧 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend API | Java 21, Spring Boot 3, Spring Cloud Gateway | Mirrors Canva's distributed Java microservice environment on AWS |
| Frontend | React, Recharts, WebSocket, Vite | Real-time dashboarding; plain JS hooks show fundamentals beyond frameworks |
| SRE Tooling | Python 3.11, scikit-learn, PyYAML, requests | Automation, anomaly detection, runbook orchestration |
| Statistical Analysis | R, forecast, ggplot2, corrplot | ARIMA forecasting + regression for SLA trend analysis |
| Infrastructure | Terraform, AWS ECS Fargate, RDS, CloudFront | IaC-first, cloud-native deployment matching Canva's AWS stack |
| Observability | Prometheus, Grafana, AWS CloudWatch | Industry-standard metrics & alerting pipeline |
| CI/CD | GitHub Actions | Automated build → test → deploy on every commit |
| Containerisation | Docker, docker-compose | Reproducible local dev + production parity |

---

## 🚀 Quick Start (Local)

### Prerequisites
- Docker & Docker Compose
- Java 21 (for local backend dev)
- Node 20 (for frontend)
- Python 3.11
- R 4.3+

### Run everything locally

```bash
git clone https://github.com/your-username/helios.git
cd helios

# Start all services: Java APIs + Postgres + Prometheus + Grafana
docker-compose up --build

# Frontend dev server
cd frontend && npm install && npm run dev
# → http://localhost:5173

# Python anomaly detector (standalone)
cd sre && pip install -r requirements.txt
python anomaly_detection/detector.py --source http://localhost:8080/api/metrics

# R SLA forecast notebook (requires R + RStudio or rmarkdown)
cd analysis && Rscript -e "rmarkdown::render('sla_forecasting.Rmd')"
```

Grafana dashboard: `http://localhost:3000` (admin/admin)

---

## ☕ Backend — Java Microservices

The backend is two Spring Boot 3 services behind a Spring Cloud Gateway.

### Metrics Service
Ingests `POST /api/metrics` events, stores them in PostgreSQL via Spring Data JPA, and exposes a `/api/metrics/query` endpoint for time-range queries.

```java
// MetricsController.java
@RestController
@RequestMapping("/api/metrics")
public class MetricsController {

    private final MetricsService metricsService;

    @PostMapping
    public ResponseEntity<Void> ingest(@RequestBody @Valid MetricEvent event) {
        metricsService.store(event);
        return ResponseEntity.accepted().build();
    }

    @GetMapping("/query")
    public List<MetricEvent> query(
            @RequestParam String service,
            @RequestParam @DateTimeFormat(iso = ISO.DATE_TIME) Instant from,
            @RequestParam @DateTimeFormat(iso = ISO.DATE_TIME) Instant to) {
        return metricsService.findByServiceAndTimeRange(service, from, to);
    }
}
```

### Alerting Engine
Evaluates sliding-window rules (e.g. "p99 latency > 500ms for 5 min") and dispatches to a notification topic (SNS in prod, Slack webhook in dev).

```java
// RuleEngine.java — evaluates loaded YAML alert rules
public class RuleEngine {

    public List<Alert> evaluate(List<MetricEvent> window, List<AlertRule> rules) {
        return rules.stream()
            .filter(rule -> rule.matches(window))
            .map(rule -> new Alert(rule.getName(), rule.getSeverity(),
                                   Instant.now(), rule.buildMessage(window)))
            .collect(toList());
    }
}
```

---

## ⚡ Frontend — Real-Time Dashboard

Built in React with WebSocket hooks for live metric streaming. No UI library dependency — all charts use Recharts, all layout is vanilla CSS Grid.

```javascript
// useMetricsWebSocket.js — streams live metric events
export function useMetricsWebSocket(service) {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8080/ws/metrics?service=${service}`);

    ws.onmessage = (event) => {
      const newPoint = JSON.parse(event.data);
      setMetrics(prev => [...prev.slice(-299), newPoint]); // rolling 300-point window
    };

    return () => ws.close();
  }, [service]);

  return metrics;
}
```

```jsx
// LatencyHeatmap.jsx — p50/p95/p99 area chart with threshold bands
export function LatencyHeatmap({ service }) {
  const metrics = useMetricsWebSocket(service);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={metrics}>
        <defs>
          <linearGradient id="p99Grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ff6b6b" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#ff6b6b" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis dataKey="timestamp" tickFormatter={t => format(new Date(t), 'HH:mm')} />
        <YAxis unit="ms" />
        <Tooltip />
        <ReferenceLine y={500} stroke="#ff4444" strokeDasharray="4 4" label="SLO" />
        <Area type="monotone" dataKey="p50" stroke="#4ecdc4" fill="none" strokeWidth={2} />
        <Area type="monotone" dataKey="p95" stroke="#ffe66d" fill="none" strokeWidth={2} />
        <Area type="monotone" dataKey="p99" stroke="#ff6b6b" fill="url(#p99Grad)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
```

---

## 🐍 Python — SRE Tooling

### Anomaly Detector (Isolation Forest)
Trains an unsupervised `IsolationForest` model on historical latency + error rate data to flag anomalous metric windows without needing labelled incidents.

```python
# detector.py
from sklearn.ensemble import IsolationForest
import numpy as np
import requests

def fetch_metrics(api_url: str, service: str, minutes: int = 60) -> np.ndarray:
    resp = requests.get(f"{api_url}/api/metrics/query",
                        params={"service": service, "lookback": minutes})
    events = resp.json()
    return np.array([[e["p99Latency"], e["errorRate"], e["requestRate"]]
                     for e in events])

def detect_anomalies(features: np.ndarray, contamination: float = 0.05) -> np.ndarray:
    model = IsolationForest(contamination=contamination, random_state=42)
    scores = model.fit_predict(features)           # -1 = anomaly, 1 = normal
    return scores

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--service", default="all")
    args = parser.parse_args()

    features = fetch_metrics(args.source, args.service)
    labels = detect_anomalies(features)
    anomaly_count = (labels == -1).sum()
    print(f"Detected {anomaly_count} anomalous windows out of {len(labels)}")
```

### Automated Runbook Executor
Reads YAML runbook definitions and executes remediation steps (restart container, scale up, purge cache) via shell or API calls.

```python
# runbook_executor.py
import yaml, subprocess, logging
from dataclasses import dataclass

@dataclass
class Step:
    name: str
    type: str          # shell | http | slack
    command: str | None = None
    url: str | None = None
    body: dict | None = None

def load_runbook(path: str) -> list[Step]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return [Step(**s) for s in data["steps"]]

def execute_step(step: Step) -> bool:
    if step.type == "shell":
        result = subprocess.run(step.command, shell=True, capture_output=True, text=True)
        logging.info(f"[{step.name}] exit={result.returncode}\n{result.stdout}")
        return result.returncode == 0
    elif step.type == "http":
        import requests
        r = requests.post(step.url, json=step.body)
        return r.status_code < 400
    return False
```

### Chaos Runner
Injects controlled latency and artificial error rates into target services to verify alert pipelines and runbooks fire correctly.

```python
# chaos_runner.py — fault injection for reliability testing
import time, random, requests, argparse

def inject_latency(target: str, extra_ms: int, duration_s: int):
    """POST chaos config to target service's chaos endpoint."""
    end = time.time() + duration_s
    while time.time() < end:
        requests.post(f"{target}/chaos/latency", json={"extra_ms": extra_ms})
        time.sleep(1)
    requests.delete(f"{target}/chaos/latency")  # clean up
    print(f"Injected {extra_ms}ms latency for {duration_s}s into {target}")
```

---

## 📊 R — Statistical SLA Analysis

### ARIMA SLA Forecasting (`sla_forecasting.Rmd`)

Uses `auto.arima` to fit a time-series model to 90 days of historical SLA compliance data and produce a 30-day forward forecast with confidence intervals.

```r
library(forecast)
library(ggplot2)
library(dplyr)

# Load historical daily SLA % data
sla_data <- read.csv("data/metrics_sample.csv") %>%
  mutate(date = as.Date(date)) %>%
  arrange(date)

sla_ts <- ts(sla_data$sla_percent, frequency = 7)  # weekly seasonality

# Fit ARIMA and forecast 30 days ahead
fit   <- auto.arima(sla_ts, seasonal = TRUE, stepwise = FALSE)
fc    <- forecast(fit, h = 30, level = c(80, 95))

autoplot(fc) +
  geom_hline(yintercept = 99.9, linetype = "dashed", colour = "red") +
  labs(title = "30-Day SLA Forecast (ARIMA)",
       subtitle = paste("Model:", fc$method),
       x = "Day", y = "SLA Compliance (%)") +
  theme_minimal()
```

### Latency Regression (`latency_regression.R`)

Fits a multiple linear regression to quantify how request rate, deploy frequency, and time-of-day predict p99 latency.

```r
library(tidyverse)

metrics <- read_csv("data/metrics_sample.csv")

model <- lm(p99_latency ~ request_rate + deploy_count + hour_of_day + is_weekend,
            data = metrics)

summary(model)
# Outputs: R², coefficients, p-values — understanding what drives latency spikes

# Residual plot to verify assumptions
plot(model, which = 1)
```

---

## 🏗️ Infrastructure — Terraform on AWS

### ECS Fargate Module (`infra/modules/ecs/main.tf`)

```hcl
resource "aws_ecs_cluster" "helios" {
  name = "helios-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "metrics_service" {
  family                   = "helios-metrics-service"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution.arn

  container_definitions = jsonencode([{
    name      = "metrics-service"
    image     = "${var.ecr_repo_url}:${var.image_tag}"
    portMappings = [{ containerPort = 8080 }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"  = "/helios/metrics-service"
        "awslogs-region" = var.aws_region
      }
    }
    environment = [
      { name = "SPRING_PROFILES_ACTIVE", value = var.environment },
      { name = "DB_HOST", value = var.db_host }
    ]
  }])
}
```

### CloudWatch Alarm Example

```hcl
resource "aws_cloudwatch_metric_alarm" "high_p99_latency" {
  alarm_name          = "helios-high-p99-latency-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "p99Latency"
  namespace           = "Helios/Metrics"
  period              = 60
  statistic           = "Average"
  threshold           = 500
  alarm_description   = "p99 latency exceeded 500ms SLO for 3 consecutive minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"
}
```

---

## ⚙️ CI/CD — GitHub Actions

### `ci.yml` — Build & Test on Every PR

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '21', distribution: 'temurin' }
      - run: cd backend/metrics-service && ./mvnw verify

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci && npm test && npm run build

  sre-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: |
          cd sre && pip install -r requirements.txt
          python -m pytest tests/ -v
          python -m mypy anomaly_detection/ runbooks/ --strict

  terraform-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: cd infra && terraform init -backend=false && terraform validate
```

### `sre-checks.yml` — Post-Deploy Reliability Gate

```yaml
name: SRE Post-Deploy Checks

on:
  workflow_run:
    workflows: ["CD Backend"]
    types: [completed]

jobs:
  anomaly-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: |
          pip install -r sre/requirements.txt
          # Wait 2 min for metrics to stabilise post-deploy
          sleep 120
          python sre/anomaly_detection/detector.py \
            --source ${{ vars.HELIOS_API_URL }} \
            --fail-on-anomaly
```

---

## 📈 Key Design Decisions

**Why two Java services instead of one?** Mirrors Canva's actual microservice topology where metrics ingestion and alerting evaluation have different scaling characteristics — ingestion is write-heavy, alerting is CPU-bound on rule evaluation.

**Why Isolation Forest for anomaly detection?** Infrastructure teams rarely have labelled incident data. Unsupervised methods let the system bootstrap detection from day one without historical labels.

**Why ARIMA in R instead of Python?** R's `forecast` package + `ggplot2` produces publication-quality SLA reports. This also demonstrates polyglot data science skills — using the right tool for the job rather than one language for everything.

**Why Terraform over CDK/Pulumi?** Terraform's HCL is the industry baseline for cloud infra at scale. Canva uses IaC extensively; demonstrating clean module structure matters more than framework novelty.

---

## 🧪 Testing Strategy

| Layer | Approach |
|-------|----------|
| Java | JUnit 5 + Testcontainers (real Postgres in CI), Mockito for unit tests |
| JavaScript | Vitest + React Testing Library, WebSocket mock |
| Python | pytest + responses (HTTP mock), hypothesis for property-based tests |
| Infrastructure | `terraform validate` + `tflint` + `checkov` security scan |
| End-to-End | Playwright smoke tests against `docker-compose` stack |

---

## 📄 License

MIT © 2025 — Built as a portfolio project to demonstrate full-stack SRE engineering skills.
