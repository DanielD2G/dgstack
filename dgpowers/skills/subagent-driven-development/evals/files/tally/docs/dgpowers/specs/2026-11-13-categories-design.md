# Categories for expenses

Status: approved on 2026-11-13.

## Intent

A flat list of expenses stops being useful after a month: people want to
know how much went to food versus transport. We want each expense to
carry a category, and `list` to filter and total by it.

## Goals, non-goals, anti-goals

- Goal: every expense has a category; old files without one keep
  working.
- Goal: `tally list --category food` shows only that category;
  `tally list --by-category` shows a total per category.
- Non-goal: a fixed list of categories, renaming, budgets.
- Anti-goal: a migration step the person has to run. Old files are read
  as they are.

## Approaches

1. **A `category` field on `Expense`, defaulted when missing** (picked):
   one field, read with a default, written always.
2. A separate `categories.json` mapping descriptions to categories:
   keeps the model untouched but splits the truth across two files.
3. Tags (many per expense): more flexible than anyone asked for.

## Design

**Model** (`tally/models.py`):

- `Expense` gets a fourth field, `category: str = "uncategorized"`.
- New `normalize_category(text) -> str`: strips, lowercases, and turns
  an empty string into `"uncategorized"`.

**Store** (`tally/store.py`):

- `load` reads `category` from each row, using `"uncategorized"` when
  the key is missing (old files).
- `save` always writes `category`.
- The key order in the file is `date`, `amount_cents`, `description`,
  `category`.

**CLI** (`tally/cli.py`):

- `add` gets an optional `--category`; the value goes through
  `normalize_category`. Its confirmation line becomes
  `added 12.50 Coffee beans [food]`.
- `list` prints the category as a last column:
  `2026-11-02     12.50  Coffee beans  [food]`.
- `list --category NAME` shows only expenses whose category equals
  `normalize_category(NAME)`.
- `list --by-category` prints one line per category, sorted by name:
  `food        25.00`, the name left-aligned in 12 columns, then the
  amount right-aligned in 8.
- `--category` and `--by-category` together: argparse error, exit 2.

**Docs:** the README shows `--category` and `--by-category`.

## UI map

No front-end changes.

## Left to the builder

Whether the per-category totals live in `cli.py` or a small helper.
