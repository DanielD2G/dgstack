# Production, October 2026

- One ECS service, 2 tasks (1 vCPU, 2 GB) for redundancy. CPU avg 12%, peak 31%.
- Traffic: peak 3.4 req/s (weekday 10:00-12:00), 0.2 req/s at night.
- RDS PostgreSQL db.t4g.medium, CPU avg 18%.
- Slowest endpoint: GET /reports/monthly, p95 14 s, ~6,000 orders per month,
  ~18,000 SQL queries per request.
- Everything else p95 < 250 ms.
