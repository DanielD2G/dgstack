---
name: backtrack-for-test
description: Backfills tests for code that was changed without them, typically after a run of quick changes, using judgment about what deserves a test and what does not, and writing them in the project's own test setup. Use it whenever the user asks to test what was just changed or to catch up on tests after fast iteration ("backtrack for test", "testeá lo que cambiamos", "armá los tests de estos cambios", "cubrí con tests lo que hicimos", "faltan tests de esto"), at the end of a quick-change session, and when a background test agent is told to load it. Not for test-driven development of a new feature, or for repairing an existing failing suite unrelated to the recent changes.
---

# backtrack-for-test

Changes landed fast and without tests, usually through quick-change mode. Your job is to look back at what changed, add the tests that earn their keep, run them, and deal with what they find.

The value here is judgment. A few tests that would catch a real regression beat many tests that pin markup and break on the next copy tweak. Testing everything is as wrong as testing nothing.

Talk to the user in their language (usually Spanish), briefly.

## Two modes

- **Interactive (default).** The user invoked you in the conversation. They are there: ask before touching product code or installing anything, and don't commit unless they ask.
- **Background.** You are a subagent launched by `subagent-for-test`, and your brief says so. There is no user to ask. Follow the steps below **and** read `references/background-mode.md`, which covers working alongside the main agent, commits, rounds, and escalation.

## 1. Find what changed

- **Base:** use the one in your brief, or the default branch (`git symbolic-ref refs/remotes/origin/HEAD`, falling back to `main`/`master`) and `git merge-base HEAD <default>`.
- **Committed:** `git log --oneline <base>..HEAD` and `git diff <base>...HEAD`.
- **Uncommitted:** `git status --porcelain`, `git diff`, `git diff --cached`, and untracked files. Quick-change doesn't commit, so most of the work may live here.
- If the user names a scope ("los últimos 3 commits", "solo lo del carrito"), use that instead.

Read each diff together with the code around it, and work out the intent of each change from commit messages and the conversation. Group the changes into units of behavior: one change can span several files, and one file can hold unrelated changes.

## 2. Decide what to test

Test what can break in a way a user or another part of the code would notice, and that a test can catch cheaply.

| Test it | Skip it |
|---|---|
| Logic: conditions, branches, calculations, parsing and formatting, client-side sort or filter | Copy, styles, classNames, spacing, colors |
| Data mapping between API and UI, defaults, empty and null handling | Static markup moved, reordered or removed, with no logic behind it |
| UI behavior with a rule: shown or hidden by state or permission, disabled until valid, the modal closes after save, the loading, empty and error states the change introduced | Wiring that only connects framework pieces without making a decision |
| Backend: validation, handlers, and messages or values other code depends on | Code an existing test already exercises (run that test instead) |
| A bug fixed during the changes: a regression test that would fail without the fix | Removals that leave nothing to observe |
| A removal that changes behavior (a request no longer sent, a step no longer required) | Snapshot-everything tests |

Borderline cases:

- **User-visible text that something depends on:** a message the front end matches on, or a value another client parses. Test that contract, not the wording.
- **Pick the cheapest level that catches it:** unit, then component, then integration, then end-to-end. Go up a level only when the behavior lives in how the pieces interact.

Before writing, show a short plan: each change unit, then test or no test, then why in a few words. In interactive mode, show it and go ahead unless something in it needs the user's call. The user can stop you.

## 3. Learn the project's test setup

