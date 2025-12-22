# Day 6: Cloud SQL + Distributed Tracing

## What I Built
- Deployed PostgreSQL on Cloud SQL
- Connected Flask to real database
- Created user signup/analytics endpoints
- Monitored database performance with APM

## Key Learning: Distributed Tracing
[Screenshot of /analytics trace showing database queries]

This trace shows:
- Total request time: 1.53s
- Database queries: 16.9ms
- Can drill down to see exact SQL queries
- Identifies optimization opportunities

## Cost Analysis
- Cloud SQL (db-f1-micro): ~$10/month
- Automatic backups, HA, security patches included
- vs self-hosted: $0 but adds operational burden
