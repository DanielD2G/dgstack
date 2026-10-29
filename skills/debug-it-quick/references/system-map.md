# System map: discovering targets and quick triage

Read only the sections for the environments this problem touches. Each section says what the separate systems are, the sweep for step 2, and the commands to follow a lead (or to start a scout with).

All commands here are read-only. Keep them that way in the briefs.

When a check needs a web dashboard (Dokploy, Coolify, Portainer, the AWS console, Grafana, a status page), prefer the CLI or API. If the page is the only way, open it in the built-in browser when the environment has one (in the Claude desktop app, the browser pane, `mcp__Claude_Browser__*`); use Claude in Chrome only if the user asks or there is no built-in browser, and never the user's own browser (`open <url>`, `xdg-open`). Background scouts usually lack browser tools, so dashboard checks are yours.

## Contents

- Docker Swarm / Compose
- Dokploy, Coolify, Portainer and similar
- Kubernetes
- AWS
- Other clouds and PaaS (GCP, Azure, Vercel, Netlify, Fly, Render, Railway, Cloudflare)
- Databases, queues and caches
- Network, DNS, TLS, proxy
- The local machine (macOS, Linux, Windows)
- The repo, CI and deploys
- Front end and browser
- Third-party services

## Docker Swarm / Compose

**Targets:** one per service in the stack, plus the host(s) and the overlay network if Swarm. Find them in `docker-compose*.yml` / stack files, or `docker service ls` / `docker compose ps`.

**Sweep:**
- Swarm: `docker service ls` (look for `0/N` replicas), `docker node ls`
- Compose / plain: `docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.RunningFor}}'` (look for `Restarting`, `Exited (137)`, `(unhealthy)`)
- Every node, not just the manager: `ssh <node> 'df -h; free -m'`
- The proxy's access log with durations: `docker logs --since 2h <traefik|nginx> | tail -200` (which routes are slow or 5xx, since when). On a busy proxy, filter instead of tailing: only 5xx, or only requests over a second, grouped by route.

**Scout starts with:**
- `docker service ps <svc> --no-trunc` (the error column says why tasks died)
- `docker service logs --since <window> --tail 200 <svc>` or `docker logs --since <window> --tail 200 <container>`
- `docker inspect <container> --format '{{.State.OOMKilled}} {{.State.ExitCode}} {{.State.Health.Status}}'`
- `docker stats --no-stream`
- Host: `df -h`, `docker system df`, `free -m`

Exit 137 with OOMKilled is memory; 137 without it is usually a kill by the orchestrator (failed healthcheck). Exit 1 right after start is usually config or a missing env var.

## Dokploy, Coolify, Portainer and similar

They run Docker (Dokploy and Coolify on Swarm or Compose) plus Traefik, so the Docker section applies on the host over SSH. Extra targets:

- the platform's own Traefik/proxy container and its logs (routing, certificates);
- the build/deploy logs of the last deployment (in the panel or its API);
- the platform's own service (`dokploy`, `coolify`) if deploys themselves fail.

Ask the user for the SSH host if it's not in the project docs. The panel is a fallback, through the browser rule above.

## Kubernetes

**Targets:** one per deployment/statefulset involved, plus ingress, nodes, and cluster DNS.

**Sweep:** `kubectl get pods -A | grep -v -E 'Running|Completed'`, `kubectl get nodes`, `kubectl get events -A --sort-by=.lastTimestamp | tail -30`

**Scout starts with:** `kubectl describe pod <pod> -n <ns>` (last state, events), `kubectl logs <pod> -n <ns> --since=<window> --tail=200` and `--previous` for crashed containers, `kubectl top pod -n <ns>`.

## AWS

**Targets:** follow the request path and split it: Route 53 / CloudFront, ALB/NLB (target health), compute (ECS service, EC2 instance, Lambda function, EKS), data (RDS, DynamoDB, ElastiCache, S3), queues (SQS, SNS, EventBridge), plus IAM/credentials and service quotas. Find them in Terraform/CDK/SAM/CloudFormation, or ask which account, profile and region.

**Sweep:** depends on the compute, e.g. `aws ecs describe-services --cluster <c> --services <s> --query 'services[].{name:serviceName,running:runningCount,desired:desiredCount,events:events[:3]}'`, `aws elbv2 describe-target-health --target-group-arn <arn>`.