- Find the framework and conventions: config files (vitest, jest, playwright, cypress, pytest, go test…), package scripts, existing tests near the changed files, and helpers, fixtures, factories and mocks.
- Mirror the closest existing test: its location, naming, imports, helpers and style. A new test should look as if the team wrote it.
- Find out how to run a single file or filter, and how to run the whole suite.
- **No setup for the level you need:**
  - **A runner you can use without installing anything:** use it without asking. The user wants tests, not a question about tooling. Pick in this order:
    1. A common framework the project already has: declared or installed in its environment (`node_modules`, the virtualenv, the lockfile, the build file). A framework installed only globally on this machine doesn't count, because teammates and CI couldn't run the tests.

       | Stack | Frameworks |
       |---|---|
       | JS/TS | vitest, jest, mocha, playwright |
       | Python | pytest |
       | Ruby | rspec, minitest |
       | PHP | phpunit, pest |
       | JVM | JUnit (via Maven or Gradle), kotest |
       | .NET | `dotnet test` (xUnit, NUnit, MSTest) |
       | Elixir | `mix test` |
       | Swift | `swift test` / XCTest |
    2. Otherwise, the runner that ships with the language: `node:test` (Node 18+), `bun test`, `deno test`, Python's `unittest`, `go test`, `cargo test`.

    Add only the minimal script or config to run it (e.g. `"test": "node --test"` in `package.json`, or a `[tool.pytest.ini_options]` block only if pytest needs one to find the tests). Mention it in the report.
  - **Anything that needs installing** (a framework or a dependency): don't install it. In interactive mode, ask and propose the lightest option. In background mode, escalate.

## 4. Live checks: reuse the server that is already running

Committed tests use the suite's own setup (mocks, test database, test server) unless the project's e2e tests are already designed to target a running app. Live checks are separate: requests or browser checks against the running page or backend, to confirm something end to end. They are not committed.

Before any live check:

1. **Look for what is already running:**
   - listening ports: `lsof -nP -iTCP -sTCP:LISTEN`;
   - each process's command and working directory: `ps -p <pid> -o command=`, `lsof -a -p <pid> -d cwd`;
   - any preview or dev-server list your tools offer;
   - the user's terminal tabs, if you can read them;
   - ports declared in the project (`.claude/launch.json`, package scripts, `.env`, `docker-compose`).
2. **Confirm it serves this checkout:** its working directory must be this repo or worktree. A server from another checkout serves different code.
3. **Use it as it is.** Never restart it, kill it, change its environment, or start a second instance next to it. If it serves stale code (no hot reload), say so instead of restarting it.
4. **If nothing is running:** in interactive mode, ask whether to start one. In background mode, skip the live check and note it in the report, or escalate if the check is essential.
5. **For browser checks,** use the built-in browser if your environment has one (in the Claude desktop app, the browser pane). Use Claude in Chrome only if the user asks for it or there is no built-in browser. Never open the page in the user's own browser (`open <url>`). With no browser at all, check over HTTP (`curl`) and say what you couldn't see.
6. **On a shared dev backend,** prefer read-only checks. If you must create data, label it clearly (`test-backtrack-…`) and delete what you created. Never run destructive operations: drops, resets, migrations or seeds.

## 5. Write and run

- Write the tests from the plan. Each test's name states the behavior ("hides the export button for viewers"), not the implementation.
- Assert on behavior: what the user sees, what gets sent, what gets returned. Avoid internal state and class names unless they are the behavior.
- **Make sure each test can fail.** A test that passes no matter what is worse than none. When in doubt, flip the expected value once, watch it fail, and restore it.
- Run the new tests, then the existing tests around the touched code. Run the full suite at the end if it takes a few minutes or less; otherwise say you didn't.

## 6. When a test finds a problem

| What it is | Interactive | Background |
|---|---|---|
| The test is wrong (bad setup, or a wrong assumption about intent that the code or the conversation makes clear) | Fix the test | Fix the test |
| Product bug, small and local, with obvious intended behavior (wrong condition, missing null check, off-by-one) | Show it in two lines and ask before fixing | Fix it, keep the regression test |
| Intent is ambiguous (is the code right or the test?), the fix isn't local, or it touches shared code, business rules or the API contract. Money, pricing, permissions and what gets saved always count here, even for a one-line fix. | Ask | Escalate |
| Flaky or environment failure | Re-run once, then report | Re-run once, then escalate if it blocks |
| Failure that existed before these changes | Report it, don't fix | Report it, don't fix |

Never weaken, skip or delete a test just to get a green run.

## 7. Report (interactive)

Keep it short:

- **tests added:** file → the behaviors covered;
- **deliberately not tested:** grouped, one line each, with the reason;
- **problems found** and what happened to each;
- **how you ran them:** the command and the result, including whether the full suite ran;
- **what you couldn't do:** no server for a live check, no setup for a level.

Don't commit unless the user asks. If they do, commit by path, only the test files and the fixes they approved: `git commit -m "<msg>" -- <paths>`. Never `git add -A`.
