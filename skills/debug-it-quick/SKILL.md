---
name: debug-it-quick
description: Fast debugging of a live problem across one or many systems, with the user kept posted the whole time. Sweep the health of everything at once, test the strongest lead directly, confirm with evidence, and ask before touching anything live. Cheap parallel Haiku scouts are a last resort for when the sweep leaves no lead. Works on services in Docker Swarm, Compose or Kubernetes, Dokploy or Coolify hosts, AWS and other clouds, databases, DNS and TLS, CI, the repo and the user's own machine. Use it whenever the user pastes an error, a log, a stack trace or a symptom and wants it found fast ("debug it quick", "debugeá esto", "¿por qué falla?", "se cayó", "está caído", "no levanta", "tira 502", "anda lentísimo", "el contenedor se reinicia", "no me anda", "algo se rompió en prod", "mi PC está lenta"), including problems that are not in code at all. Not for building features or for slow, test-first fixing of a bug whose location is already known.
---

# debug-it-quick

Something is broken and the user wants to know where, fast. The cause is often not where the error shows up (a 502 at the proxy is a crashed service, which is a full connection pool, which is a config change), and often not in code at all.

What makes this fast: one sweep that shows the health of everything, then a direct test of the best lead. In practice the sweep almost always produces a lead. What makes it pleasant: the user always knows what you're checking and what you've found.

Talk to the user in their language (usually Spanish), briefly.

## Keep the user posted

Send a short status line at each of these moments. A run with no updates until the answer feels broken even when it's fast.

1. after reading the context: what the symptom suggests and what you'll sweep;
2. after the sweep: what it showed and the lead you're testing (or that there's none);
3. when you confirm the cause (or the lead dies and you move on).

Plain text, no emojis, times in the user's timezone with UTC alongside when the logs are UTC:

```
Barrido: los 7 servicios arriba, pero 1 de cada 3 pagos da 504 desde las 11:20 (14:20 UTC). Pruebo el proveedor de pagos.
```

## 1. Read the context (a minute)

- **The error:** pull out service names, hosts, URLs, status codes and above all the **time** it started.
- **Project instructions and infra files:** `CLAUDE.md`/`AGENTS.md`, README, `docker-compose*.yml`, stack files, manifests, Terraform, CI workflows, proxy config. They name the systems and how to reach them.
- **What changed:** `git log` with dates around the start time, recent deploys, the user's own words. Keep looking further back when nothing changed yesterday: a change days ago can take days to bite (something slowly filling up, something slowly expiring).

Don't read deeply into any one system yet.

## 2. Sweep everything at once

Run the few commands that show the whole picture, on **every** host or account involved:

- service and container state: `docker service ls`, `docker ps -a`, `kubectl get pods -A`, the ECS service list, `systemctl --failed`;
- host resources on each node: `df -h`, `free -m`;
- **request durations and status codes in the proxy's access log** (Traefik, nginx, ALB): it shows which routes are slow or failing and which aren't, which is often the whole answer for "slow" or "intermittent";
- get the time from the servers (`date -u` over SSH, log timestamps), not your local clock.

`references/system-map.md` has the sweep and follow-up commands per environment (Swarm, Kubernetes, AWS, DNS/TLS, the local machine...). Read only the section for an environment you don't already know how to triage. Prefer CLIs and APIs; if a system is only visible in a web dashboard, open it in the built-in browser when the environment has one (in the Claude desktop app, the browser pane), Claude in Chrome only if the user asks or there is no built-in browser, and never the user's own browser (`open <url>`).

## 3. Test the strongest lead yourself

A lead is anything that points at one place: a service at `0/2`, a disk at 100%, a change that lines up with the start time, slow routes that share a dependency. Test it with the one or two commands that would prove or kill it (the stopped task's reason, the connection count, the dependency's own logs or status page). Follow the chain until you reach a cause, not a symptom: the earliest anomaly in time is usually it.

If the lead dies, take the next one. If you run out of leads, go to step 4.

## 4. Last resort: scouts

Only when the sweep and your leads point nowhere and there are several systems left to check. Spawn one read-only Haiku scout per remaining system, all in one message (Claude Code: Agent tool, `model: "haiku"`, `subagent_type: "Explore"`), with the brief in `references/scout-brief.md`. Keep checking yourself while they run, act on the first strong hint, and stop the rest once the cause is confirmed.

Send at most half of the concurrent-subagent limit (20 by default in Claude Code, set by `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`) and never more than 10; group low-suspicion systems into one scout. Scouts never restart, deploy, delete or edit anything, and never print secrets: say so in every brief.

## 5. Confirm, then propose the fix

Confirm with evidence: the log line, the metric, the config value, the commit. Check that the cause explains **all** of the symptom ("some users fail and others don't", "only some pages"); if part is unexplained, say so.

Then the fix:

- **Anything on a live system** (restart, redeploy, rollback, scale, env change, freeing disk, DNS): ask first, naming exactly what you'll run and where, and what it costs (a restart cuts traffic, a truncate loses logs).
- **Something you can't reach** (a registrar's panel, a console you have no access to): give the user the exact steps and how to check it worked.
- **Workaround vs fix:** if restoring service now differs from the real fix, offer both and say which is which. If a live change would be undone by the next deploy, say so.
- **A code fix**, when the user asked for it: smallest change, then say how you verified it.

## 6. Report

```
Causa: <one or two lines, including why the symptom looks the way it does>
Evidencia: <log lines / metrics / commit, with time and system>
Fix: <what to do, and what you're waiting on the user for>
Descartado: <what you checked and found healthy>
Sin revisar: <what you skipped on purpose because the cause was confirmed, and what you couldn't reach>
```

If it's a kind of problem likely to come back, offer to note it in the project's docs.

## Common mistakes

| Mistake | Why it hurts |
|---|---|
| Sweeping only the host the error points at | The cause is often on a machine nobody was looking at. |
| Skipping the proxy's access log on "slow" or "intermittent" | It shows which routes are affected in one command. |
| Waiting for scouts when you already had a lead | Minutes to hear what one direct check would have said. |
| Silent stretches | The user can't tell whether you're close or lost. |
| Blaming the loudest error | Old, recurring errors (a cron that fails every night, a warning logged since boot) are rarely today's cause. Line them up with the start time. |
| Restarting what's broken to "see if it helps" | It destroys the evidence and may hide the cause. Ask first. |