**Scout starts with:**
- Logs: `aws logs tail <group> --since 30m --filter-pattern '?ERROR ?Exception ?Task timed out'`
- ECS: stopped tasks and their `stoppedReason` (`aws ecs list-tasks --desired-status STOPPED`, then `describe-tasks`)
- Lambda: errors and throttles in CloudWatch metrics; timeout and memory in the function config
- RDS: `describe-db-instances` status, CPU, connections, free storage metrics
- Recent changes: CloudTrail `lookup-events` in the window

Always pass `--profile` and `--region` explicitly in the brief.

## Other clouds and PaaS

Use their CLIs read-only (`gcloud`, `az`, `vercel`, `netlify`, `fly`, `render`, `railway`, `wrangler`) for: service status, recent deploys, logs filtered to the window, and env var names (not values). Usually one target for the platform's deploy/build, one for runtime logs, one for its edge/DNS. If the session has an MCP server for the platform, prefer it.

## Databases, queues and caches

**Targets:** each database, broker and cache on its own.

**Scout starts with:** reachability (`pg_isready`, `redis-cli ping`, `mysqladmin ping`), connection count vs limit, disk/storage free, long-running queries or locks (`pg_stat_activity`), replication lag, queue depth and dead-letter count. Read-only queries only; no `VACUUM`, `FLUSH`, `KILL`.

## Network, DNS, TLS, proxy

One scout can usually group these.

- DNS: `dig +short <host>` and `dig +short AAAA <host>`, compare against what they should be; `dig @1.1.1.1` vs the local resolver. A stale record left over from a migration is a classic.
- Dual stack: when a host has both A and AAAA, test each family on its own (`curl -4 -sv`, `curl -6 -sv`, or `--resolve <host>:443:<ip>`). They can land on different servers, and clients (and Let's Encrypt) prefer IPv6.
- TLS: `echo | openssl s_client -connect <host>:443 -servername <host> 2>/dev/null | openssl x509 -noout -dates -subject`
- HTTP path: `curl -sv -o /dev/null --max-time 10 <url>` (status, redirects, which hop fails)
- Ports: `nc -zv <host> <port>`
- Proxy (nginx, Traefik, Caddy): its error log in the window, and whether the upstream it points at exists

## The local machine (macOS, Linux, Windows)

For "my PC is slow", "X won't start", "no internet", a broken dev environment. Targets: resources (CPU, memory, disk), the specific app/process, network, recent changes (updates, installs), and the dev toolchain if relevant.

- **macOS:** `top -l 1 -o cpu | head -20`, `vm_stat`, `df -h`, `log show --last 30m --predicate 'eventType == logEvent and messageType == error' | tail -100`, `lsof -nP -iTCP -sTCP:LISTEN`, crash reports in `~/Library/Logs/DiagnosticReports/`, `softwareupdate --history`
- **Linux:** `systemctl --failed`, `journalctl -p err --since '30 min ago'`, `top -bn1 | head -20`, `free -m`, `df -h`, `dmesg -T | tail -50`, `ss -tlnp`
- **Windows (PowerShell):** `Get-WinEvent -FilterHashtable @{LogName='System','Application'; Level=1,2; StartTime=(Get-Date).AddHours(-1)}`, `Get-Process | Sort-Object CPU -Descending | Select -First 15`, `Get-PSDrive -PSProvider FileSystem`, `Get-Service | Where Status -eq 'Stopped'`, `Get-NetTCPConnection -State Listen`
- **Dev toolchain:** versions (`node -v`, `python --version`, ...) against what the project pins, `PATH`, a stale lockfile or cache.

## The repo, CI and deploys

**Targets:** recent commits, the failing CI run, the last deploy.

- `git log --since '<start time minus a day>' --oneline --stat`, and `git diff <last good>..<first bad>` when known
- CI: `gh run list --limit 10`, `gh run view <id> --log-failed`
- A dependency bump in the lockfile is a common silent cause; check lockfile diffs.

## Front end and browser

Console errors, failed network requests, the API response the page got. Use the browser rule above; these checks are usually yours, not a scout's. Check whether the backend returned the error (then it's a backend target) or the front end broke on a good response.

## Third-party services

Payment, email, auth, maps, LLM APIs, anything external the system calls. One scout can check their status pages through their APIs or `curl`, plus the errors our logs show when calling them (401 = credential, 429 = quota/rate limit, 5xx = their outage).
