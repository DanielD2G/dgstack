# Infra

- 2 x EC2 `t3.large` (on-demand) in an Auto Scaling group, Docker, behind an ALB with sticky sessions.
- RDS PostgreSQL `db.t3.large`, `max_connections` = 200. Stays as is.
- S3 buckets for uploads and exports.

Monthly cost (September 2026 bill, excluding RDS and S3):

| Item | USD |
|---|---|
| EC2 2 x t3.large | 121 |
| ALB (hours + LCU) | 31 |
| EBS + CloudWatch | 28 |
| **Total** | **180** |
