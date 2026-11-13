# tally

A tiny expense tracker: a JSON file of expenses and a command line to add
and list them. Standard library only.

    python3 -m tally add --date 2026-11-02 --amount 12.50 --description "Coffee beans"
    python3 -m tally list

Run the tests with:

    python3 -m unittest discover -s tests -v
