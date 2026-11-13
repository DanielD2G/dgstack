import io
import tempfile
import unittest
from pathlib import Path

from tally.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.file = str(Path(self.dir.name) / "expenses.json")

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        code = main(["--file", self.file, *argv], out=out)
        return code, out.getvalue()

    def test_add_and_list(self):
        code, text = self.run_cli("add", "--date", "2026-11-02", "--amount", "12.50", "--description", "Coffee beans")
        self.assertEqual(code, 0)
        self.assertEqual(text, "added 12.50 Coffee beans\n")
        code, text = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertEqual(text, "2026-11-02     12.50  Coffee beans\n")

    def test_add_rejects_bad_amount(self):
        code, _ = self.run_cli("add", "--date", "2026-11-02", "--amount", "abc", "--description", "x")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
