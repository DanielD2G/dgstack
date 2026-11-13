import tempfile
import unittest
from pathlib import Path

from tally import store
from tally.models import Expense


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = str(Path(self.dir.name) / "expenses.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_missing_file_is_empty(self):
        self.assertEqual(store.load(self.path), [])

    def test_add_then_load_round_trips(self):
        store.add(Expense("2026-11-02", 1250, "Coffee beans"), self.path)
        store.add(Expense("2026-11-03", 480, "Bus"), self.path)
        self.assertEqual(
            store.load(self.path),
            [Expense("2026-11-02", 1250, "Coffee beans"), Expense("2026-11-03", 480, "Bus")],
        )


if __name__ == "__main__":
    unittest.main()
