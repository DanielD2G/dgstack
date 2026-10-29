# Production metrics, September 2026

From CloudWatch and the ALB access logs, 1-30 Sep.

## HTTP traffic
- Steady around the clock (accounting customers in many timezones): 38-45 req/s, avg 41 req/s. No real night dip.
- Latency: p50 120 ms, p95 410 ms, p99 900 ms. Mean ~300 ms.
- Total requests: 106.3 M.

## Uploads (`POST /uploads`)
- 1,900 per day. p50 2.1 MB, p95 8.4 MB, max 48 MB (ZIPs of bank statements).

## WebSockets
- Peak concurrent dashboard connections: 3,200. Average: 1,400.

## Month-end export (`runMonthlyExport`)
- 1 Sep run: 19 min 40 s. 1 Aug run: 21 min 05 s. 1 Jul run: 22 min 18 s (peak, quarter close).
- Writes ~3.1 GB of CSVs to local disk before upload.
- Grows with active accounts (+4% per month).

## Database
- Connections in use: avg 34, peak 61 (both instances, pool max 20 each plus admin tools).
