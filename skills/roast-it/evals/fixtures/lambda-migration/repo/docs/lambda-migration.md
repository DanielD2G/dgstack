# Proposal: move tally-api to AWS Lambda

Author: platform team. Status: draft for approval.

## Why
Servers are a burden. We pay for two instances 24/7 even when nobody is using
them. Lambda scales to zero and we only pay for what we use.

## Plan
1. Wrap the Express app with `@codegenie/serverless-express`, one function
   behind API Gateway (HTTP API), 512 MB memory.
2. The API is stateless, so no code changes are needed beyond the handler
   wrapper.
3. The month-end export becomes a Lambda triggered by an EventBridge schedule.
4. Decommission the EC2 instances and the ALB.

## Cost
At ~10 M requests per month and 300 ms average duration:

- Requests: 10 M x $0.20 / M = $2
- Compute: 10 M x 0.3 s x 0.5 GB = 1.5 M GB-s x $0.0000166667 = $25
- API Gateway: 10 M x $1.00 / M = $10

**Total ~$37/month vs $180 today: an ~80% saving.**

## Timeline
Three weeks, one engineer.

## Risks
Cold starts, mitigated with provisioned concurrency if needed.
