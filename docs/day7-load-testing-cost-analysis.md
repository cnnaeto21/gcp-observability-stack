# Day 7: Load Testing & Cost Analysis

## Load Testing Results

### Test Setup
- **Tool:** Locust (Python-based load testing)
- **Scenarios:** 10, 25, 100 concurrent users
- **Duration:** 3-5 minutes per test
- **Target:** Flask app on e2-micro VM

### Performance Summary

| Users | RPS | Median Response | 95%ile | Failures | CPU Usage | RAM Status | Overall Status |
|-------|-----|----------------|--------|----------|-----------|------------|----------------|
| 10 | 3-4 | 26ms | ~100ms | 0.2% | 37% | ~700MB | ✅ Healthy |
| 25 | 5.6 | 1600ms | 5300ms | 2.1% | <50% | ~900MB | 🟡 Degraded |
| 100 | ~8 | 12000ms | 17000ms | 1.6% | 100% | **OOM** | 🔴 Failed |

### The Bottleneck: Out of Memory (OOM)

**At 25+ concurrent users, the VM ran out of memory:**
```
[ERROR] Worker (pid:1200) was sent SIGKILL! Perhaps out of memory?
[ERROR] Worker (pid:1207) was sent SIGKILL! Perhaps out of memory?
[ERROR] Worker (pid:1214) was sent SIGKILL! Perhaps out of memory?
[ERROR] Worker (pid:1221) was sent SIGKILL! Perhaps out of memory?
[ERROR] Worker (pid:1228) was sent SIGKILL! Perhaps out of memory?
```

**Root cause analysis:**

e2-micro VM has only 1GB RAM:
```
Base OS:              ~200 MB
Prometheus:           ~100 MB
Datadog agent:        ~150 MB
Cloud SQL connections: ~50 MB
----------------------------
Available for Flask:  ~500 MB

5 gunicorn workers × 100-150 MB each = 500-750 MB
Under load: Memory spikes → Exceeds 1GB → OOM killer → Workers killed
```

**Key finding:** Memory, not CPU, was the bottleneck!

---

## Infrastructure Capacity Analysis

### e2-micro ($7/month)
- **Max concurrent users:** ~10
- **Max RPS:** 3-4 requests/second
- **Failure mode:** Out of memory (OOM) kills gunicorn workers
- **Use case:** Development, personal projects, very light production traffic

### Required for 100 concurrent users
- **VM:** e2-standard-2 (2 vCPU, 8GB RAM) - $49/month
- **Reasoning:** 8x more RAM allows 10-15 gunicorn workers
- **Database:** Cloud SQL db-f1-micro - $10/month
- **Total infrastructure:** $59/month

### Scaling Options Comparison

| Approach | Setup | Monthly Cost | Complexity | Capacity |
|----------|-------|-------------|------------|----------|
| **Current (e2-micro)** | Done | $17 | Low | 10 users |
| **Vertical (e2-standard-2)** | 10 min | $59 | Low | 100 users |
| **Horizontal (3× e2-micro + LB)** | 2 hours | $98 | Medium | 100 users |
| **Optimize current** | 1 hour | $17 | Medium | 15-20 users |

---

## Cost Analysis

### Actual GCP Costs Incurred (Dec 18-24, 2025)

**Total: $0.64** (mostly covered by free tier credits)

Breakdown:
- **Cloud SQL:** $0.54 (85% of total)
- **Artifact Registry:** $0.10 (Docker image storage)
- **Cloud Storage:** $0.00
- **Compute Engine:** $0.00 (free tier)

**Projected monthly cost if running 24/7:** $19-25

---

## Observability Cost Comparison (Annual)

### Prometheus + Grafana Stack

**Direct costs:**
- Software licenses: $0 (open source)
- VM overhead: 250MB RAM (~25% of 1GB)
- Storage: Minimal

**Hidden costs:**
- Initial setup: 8 hours × $150/hour = $1,200
- Monthly maintenance: 6 hours × $150/hour = $900/month
  - Update Prometheus/Grafana: 1 hour
  - Debug scrape failures: 1 hour
  - Tune alert rules: 2 hours
  - Add new services/dashboards: 2 hours

