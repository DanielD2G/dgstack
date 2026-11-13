# Export Formats Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `tally export --format csv|markdown|json [--out PATH]` writes the expenses in that format.

**Architecture:** One module per format under `tally/export/`, each with a pure `export(expenses) -> str`. A small registry in `tally/export/__init__.py` finds a format's module by name, so formats never import each other. The CLI asks the registry.

**Tech Stack:** Python 3 standard library only (`csv`, `json`, `importlib`, `argparse`, `unittest`).

**Spec:** `docs/dgpowers/specs/2026-11-13-export-formats-design.md`

## Global Constraints

- Standard library only. No new dependencies.
- Every exporter returns text ending with exactly one `\n`.
- Every exporter sorts by `date` ascending, keeping stored order for equal dates (`sorted(expenses, key=lambda e: e.date)`).
- Amounts are shown with `tally.models.format_amount`.
- Tests use `unittest`; the whole suite is `python3 -m unittest discover -s tests`.

## Task Graph

| Wave | Tasks | Needs |
|------|-------|-------|
| 1 | Task 1 | nothing |
| 2 | Task 2, Task 3, Task 4 | Task 1 |
| 3 | Task 5 | Task 2, Task 3, Task 4 |

## Review Focus

- A description containing a comma or a double quote must survive a CSV round trip (Task 2).
- A description containing `|` must not break the Markdown table (Task 3).
- Non-ASCII descriptions ("Café") must stay readable in JSON, not `\u` escapes (Task 4).
- An empty expense list must still produce valid output in every format (Tasks 2, 3, 4).
- `get()` with a name outside `FORMATS` must not import anything (Task 1).

---

### Task 1: Format registry

**Depends on:** none

**Files:**
- Create: `tally/export/__init__.py`
- Test: `tests/test_export_registry.py`

**Interfaces:**
- Consumes: `tally.models.Expense`
- Produces:
  - `FORMATS: tuple[str, ...] = ("csv", "markdown", "json")`
  - `get(name: str) -> Callable[[list[Expense]], str]` — imports `tally.export.<name>_format` and returns its `export` function; raises `ValueError("unknown format: <name>")` for a name not in `FORMATS`, without importing.
  - Contract for format modules: `tally/export/<name>_format.py` defines `export(expenses: list[Expense]) -> str`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export_registry.py
import sys
import types
import unittest

from tally import export


