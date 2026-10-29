"""Script checks for roast-it evals. Judge assertions are graded separately.
   python3 evals/grade.py <run-dir>   (run-dir holds outputs/answer.md)
Prints JSON: [{"id", "passed", "evidence"}]."""
import json, re, sys
from pathlib import Path

run = Path(sys.argv[1])
text = (run / "outputs" / "answer.md").read_text()
lines = [l for l in text.splitlines() if l.strip()]
head = " ".join(lines[:3]).lower()

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆↔-⇿✅❌]")
VERDICT = re.compile(r"veredicto|verdict|no lo har|no lo merge|no tiene sentido|mergealo|mergeable|se puede mergear|sobrevive|aguanta|así como está|no\.|sí\b|no,")

out = []
m = VERDICT.search(head)
out.append({"id": "verdict-up-front", "passed": bool(m), "evidence": lines[0][:160] if lines else ""})
e = EMOJI.findall(text)
out.append({"id": "no-emojis", "passed": not e, "evidence": "none" if not e else " ".join(sorted(set(e)))})
links = re.findall(r"https://docs\.aws\.amazon\.com/\S+", text)
out.append({"id": "cites-official-docs", "passed": bool(links), "evidence": links[0] if links else "no docs.aws.amazon.com link"})
print(json.dumps(out, ensure_ascii=False, indent=1))
