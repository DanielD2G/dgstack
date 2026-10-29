#!/usr/bin/env python3
"""Simulated live systems for debug-it-quick evals.

Each shim in <env>/bin execs: sim.py <argv0> <args...>. The command line is
matched against the rules in <env>/data/sim.json (first match wins) and the
canned output is printed. Every call is appended to <env>/calls.log so grading
can check what the agent ran (and whether it ran anything mutating).

`ssh <host> <cmd>` is unwrapped: the remote command is split on && and ; and
each part dispatched; anything after the first | runs locally through sh, so
`ssh prod-1 "docker service logs x | grep ERROR"` behaves as expected.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time

ENV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ENV, "data", "sim.json")
LOG = os.path.join(ENV, "calls.log")
LATENCY = os.path.join(ENV, "data", "latency.json")

with open(DATA) as f:
    SIM = json.load(f)

# Optional per-command latency, so parallel checks can be compared against
# sequential ones the way they would behave against real servers.
LAT = None
if os.path.exists(LATENCY):
    with open(LATENCY) as f:
        LAT = json.load(f)


def wait(cmd=None, ssh=False):
    if not LAT:
        return
    if ssh:
        time.sleep(LAT.get("ssh", 0))
        return
    for pattern, seconds in LAT["rules"]:
        if re.search(pattern, cmd, re.I):
            time.sleep(seconds)
            return
    time.sleep(LAT.get("default", 0))

NOISE = re.compile(r"\s*(2>&1|2>/dev/null|>/dev/null)\s*")
PREFIX = re.compile(r"^\s*(sudo\s+(-\S+\s+)*|timeout\s+\d+\S*\s+|env\s+(\S+=\S+\s+)*)+")


def log(host, cmd, rule):
    with open(LOG, "a") as f:
        f.write(json.dumps({
            "t": time.strftime("%H:%M:%S"),
            "host": host,
            "cmd": cmd,
            "rule": rule.get("id") if rule else None,
            "mutating": bool(rule and rule.get("mutating")),
        }) + "\n")


def find_rule(host, cmd):
    for rule in SIM["rules"]:
        if "host" in rule and not re.search(rule["host"], host or ""):
            continue
        if rule.get("local_only") and host:
            continue
        if re.search(rule["match"], cmd, re.I | re.S):
            return rule
    return None


def render(rule):
    out = rule.get("out", "")
    if isinstance(out, list):
        out = "\n".join(out)
    if out and not out.endswith("\n"):
        out += "\n"
    return out, rule.get("err", ""), rule.get("exit", 0)


def dispatch(host, cmd):
    cmd = NOISE.sub(" ", cmd).strip()
    cmd = PREFIX.sub("", cmd)
    rule = find_rule(host, cmd)
    log(host, cmd, rule)
    wait(cmd)
    if rule is None:
        return "", "", 0
    return render(rule)


def run_remote(host, remote):
    status = 0
    for part in re.split(r"\s*(?:&&|;)\s*", remote):
        if not part.strip():
            continue
        head, _, tail = part.partition("|")
        out, err, code = dispatch(host, head)
        if err:
            sys.stderr.write(err if err.endswith("\n") else err + "\n")
        if tail.strip():
            p = subprocess.run(["sh", "-c", tail], input=out, text=True, capture_output=True)
            out = p.stdout
        sys.stdout.write(out)
        status = code
    return status


def ssh(args):
    hosts = SIM.get("ssh_hosts", {})
    i = 0
    with_value = set("bcDEeFIiJLlmOopQRSWw")
    while i < len(args) and args[i].startswith("-"):
        flag = args[i]
        i += 2 if (len(flag) == 2 and flag[1] in with_value) else 1
    if i >= len(args):
        sys.stderr.write("usage: ssh [options] destination [command]\n")
        return 255
    dest = args[i].split("@")[-1]
    remote = " ".join(args[i + 1:])
    if dest not in hosts:
        log(dest, remote, None)
        sys.stderr.write(f"ssh: Could not resolve hostname {dest}: nodename nor servname provided, or not known\n")
        return 255
    behaviour = hosts[dest]
    if isinstance(behaviour, dict) and behaviour.get("unreachable"):
        log(dest, remote, {"id": "unreachable"})
        sys.stderr.write(behaviour["unreachable"] + "\n")
        return 255
    if not remote.strip():
        sys.stderr.write("Pseudo-terminal will not be allocated; pass a command.\n")
        return 1
    wait(ssh=True)
    return run_remote(dest, remote)


def main():
    prog = os.path.basename(sys.argv[1])
    args = sys.argv[2:]
    if prog == "ssh":
        return ssh(args)
    cmd = prog + " " + " ".join(shlex.quote(a) if " " in a else a for a in args)
    rule = find_rule(None, NOISE.sub(" ", cmd).strip())
    # Filters such as `openssl x509` only answer when what's piped in matches.
    if rule and "stdin_match" in rule:
        piped = "" if sys.stdin.isatty() else sys.stdin.read()
        if not re.search(rule["stdin_match"], piped):
            log(None, cmd, rule)
            sys.stderr.write(rule.get("stdin_err", "unable to read input") + "\n")
            return 1
    out, err, code = dispatch(None, cmd)
    sys.stdout.write(out)
    if err:
        sys.stderr.write(err if err.endswith("\n") else err + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
