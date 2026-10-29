---
name: debug-it-quick
description: Fast, two-level debugging across one or many systems. The main agent reads the error and the project's context, maps every system that could be involved (services in a Docker Swarm, Compose or Kubernetes, a Dokploy or Coolify host, AWS resources, a database, DNS and TLS, CI, the local PC, the repo), then fans out cheap parallel Haiku scouts, one per system, and escalates only where a scout finds a hint, while telling the user what is being checked and where the problem probably is. Use it whenever the user pastes an error, a log, a stack trace or a symptom and wants it found fast ("debug it quick", "debugeá esto", "¿por qué falla?", "se cayó", "está caído", "no levanta", "tira 502", "el contenedor se reinicia", "no me anda", "algo se rompió en prod", "mi PC está lenta"), including problems that are not in code at all, such as infrastructure, deploys, servers, networks, the user's own machine. Not for building features or for slow, test-first fixing of a bug whose location is already known.
---

# debug-it-quick

Something is broken and the user wants to know where, fast. The cause is often not in the place the error shows up: a 502 at the proxy is a crashed service, which is a refused database connection, which is a full disk. And it is often not in code at all.

The approach is breadth first, then depth only where the evidence points:

1. **You (the main agent)** read the error and the context, map the systems, and run a quick sweep.
2. **Haiku scouts** check every remaining system in parallel, read-only, and come back with a verdict.
3. **You** follow the hints: dig yourself, or send a stronger subagent where the digging is long.

Speed is the point, so use small models for breadth and spend intelligence only where a hint justifies it. Keep the user informed the whole time.

Talk to the user in their language (usually Spanish), briefly.

## Keep the user posted

The user should never wonder what you are doing. Send a short status line at each of these moments, not only at the end:

- after reading the context: what the error suggests and how many systems you will check;
- when the scouts go out: which systems, one line;
- each time a scout comes back with something (not for every clean result; batch those);
- when you narrow it down: "Probablemente está en X porque Y. Confirmando."
- when you confirm the cause.

Format, plain text, no emojis:

```
Investigando: api, worker, postgres, traefik (4 scouts). Ya descarté: DNS, disco del host.
Pista: worker reinicia cada 30 s desde las 14:02, OOMKilled. Lo reviso yo.
```

## 1. Read the error and the context (minutes, not more)

- **The error itself:** pull out every identifier: service and container names, hosts, ports, URLs, status codes, file paths, request or trace IDs, and above all the **time** it started. Ask the user for the time only if nothing gives it and it matters.
- **Project instructions and docs:** `CLAUDE.md`, `AGENTS.md`, README, `docs/`, runbooks, `.env.example`. They often name the systems, how to reach them and known pitfalls.
- **Infrastructure files:** `docker-compose*.yml`, stack files, Kubernetes manifests, Helm values, Terraform, `dokploy`/Coolify config, CI workflows, Procfiles, nginx/Traefik/Caddy config. These are the system map, already written.
- **Memory:** anything you remember about this project's past incidents.
- **What changed recently:** `git log --since` around the start time, recent deploys, the user's own words ("desde que actualicé...").

Don't start fixing anything yet, and don't read deeply into any one system: that is what the scouts are for.

## 2. Map the systems

List every **scan target**: one system or surface that one scout can inspect on its own in a few minutes. For each, write down how to reach it (CLI and context, SSH host, MCP tool, log command) and rank them by suspicion.

`references/system-map.md` has, per kind of environment, how to discover the targets and the quick triage commands to use. Read the sections that apply.

Rules of thumb:

- A target is a unit with its own logs and health: one service, one database, one load balancer, the host itself, the network path. Not "the backend" when the backend is five services.
- Include the boring layers: host disk and memory, DNS, TLS certificates, the proxy, credentials and quotas, the third-party APIs the system calls. They break more often than they get suspected.
- If you can't tell how to reach a system, ask the user in one line, but don't block the other scouts on it.
- A system only reachable through a web dashboard is yours, not a scout's: open it in the built-in browser if the environment has one (in the Claude desktop app, the browser pane), Claude in Chrome only if the user asks or there is no built-in browser, and never the user's own browser (`open <url>`).

## 3. Quick sweep (you, one or two commands)

Before spawning anyone, run the one command per environment that shows the health of everything at once: `docker service ls`, `docker ps -a`, `kubectl get pods -A`, the ECS service list, `systemctl --failed`, `df -h` on the host. It takes seconds and often points straight at the culprit (a `0/1` replicas, a `CrashLoopBackOff`, a disk at 100%).

- **The sweep shows one clear culprit:** skip the fan-out and go to step 5 with it. Tell the user.
- **It shows several broken things:** find which one broke first (timestamps); the rest are probably symptoms. Scout them anyway.
- **It shows nothing or you can't run it:** fan out to every target.

