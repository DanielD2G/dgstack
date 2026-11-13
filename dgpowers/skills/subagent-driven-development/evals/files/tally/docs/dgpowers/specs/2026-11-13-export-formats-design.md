# Export expenses in three formats

Status: approved on 2026-11-13.

## Intent

People keep their expenses in tally and then need them somewhere else: a
spreadsheet for the accountant, a note for a housemate, another program.
Today the only way out is copying the `list` output by hand. We want an
`export` command that writes the expenses as CSV, Markdown or JSON.

## Goals, non-goals, anti-goals

- Goal: `tally export --format csv|markdown|json` prints the expenses in
  that format; `--out PATH` writes them to a file instead.
- Goal: adding a fourth format later means adding one module, without
  editing the others.
- Non-goal: importing. Non-goal: filtering by date.
- Anti-goal: any third-party dependency. Standard library only.

## Approaches

1. **One module per format behind a small registry** (picked): each
   format is a module with one `export(expenses) -> str` function; the
   registry finds a format's module by name. Formats don't know about
   each other.
2. One `export.py` with three functions and an if/else: less code today,
   but every new format edits the same file.
3. Classes with a base `Exporter`: more ceremony than three pure
   functions need.

## Design

**Registry** (`tally/export/__init__.py`):

- `FORMATS = ("csv", "markdown", "json")`.
- `get(name) -> Callable[[list[Expense]], str]`: imports
  `tally.export.<name>_format` and returns its `export` function.
  An unknown name raises `ValueError("unknown format: <name>")` and
  never tries to import anything.
- Every exporter receives the expenses in stored order and sorts them
  itself by date, ascending, keeping stored order for equal dates.
- Every exporter returns text that ends with exactly one newline.

**CSV** (`tally/export/csv_format.py`):

- Header row `date,amount,description`.
- `amount` is `format_amount(amount_cents)`, e.g. `12.50`.
- Written with the `csv` module, default dialect, `\n` line endings, so a
  description with a comma or a quote is quoted correctly.
- No expenses: the header row only.

**Markdown** (`tally/export/markdown_format.py`):

- A table:

  ```
  | Date | Amount | Description |
  |---|---:|---|
  | 2026-11-02 | 12.50 | Coffee beans |

  Total: 12.50
  ```

- A `|` in a description is written as `\|`.
- After the table, a blank line and `Total: <sum>`.
- No expenses: the two header lines, a blank line and `Total: 0.00`.

**JSON** (`tally/export/json_format.py`):

- `{"expenses": [{"date": ..., "amount_cents": ..., "description": ...}], "total_cents": N}`
- Keys in that order, `indent=2`, `ensure_ascii=False`.
- No expenses: `"expenses": []` and `"total_cents": 0`.

**CLI** (`tally/cli.py`):

- New command `export` with `--format` (required, choices are
  `FORMATS`) and `--out PATH` (optional).
- Without `--out`, the text is written to the command's output as is
  (no extra newline).
- With `--out`, the text is written to that file as UTF-8 and the
  command prints `wrote <n> expenses to <PATH>`.
- An unknown format is rejected by argparse (exit code 2).
- The README gets an `export` example.

## UI map

No front-end changes.

## Left to the builder

How each exporter is structured internally.
