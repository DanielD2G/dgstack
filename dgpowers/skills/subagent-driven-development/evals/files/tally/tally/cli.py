import argparse
import sys

from tally import store
from tally.models import Expense, format_amount, parse_amount


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tally", description="A tiny expense tracker.")
    parser.add_argument("--file", default=store.DEFAULT_FILE, help="expenses file")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="add an expense")
    add.add_argument("--date", required=True)
    add.add_argument("--amount", required=True)
    add.add_argument("--description", required=True)

    commands.add_parser("list", help="list every expense")
    return parser


def main(argv: list[str], out=sys.stdout) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "add":
        try:
            cents = parse_amount(args.amount)
        except ValueError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        store.add(Expense(args.date, cents, args.description), args.file)
        print(f"added {format_amount(cents)} {args.description}", file=out)
        return 0

    if args.command == "list":
        for e in store.load(args.file):
            print(f"{e.date}  {format_amount(e.amount_cents):>8}  {e.description}", file=out)
        return 0

    return 2