## 4. Fan out the scouts

Spawn one scout per target, all in the same message so they run in parallel, in the background, on the smallest model: in Claude Code, the Agent tool with `model: "haiku"`, `subagent_type: "Explore"` (no file edits) or `general-purpose` if Explore is not available. Use the brief in `references/scout-brief.md`.

**How many at once.** Claude Code runs at most 20 subagents concurrently by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` changes it; past the limit, spawning fails). Be conservative and leave room for the escalation subagents and anything else running:

- send at most **half the limit, and never more than 10**: with the default, 10 scouts;
- if you have more targets than that, give the lowest-suspicion ones to the same scout in groups (one scout checks "DNS + TLS + CDN"), rather than queueing a second wave;
- with fewer than 3 targets, skip the scouts and check them yourself: spawning costs more than it saves.

**Scouts are read-only.** They read logs, status, metrics and config. They never restart, redeploy, scale, delete, write files, run migrations, or change settings, and never print secrets. Say so in the brief, every time: a fast model with shell access on production must not try to "fix" what it finds.

**Permissions.** Background scouts surface their permission prompts in your session. If the user will get many prompts, warn them in the same status line that sends the scouts out.

**No subagents here?** Check the targets yourself, one after another, in order of suspicion, with the same budget per target, and keep posting status lines.

## 5. Follow the hints

Don't wait for every scout. Act on the first strong hint as it arrives.

Each scout returns a verdict: `SUSPECT`, `CLEAN` or `UNREACHABLE`, with evidence. When a `SUSPECT` comes in, decide who digs:

| Situation | Who digs |
|---|---|
| The hint is clear and confirming it takes a few commands or one file | You, now. Fastest. |
| Confirming it needs a long dig in one system: big logs, a lot of code, a timeline to rebuild | A **Sonnet** subagent (`model: "sonnet"`) with the scout's findings in its brief. You keep coordinating and talking to the user. |
| The hints span several systems and need connecting, or the cause is subtle (race, config drift, a combination) | You. This is the reasoning the main agent is for. |
| You are stuck after one round of digging | One stronger subagent (`model: "opus"`) with everything gathered so far, or ask the user for what's missing (access, a time, a reproduction). |

Reading the scouts together:

- **Order by time.** The earliest anomaly is usually the cause; later errors downstream are symptoms. Line up the timestamps from every scout.
- **Two scouts pointing at the same dependency** (both api and worker can't reach postgres) point at that dependency, even if its own scout said `CLEAN`. Send it a second look.
- **`UNREACHABLE` is a finding,** not a gap: a scout that can't reach a system may be seeing the outage itself. Tell the user if it's a missing credential instead.
- **All `CLEAN`:** the target list is incomplete or the time window is wrong. Re-read the error, add the targets you skipped (the boring layers, the third parties, the client side), and tell the user what you've ruled out.

Once the cause is confirmed, stop the scouts still running (in Claude Code, TaskStop) so they don't burn time or prompt the user for nothing.

## 6. Confirm, then propose the fix

Confirm the cause with evidence, not with a plausible story: the log line, the metric, the config value, the commit, ideally a reproduction. If you can only say "probably", say "probably".

Then propose the fix. Who applies it:

- **Anything on a live or shared system** (restart, redeploy, rollback, scale, config or env change, freeing disk, rotating a credential): ask first, naming exactly what you will run and where. These are hard to undo and affect other people.
- **A code or local fix,** when the user asked you to fix it: go ahead, smallest change, and say how you verified it.
- **A workaround vs a fix:** if the quick way to restore service (restart, rollback) differs from the real fix (the memory leak, the missing index), offer both and say which is which.

## 7. Report

Short, in this order:

```
Causa: <one or two lines>
Evidencia: <the log line / metric / commit, with time and system>
Fix: <what to do, and whether you did it or are waiting for the go-ahead>
Descartado: <systems checked and clean, one line>
Sin revisar: <what nobody could check, and why>
```

If it was a recurring kind of problem for this project, offer to note it in the project's docs or memory so the next debug starts there.

## Common mistakes

| Mistake | Why it hurts |
|---|---|
| Spawning scouts before the quick sweep | One `docker service ls` would have shown the `0/1` in two seconds. |
| Deep-diving the system where the error shows up | That is usually where the symptom is, not the cause. |
| Waiting for every scout before acting | The user wants the answer, not the census. Act on the first strong hint. |
| Silent stretches | The user can't tell whether you're close or lost. Post a status line. |
| A scout "fixing" what it found | Restarting the crashed service destroys the evidence and may hide the cause. Scouts only read. |
| Using a big model for breadth | Slower and more expensive for work that is mostly reading logs. Haiku for breadth, bigger models only for depth. |
| Calling it found without evidence | A plausible cause that turns out wrong costs more time than one more check. |
