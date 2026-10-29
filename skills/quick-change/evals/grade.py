"""Grade quick-change eval runs.

Layout: <iteration>/eval-<id>-<name>/<config>/run-<n>/{repo/, outputs/response.md, judge.json?}

File assertions are checked by diffing repo/ against the fixture. Judge assertions
are read from judge.json ({"<assertion id>": {"passed": bool, "evidence": str}}),
written by a human or a grader agent after reading outputs/response.md.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def changed_files(fixture: Path, repo: Path) -> list[str]:
    out = subprocess.run(["diff", "-rq", str(fixture), str(repo)], capture_output=True, text=True).stdout
    files = []
    for line in out.splitlines():
        m = re.match(r"Files (.+) and (.+) differ", line)
        if m:
            files.append(str(Path(m.group(2)).relative_to(repo)))
        m = re.match(r"Only in (.+): (.+)", line)
        if m:
            path = Path(m.group(1)) / m.group(2)
            base = repo if str(path).startswith(str(repo)) else fixture
            files.append(str(path.relative_to(base)))
    return sorted(files)


def grade_run(run_dir: Path, ev: dict, fixture: Path) -> dict:
    repo = run_dir / "repo"
    changes = changed_files(fixture, repo)
    diff = subprocess.run(["diff", "-ruN", str(fixture), str(repo)], capture_output=True, text=True).stdout
    diff = diff.replace(str(fixture) + "/", "a/").replace(str(repo) + "/", "b/")
    (run_dir / "outputs" / "changes.diff.txt").write_text(diff or "(no changes)\n")

    judge_path = run_dir / "judge.json"
    judge = json.loads(judge_path.read_text()) if judge_path.exists() else {}

    expectations = []
    for a in ev["assertions"]:
        if a["type"] == "files":
            extra = [f for f in changes if f not in a["allowed_changes"]]
            missing = a["require_change"] and not changes
            passed = not extra and not missing
            evidence = f"changed: {changes or 'none'}"
        elif a["type"] in ("grep_absent", "grep_present"):
            target = repo / a["file"]
            found = target.exists() and re.search(a["pattern"], target.read_text()) is not None
            passed = found if a["type"] == "grep_present" else not found
            evidence = f"pattern {a['pattern']!r} {'found' if found else 'not found'} in {a['file']}"
        else:
            j = judge.get(a["id"])
            passed = bool(j and j["passed"])
            evidence = j["evidence"] if j else "not judged yet"
        expectations.append({"text": a["text"], "passed": passed, "evidence": evidence})

    n_pass = sum(e["passed"] for e in expectations)
    grading = {
        "expectations": expectations,
        "summary": {
            "passed": n_pass,
            "failed": len(expectations) - n_pass,
            "total": len(expectations),
            "pass_rate": round(n_pass / len(expectations), 2),
        },
    }
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2, ensure_ascii=False))
    return grading


def main(iteration: Path):
    spec = json.loads((HERE / "evals.json").read_text())
    fixture = (HERE / "fixture").resolve()
    for ev in spec["evals"]:
        eval_dir = iteration / f"eval-{ev['id']}-{ev['name']}"
        if not eval_dir.exists():
            continue
        (eval_dir / "eval_metadata.json").write_text(
            json.dumps(
                {"eval_id": ev["id"], "eval_name": ev["name"], "prompt": ev["prompt"], "assertions": [a["text"] for a in ev["assertions"]]},
                indent=2,
                ensure_ascii=False,
            )
        )
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            # The review viewer looks for metadata next to the run, not two levels up.
            (run_dir / "eval_metadata.json").write_text((eval_dir / "eval_metadata.json").read_text())
            g = grade_run(run_dir, ev, fixture)
            print(f"{eval_dir.name:45} {run_dir.parent.name:14} {g['summary']['passed']}/{g['summary']['total']}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
