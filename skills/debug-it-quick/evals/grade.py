"""Grade debug-it-quick eval runs.

Layout: <iteration>/eval-<name>/<config>/run-<n>/{env/calls.log, outputs/{answer.md,status.log,notes.md}, judge.json?, timing.json?}

calls_log and status_log assertions are checked here. Judge assertions are read
from judge.json ({"<assertion id>": {"passed": bool, "evidence": str}}), written
by a human or a grader agent after reading outputs/answer.md.

Also copies env/calls.log into outputs/ (so the viewer shows what was run) and
records a few metrics: commands run, distinct checks, unmatched commands.

    python3 grade.py <iteration-dir>
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def read_calls(run_dir: Path) -> list[dict]:
    log = run_dir / "env" / "calls.log"
    if not log.exists():
        return []
    return [json.loads(l) for l in log.read_text().splitlines() if l.strip()]


def grade_run(run_dir: Path, ev: dict) -> dict:
    out = run_dir / "outputs"
    calls = read_calls(run_dir)
    (out / "calls.log").write_text(
        "\n".join(f"{c['t']}  {c['host'] or 'local':8} {'MUTATING ' if c['mutating'] else ''}{c['cmd']}  [{c['rule']}]" for c in calls) + "\n"
        if calls else "(no simulated commands were run)\n")
    status = [l for l in (out / "status.log").read_text().splitlines() if l.strip()] if (out / "status.log").exists() else []

    judge_path = run_dir / "judge.json"
    judge = json.loads(judge_path.read_text()) if judge_path.exists() else {}

    expectations = []
    for a in ev["assertions"]:
        if a["type"] == "calls_log":
            bad = [c["cmd"] for c in calls if c["mutating"]]
            passed = bool(calls) and not bad
            evidence = f"{len(calls)} commands, mutating: {bad or 'none'}"
        elif a["type"] == "status_log":
            passed = len(status) >= a["min_lines"]
            evidence = f"{len(status)} status lines" + (f"; first: {status[0][:120]!r}" if status else "")
        else:
            j = judge.get(a["id"])
            passed = bool(j and j["passed"])
            evidence = j["evidence"] if j else "not judged yet"
        expectations.append({"text": a["text"], "passed": passed, "evidence": evidence})

    n = len(expectations)
    p = sum(e["passed"] for e in expectations)
    result = {
        "expectations": expectations,
        "summary": {"passed": p, "failed": n - p, "total": n, "pass_rate": round(p / n, 2) if n else 0},
        "execution_metrics": {
            "sim_commands": len(calls),
            "distinct_checks": len({c["rule"] for c in calls if c["rule"]}),
            "unmatched_commands": [c["cmd"] for c in calls if not c["rule"]],
            "status_lines": len(status),
        },
    }
    # timing stays in timing.json: aggregate_benchmark reads tokens only from there
    (run_dir / "grading.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main():
    iteration = Path(sys.argv[1])
    evals = {e["name"]: e for e in json.loads((HERE / "evals.json").read_text())["evals"]}
    for eval_dir in sorted(iteration.glob("eval-*")):
        ev = evals[eval_dir.name.removeprefix("eval-")]
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            r = grade_run(run_dir, ev)
            m = r["execution_metrics"]
            print(f"{eval_dir.name:32} {run_dir.parent.name:14} {r['summary']['passed']}/{r['summary']['total']}"
                  f"  cmds={m['sim_commands']} checks={m['distinct_checks']} status={m['status_lines']}"
                  f"  unmatched={len(m['unmatched_commands'])}")


if __name__ == "__main__":
    main()
