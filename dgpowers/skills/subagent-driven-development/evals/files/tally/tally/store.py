import json
from pathlib import Path

from tally.models import Expense

DEFAULT_FILE = "expenses.json"


def load(path: str = DEFAULT_FILE) -> list[Expense]:
    """Read every expense from the file. A missing file is an empty list."""
    file = Path(path)
    if not file.exists():
        return []
    rows = json.loads(file.read_text(encoding="utf-8"))
    return [Expense(r["date"], r["amount_cents"], r["description"]) for r in rows]


def save(expenses: list[Expense], path: str = DEFAULT_FILE) -> None:
    rows = [
        {"date": e.date, "amount_cents": e.amount_cents, "description": e.description}
        for e in expenses
    ]
    Path(path).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def add(expense: Expense, path: str = DEFAULT_FILE) -> None:
    expenses = load(path)
    expenses.append(expense)
    save(expenses, path)