class RegistryTests(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(export.FORMATS, ("csv", "markdown", "json"))

    def test_get_returns_the_modules_export_function(self):
        fake = types.ModuleType("tally.export.csv_format")
        fake.export = lambda expenses: "fake\n"
        sys.modules["tally.export.csv_format"] = fake
        try:
            self.assertIs(export.get("csv"), fake.export)
        finally:
            del sys.modules["tally.export.csv_format"]

    def test_unknown_format_raises_without_importing(self):
        with self.assertRaises(ValueError) as caught:
            export.get("os")
        self.assertEqual(str(caught.exception), "unknown format: os")
        self.assertNotIn("tally.export.os_format", sys.modules)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_export_registry -v`
Expected: FAIL with `ImportError: cannot import name 'export' from 'tally'`

- [ ] **Step 3: Implement `FORMATS` and `get(name)` in `tally/export/__init__.py`**

Check `name in FORMATS` first, then `importlib.import_module(f"tally.export.{name}_format").export`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_export_registry -v`
Expected: 3 tests, OK

- [ ] **Step 5: Commit**

```bash
git add tally/export/__init__.py tests/test_export_registry.py
git commit -m "feat: add export format registry"
```

---

### Task 2: CSV exporter

**Depends on:** Task 1

**Files:**
- Create: `tally/export/csv_format.py`
- Test: `tests/test_export_csv.py`

**Interfaces:**
- Consumes: `tally.models.Expense`, `tally.models.format_amount`; the module contract from Task 1.
- Produces: `export(expenses: list[Expense]) -> str` in `tally.export.csv_format`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export_csv.py
import csv
import io
import unittest

from tally.export.csv_format import export
from tally.models import Expense


class CsvExportTests(unittest.TestCase):
    def test_header_and_rows_sorted_by_date(self):
        text = export([
            Expense("2026-11-03", 480, "Bus"),
            Expense("2026-11-02", 1250, "Coffee beans"),
        ])
        self.assertEqual(
            text,
            "date,amount,description\n"
            "2026-11-02,12.50,Coffee beans\n"
            "2026-11-03,4.80,Bus\n",
        )

    def test_comma_and_quote_survive_a_round_trip(self):
        text = export([Expense("2026-11-02", 900, 'Bread, "sourdough"')])
        rows = list(csv.reader(io.StringIO(text)))
        self.assertEqual(rows[1], ["2026-11-02", "9.00", 'Bread, "sourdough"'])

    def test_empty_is_header_only(self):
        self.assertEqual(export([]), "date,amount,description\n")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_export_csv -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tally.export.csv_format'`

- [ ] **Step 3: Implement `export(expenses: list[Expense]) -> str` in `tally/export/csv_format.py`**

`csv.writer(buffer, lineterminator="\n")` over an `io.StringIO`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_export_csv -v`
Expected: 3 tests, OK

- [ ] **Step 5: Commit**

```bash
git add tally/export/csv_format.py tests/test_export_csv.py
git commit -m "feat: add CSV exporter"
```

---

### Task 3: Markdown exporter

**Depends on:** Task 1

**Files:**
- Create: `tally/export/markdown_format.py`
- Test: `tests/test_export_markdown.py`

**Interfaces:**
- Consumes: `tally.models.Expense`, `tally.models.format_amount`; the module contract from Task 1.
- Produces: `export(expenses: list[Expense]) -> str` in `tally.export.markdown_format`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export_markdown.py
import unittest

from tally.export.markdown_format import export
from tally.models import Expense


class MarkdownExportTests(unittest.TestCase):
    def test_table_sorted_by_date_with_total(self):
        text = export([
            Expense("2026-11-03", 480, "Bus"),
            Expense("2026-11-02", 1250, "Coffee beans"),
        ])
        self.assertEqual(
            text,
            "| Date | Amount | Description |\n"
            "|---|---:|---|\n"
            "| 2026-11-02 | 12.50 | Coffee beans |\n"
            "| 2026-11-03 | 4.80 | Bus |\n"
            "\n"
            "Total: 17.30\n",
        )

    def test_pipe_in_description_is_escaped(self):
        text = export([Expense("2026-11-02", 300, "Tea | herbal")])
        self.assertIn("| 2026-11-02 | 3.00 | Tea \\| herbal |\n", text)

    def test_empty_has_headers_and_zero_total(self):
        self.assertEqual(
            export([]),
            "| Date | Amount | Description |\n|---|---:|---|\n\nTotal: 0.00\n",
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_export_markdown -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tally.export.markdown_format'`

- [ ] **Step 3: Implement `export(expenses: list[Expense]) -> str` in `tally/export/markdown_format.py`**

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_export_markdown -v`
Expected: 3 tests, OK

- [ ] **Step 5: Commit**

```bash
git add tally/export/markdown_format.py tests/test_export_markdown.py
git commit -m "feat: add Markdown exporter"
```

---

### Task 4: JSON exporter

**Depends on:** Task 1

**Files:**
- Create: `tally/export/json_format.py`
- Test: `tests/test_export_json.py`

**Interfaces:**
- Consumes: `tally.models.Expense`; the module contract from Task 1.
- Produces: `export(expenses: list[Expense]) -> str` in `tally.export.json_format`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export_json.py
import json
import unittest

from tally.export.json_format import export
from tally.models import Expense


class JsonExportTests(unittest.TestCase):
    def test_structure_sorted_by_date_with_total(self):
        text = export([
            Expense("2026-11-03", 480, "Bus"),
            Expense("2026-11-02", 1250, "Coffee beans"),
        ])
        self.assertTrue(text.endswith("}\n"))
        data = json.loads(text)
        self.assertEqual(list(data), ["expenses", "total_cents"])
        self.assertEqual(
            data["expenses"],
            [
                {"date": "2026-11-02", "amount_cents": 1250, "description": "Coffee beans"},
                {"date": "2026-11-03", "amount_cents": 480, "description": "Bus"},
            ],
        )
        self.assertEqual(list(data["expenses"][0]), ["date", "amount_cents", "description"])
        self.assertEqual(data["total_cents"], 1730)

    def test_indent_and_non_ascii(self):
        text = export([Expense("2026-11-02", 350, "Café")])
        self.assertIn('\n  "expenses": [\n', text)
        self.assertIn('"description": "Café"', text)

    def test_empty(self):
        self.assertEqual(json.loads(export([])), {"expenses": [], "total_cents": 0})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_export_json -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tally.export.json_format'`

- [ ] **Step 3: Implement `export(expenses: list[Expense]) -> str` in `tally/export/json_format.py`**

`json.dumps(..., indent=2, ensure_ascii=False) + "\n"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_export_json -v`
Expected: 3 tests, OK

- [ ] **Step 5: Commit**

```bash
git add tally/export/json_format.py tests/test_export_json.py
git commit -m "feat: add JSON exporter"
```

---

### Task 5: `export` command

**Depends on:** Task 2, Task 3, Task 4

**Files:**
- Modify: `tally/cli.py`
- Modify: `README.md`
- Test: `tests/test_cli_export.py`

**Interfaces:**
- Consumes: `tally.export.FORMATS`, `tally.export.get(name)` (Task 1); the three exporters through the registry (Tasks 2, 3, 4).
- Produces: the `export` subcommand of `tally.cli.main`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli_export.py
import io
import tempfile
import unittest
from pathlib import Path

from tally import store
from tally.cli import main
from tally.models import Expense


class CliExportTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.file = str(Path(self.dir.name) / "expenses.json")
        store.save(
            [Expense("2026-11-03", 480, "Bus"), Expense("2026-11-02", 1250, "Coffee beans")],
            self.file,
        )

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        code = main(["--file", self.file, *argv], out=out)
        return code, out.getvalue()

    def test_csv_to_output(self):
        code, text = self.run_cli("export", "--format", "csv")
        self.assertEqual(code, 0)
        self.assertEqual(
            text,
            "date,amount,description\n2026-11-02,12.50,Coffee beans\n2026-11-03,4.80,Bus\n",
        )

    def test_markdown_and_json_to_output(self):
        code, text = self.run_cli("export", "--format", "markdown")
        self.assertEqual(code, 0)
        self.assertTrue(text.endswith("\nTotal: 17.30\n"))
        code, text = self.run_cli("export", "--format", "json")
        self.assertEqual(code, 0)
        self.assertIn('"total_cents": 1730', text)

    def test_out_writes_the_file_and_reports(self):
        target = str(Path(self.dir.name) / "out.csv")
        code, text = self.run_cli("export", "--format", "csv", "--out", target)
        self.assertEqual(code, 0)
        self.assertEqual(text, f"wrote 2 expenses to {target}\n")
        self.assertEqual(
            Path(target).read_text(encoding="utf-8"),
            "date,amount,description\n2026-11-02,12.50,Coffee beans\n2026-11-03,4.80,Bus\n",
        )

    def test_unknown_format_exits_2(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_cli("export", "--format", "xml")
        self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_cli_export -v`
Expected: FAIL, argparse rejects `export` (`SystemExit: 2`) in the first three tests

- [ ] **Step 3: Add the `export` subcommand to `build_parser()` and its branch to `main()` in `tally/cli.py`**

`--format` is required with `choices=FORMATS`; `--out` is optional. Without `--out`, write the text with `out.write(text)` (no extra newline). With `--out`, write the file as UTF-8 and print `wrote <n> expenses to <PATH>`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_cli_export -v`
Expected: 4 tests, OK

- [ ] **Step 5: Add an `export` example to `README.md`**

Under the existing examples, add:

```
    python3 -m tally export --format csv --out november.csv
```

- [ ] **Step 6: Run the whole suite**

Run: `python3 -m unittest discover -s tests`
Expected: 23 tests, OK

- [ ] **Step 7: Commit**

```bash
git add tally/cli.py README.md tests/test_cli_export.py
git commit -m "feat: add export command"
```
