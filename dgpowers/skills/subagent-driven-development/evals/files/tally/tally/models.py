from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    """One expense. Money is kept in cents to avoid float drift."""

    date: str  # ISO date, YYYY-MM-DD
    amount_cents: int
    description: str


def parse_amount(text: str) -> int:
    """Turn "12.50" or "12" into cents. Raises ValueError on anything else."""
    whole, _, frac = text.strip().partition(".")
    if not whole.isdigit() or (frac and not frac.isdigit()) or len(frac) > 2:
        raise ValueError(f"not an amount: {text!r}")
    return int(whole) * 100 + int(frac.ljust(2, "0") or 0)


def format_amount(cents: int) -> str:
    """Turn cents into "12.50"."""
    return f"{cents // 100}.{cents % 100:02d}"