**Total first year (10 hosts):**
- Setup: $1,200
- Maintenance: $900 × 12 = $10,800
- Infrastructure: $200
- **Total: $12,200**

---

### Datadog Stack

**Direct costs:**
- Subscription: $31/host/month
- For 10 hosts: $310/month = $3,720/year
- VM overhead: 150MB RAM (~15% of 1GB)

**Hidden costs:**
- Initial setup: 1 hour × $150 = $150
- Monthly maintenance: 2 hours × $150 = $300/month
  - Review auto-discoveries: 0.5 hours
  - Tune alerts: 1 hour
  - Update dashboards: 0.5 hours

**Total first year (10 hosts):**
- Setup: $150
- Software: $3,720
- Maintenance: $300 × 12 = $3,600
- **Total: $7,470**

---

### Comparison Summary

| Metric | Prometheus + Grafana | Datadog | Winner |
|--------|---------------------|---------|--------|
| **Setup time** | 8 hours | 1 hour | Datadog |
| **Monthly maintenance** | 6 hours | 2 hours | Datadog |
| **First year (10 hosts)** | $12,200 | $7,470 | Datadog (39% cheaper) |
| **At scale (100 hosts)** | $12,200 | $40,800 | Prometheus (67% cheaper) |
| **Break-even point** | - | ~20 hosts | - |

**Key insight:** Engineer time ($150/hour) dominates costs at small scale. Datadog's higher license fee is offset by 66% reduction in maintenance time.

---

## Lessons Learned

### 1. Memory, Not CPU, Was the Bottleneck
- CPU never exceeded 50% during normal operation
- But RAM exhaustion killed workers at 25 users
- **Implication:** When sizing VMs, look at RAM requirements, not just CPU

### 2. Small VMs Fail Ungracefully
- No gradual degradation
- Sudden transition from "working" to "OOM killed"
- **Implication:** Build in headroom, monitor memory usage closely

### 3. Observability Tooling Consumes Resources
- Prometheus + Datadog: ~250MB RAM (25% of total)
- On production systems, budget 15-20% overhead for monitoring
- **Implication:** Factor monitoring overhead into capacity planning

### 4. Load Testing Reveals Limits Before Production
- Discovered OOM issue in test, not in front of customers
- Identified exact breaking point (between 10-25 users)
- **Implication:** Always load test before launch

### 5. Total Cost of Ownership ≠ License Cost
- "Free" Prometheus cost $12K/year in engineer time
- "Expensive" Datadog cost $7K/year total
- **Implication:** Evaluate total cost, not just sticker price

---

## Recommendations for Production

**If deploying this system to production:**

1. **Start with e2-small ($14/month)**
   - 2GB RAM gives breathing room
   - Handles 25-30 concurrent users
   - Still very affordable

2. **Use Datadog for observability**
   - At <20 hosts, it's cheaper than DIY
   - Faster time to value
   - Less operational burden

3. **Implement auto-scaling**
   - Use GCP Managed Instance Groups
   - Scale horizontally based on CPU/memory
   - Costs more but handles traffic spikes

4. **Monitor memory usage closely**
   - Set alerts at 70% memory (before OOM)
   - Track memory per worker
   - Tune worker count based on actual usage

5. **Use Cloud SQL connection pooling**
   - Implement pgBouncer for connection reuse
   - Reduces memory overhead
   - Handles more concurrent requests

---

## Cost Per User Economics

| Infrastructure | Max Users | Monthly Cost | Cost per User |
|----------------|-----------|--------------|---------------|
| e2-micro | 10 | $17 | $1.70/user |
| e2-small | 30 | $24 | $0.80/user |
| e2-medium | 60 | $38 | $0.63/user |
| e2-standard-2 | 100 | $59 | $0.59/user |

**Insight:** Economies of scale - bigger VMs are more cost-efficient per user.

---

## Next Steps

For continued learning:
1. Implement auto-scaling to handle variable load
2. Add CDN (Cloud CDN) to reduce origin traffic
3. Implement caching (Redis) to reduce database load
4. Set up multi-region deployment for HA
5. Implement chaos engineering to test resilience
