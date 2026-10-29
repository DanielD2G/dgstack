# Attack angles

Where proposals usually break, by kind of target. These are places to look, not objections to paste: an angle becomes a finding only when you have the evidence for it in this proposal. Skip the angles that don't apply.

## Any target

- **The problem.** Is the problem real, measured, and big enough to pay for this? Find the incident, the metric or the user complaint behind it. "It feels slow" is not a baseline.
- **The do-nothing and the boring option.** What happens if nobody does this for six months? What's the smallest change that gets 80% of the benefit (an index, a cache, a config change, a bigger instance, a manual process)?
- **Cost of ownership.** Who operates it at 3 a.m.? New on-call surface, new dashboards, new skills the team doesn't have, new vendor.
- **Reversibility.** If it goes wrong, how do you back out, and how long does that take? One-way doors deserve more evidence.
- **Estimates.** Compare with how long similar work took in this repo's history (`git log` on comparable changes). Migrations and rewrites run long; look for the parts the estimate leaves out (data backfill, dual-running, cutover, decommission).
- **Success.** Is there a metric, a baseline and a target? Could it succeed on paper and fail in reality?

## A PR

- **Correctness at the edges:** empty, null, huge, concurrent, retried, partially failed, out of order. Find the input that breaks it and show it.
- **Callers:** grep every caller of what changed. Changed signatures, changed defaults, changed error behavior, changed ordering.
- **Data:** migrations that lock big tables, backfills that don't fit in one transaction, columns dropped while old code still reads them, deploy order between app and schema.
- **Tests:** do they test the claim of the PR, or only that the code runs? What would still pass if the change were wrong?
- **Rollout:** feature flag? What happens to in-flight requests, queued jobs and cached data during the deploy?
- **Scope:** does the PR do what its title says, and only that? Unrelated changes hide risk.

## A PRD or product definition

- **The user:** who exactly, and what evidence says they want this (interviews, tickets, usage data)? "Users want" with no source is an assumption.
- **The behavior change:** what must users do differently for this to work, and why would they?
- **The numbers:** market size, conversion, adoption, revenue. Recompute them from the inputs; check the inputs against real data the user has.
- **Contradictions:** goals vs. non-goals, scope vs. timeline, the metric vs. what the feature actually moves.
- **Second-order effects:** support load, abuse, cannibalizing an existing feature or plan, what sales or ops have to change.
- **Missing pieces:** edge cases, empty states, permissions, migration of existing users, what happens when it's turned off.

## An architecture or migration plan

Read the current system first and describe its real workload: request duration distribution (p50, p99, max), payload sizes, traffic shape (steady, spiky, cron), state (local disk, in-memory caches, sessions, long-lived connections), background work, dependencies. Then check the workload against the target, using the target's **current** official docs and quotas, linked.

Example, "move this to AWS Lambda". Look up the current values of each and check them against the real workload:

- **Max execution time.** Any request, job or export that can run longer? Check the slowest real ones, not the average.
- **Payload size** for synchronous and asynchronous invocations, and API Gateway or function URL limits in front of it. File uploads and big responses?
- **Memory, CPU, ephemeral storage** (`/tmp`) and deployment package size, including dependencies and native binaries.
- **Concurrency:** the account's concurrency limit vs. peak traffic; reserved concurrency; burst scaling.
- **Steady state and bursts, separately.** Something that holds at average load can fall over when the platform scales out fast (a retry storm, a traffic spike, a cold deploy). For every shared resource behind the functions (database connections, a rate-limited API, a license count), do the math for both.
- **Cold starts** for this runtime and package size, against the latency the users get today.
- **Connections:** a function per request opening database connections can exhaust the database. Is there pooling (RDS Proxy or similar)?
- **State:** anything relying on local disk, in-memory caches, sticky sessions, WebSockets, or a background thread that outlives the request.
- **Networking:** VPC access, NAT costs for outbound calls, fixed egress IPs the partners whitelist.
- **Cost:** price the real traffic (requests x duration x memory, plus API Gateway, NAT, logs) against what it costs today. Steady high traffic is often cheaper on containers.
- **Ops:** local dev, debugging, observability, deploy pipeline, timeouts in every layer between client and function.

The same method works for any target (Kubernetes, microservices, Kafka, serverless databases, edge runtimes, a new vendor): list the target's hard limits and operational costs, then hold the real workload against each one.

## Product, pricing or business

- **Unit economics:** price minus the real cost to serve per customer, including support and infra at the projected usage, not the current one.
- **Competitors and substitutes,** including the spreadsheet or manual process customers use today.
- **Who pays and who decides:** the buyer, the user and the person who approves the budget can be three different people.
- **Assumed growth:** what has to be true for the numbers to work, and how far that is from today's real numbers.
