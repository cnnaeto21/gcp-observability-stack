# Production-Grade Observability Stack on GCP

A comprehensive comparison of open-source (Prometheus + Grafana) vs enterprise (Datadog) observability solutions, built hands-on with a Flask application on Google Cloud Platform.

## Project Goals

- Build production-ready monitoring infrastructure
- Compare open-source vs commercial observability tools
- Understand total cost of ownership for observability
- Learn metrics, logs, and traces (three pillars)

## Architecture
```
Flask API (Port 8080)
├── Prometheus Client (metrics endpoint)
├── Datadog APM (auto-instrumentation)
└── Custom business metrics

Monitored by:
├── Prometheus (localhost:9090) → Grafana (localhost:3000)
└── Datadog Agent → Datadog Cloud (SaaS)
```

## ✨ Features Implemented

### Open-Source Stack (Prometheus + Grafana)
- ✅ Prometheus metrics collection (pull-based)
- ✅ Custom metrics: counters, histograms, gauges
- ✅ Grafana dashboards with variables
- ✅ Alert rules (P0 critical, P1 warning)
- ✅ PromQL queries for percentiles

### Enterprise Stack (Datadog)
- ✅ Infrastructure monitoring (auto-discovery)
- ✅ APM with distributed tracing
- ✅ Log aggregation
- ✅ Custom business metrics
- ✅ Unified dashboards

##  Key Learnings

### Metrics vs Traces
- **Metrics** show "what" (p95 latency is 2 seconds)
- **Traces** show "why" (database query took 1.8s of that 2s)

### Push vs Pull
- **Prometheus:** Pulls metrics from targets (explicit config)
- **Datadog:** Agent pushes to cloud (auto-discovery)

### Cost Analysis
- **Break-even:** ~20 hosts when factoring engineer time
- **Under 20 hosts:** Datadog cheaper (saves maintenance time)
- **Over 50 hosts:** Prometheus cheaper (scales without license costs)

##  Quick Start

### Prerequisites
- GCP account
- `gcloud` CLI configured
- Python 3.8+

### Deploy Infrastructure
```bash
# Create GCP VM
gcloud compute instances create flask-api-vm \
  --machine-type=e2-micro \
  --zone=us-central1-a \
  --image-family=ubuntu-2204-lts

# SSH into VM
gcloud compute ssh flask-api-vm --zone=us-central1-a

# Run setup script
./scripts/setup.sh
```

### Access Services

- Flask API: `http://<EXTERNAL_IP>:8080`
- Prometheus: `http://<EXTERNAL_IP>:9090`
- Grafana: `http://<EXTERNAL_IP>:3000` (admin/admin)
- Datadog: `https://app.datadoghq.com`

##  Project Structure
```
gcp-observability-stack/
├── README.md
├── docs/
│   ├── prometheus-vs-datadog-comparison.md  # Detailed comparison
│   ├── day1-gcp-setup.md                   # GCP deployment
│   ├── day2-prometheus-grafana.md          # Open-source stack
│   ├── day3-alerts.md                      # Alert configuration
│   └── day4-5-datadog.md                   # Enterprise stack
├── flask-app/
│   ├── app.py                              # Instrumented Flask app
│   ├── requirements.txt
│   └── README.md
├── prometheus/
│   ├── prometheus.yml                      # Scrape config
│   └── alert_rules.yml                     # Alert definitions
├── datadog/
│   └── conf.yaml                           # Datadog integration
└── scripts/
    ├── setup.sh                            # Automated setup
    └── load_test.sh                        # Traffic generation
```

##  Technical Concepts Demonstrated

### Metrics Types
- **Counter:** Monotonically increasing (total requests)
- **Gauge:** Current value (active connections)
- **Histogram:** Distribution with buckets (latency percentiles)

### Alert Design
- `for: 2m` duration prevents alert fatigue
- P0 (critical) → Page on-call engineer
- P1 (warning) → Slack notification
- Severity-based routing strategy

### PromQL Examples
```promql
# Request rate per second
rate(flask_request_count_total[1m])

# P95 latency
histogram_quantile(0.95, sum by (le) (rate(flask_request_latency_seconds_bucket[1m])))

# Error rate (5xx errors)
rate(flask_request_count_total{status=~"5.."}[1m])
```

## Cost Analysis

### Monthly Costs (10 hosts example)

| Stack | Direct Cost | Engineer Time | Total |
|-------|-------------|---------------|-------|
| Prometheus | $0 | 6 hrs × $150 = $900 | $900 |
| Datadog | $310 | 2 hrs × $150 = $300 | $610 |

**Winner at 10 hosts:** Datadog (32% cheaper)

See [full comparison document](docs/prometheus-vs-datadog-comparison.md) for complete analysis.

## Use Cases

### Choose Prometheus When:
- You have 50+ hosts
- Data must stay on-premise (compliance)
- You have dedicated SRE team
- Cost control is critical

### Choose Datadog When:
- You have <20 hosts
- Team focuses on product, not infrastructure
- You need unified metrics + logs + traces
- Fast setup is priority

##  Screenshots

[Add screenshots to /screenshots directory]

## 🔗 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [Datadog APM Guide](https://docs.datadoghq.com/tracing/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
