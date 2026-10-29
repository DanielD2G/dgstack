# Background mode

You were launched by `subagent-for-test` as a background agent. The user and the main agent keep working in **this same checkout** while you work. There is no user to ask: you decide what is yours to decide, commit your own work, and escalate the rest through the main agent.

Your brief gives you the repo, branch, base, HEAD at launch, running servers, known test commands, and a list of changes with their intent. Treat the brief's intent notes as the source of truth for what the code is supposed to do.

## Who owns what

- **Test files you create or edit are yours.** The main agent won't touch them.
- **Product code belongs to the main agent.** Touch it only for the small, local, obvious fixes in SKILL.md step 6, and only like this:
  1. Re-read the file right before editing it. If it changed since your last read, re-evaluate the fix against the new version.
  2. Don't edit lines the most recent update changed. They may still be in flux. Wait for the next round, or escalate if it blocks.
  3. If the file already has uncommitted changes that aren't yours (`git diff --quiet -- <file>` fails before your edit), apply the fix but **don't commit it**. List it under "Uncommitted" in your report so it goes in with the user's changes.
- **Config files you touch to run tests** (e.g. a `test` script in `package.json` for a built-in runner) follow the same rules as product code.

## Git: what you may and may not run

You may:

- run read commands freely: `status`, `diff`, `log`, `show`, `merge-base`;
- commit your own paths only, by pathspec: `git commit -m "<msg>" -- <path> <path>…`. New files need `git add -- <path>` first.

Never, because each one pulls the floor out from under the user:

- `git add -A`, `git add .`, `commit -a`;
- `stash`;
- `checkout` or `restore` of files;
- `switch`, or changing branches;
- `reset`, `rebase`, `commit --amend`, `clean`, `cherry-pick`;
- `push`.

If `.git/index.lock` exists, the main agent is running git. Wait a few seconds and retry. Never delete the lock.

**Commit messages:** follow the repo's convention (look at `git log`). If there is none, use `test(<area>): <behavior covered>` or `fix(<area>): <what was wrong>`. Don't add attribution lines unless the repo's convention has them.

**When to commit a test:** only when it passes **and** the code it covers is already committed. Then a commit never contains tests for code that isn't in it, and a revert of the user's uncommitted work can't leave the branch red. A passing test whose code is still uncommitted goes under "Uncommitted" in the report. A failing test is never committed: an open escalation keeps its test uncommitted until the decision is made.

## Rounds

At launch, note `HEAD` and a snapshot of every dirty or untracked file with its content hash (`git hash-object <file>`). A file that is already modified stays ` M` in `git status` however much it changes after that, so compare hashes, not status. The user also edits files directly, with no UPDATE, and only the hash change shows it.

**Round 1 covers the changes listed in the brief.** If the brief lists none (the agent was started on entering quick-change), don't backfill older work on the branch. Take the snapshot and end the round with a short report saying you're ready.

Then work in rounds:

1. **Collect what's new** since the last round:
   - commits: `git log <last-head>..HEAD`;
   - files whose hash changed, and files that became dirty or untracked;
   - every `UPDATE:` message from the main agent.
2. **Run SKILL.md steps 1–6 on that delta only.** The live-check rules apply: reuse the running server from the brief, and recheck it is still up before using it.
3. **Keep your tests aligned with intent.** When the user deliberately changes behavior that one of your tests covers, the update says so. Update or remove that test. Don't "fix" the product back. If you can't tell whether a change was deliberate, escalate.
4. **Allow for edits in flight.** If a failure is in a file the latest update touched, wait briefly, re-read the file and re-run once before you treat it as a bug. The file may be mid-edit.
5. **Check git again.** If something changed while you worked, run another round.
6. **When nothing new is left,** end your turn with a TEST ROUND REPORT.

The main agent resumes you with the next `UPDATE:` and you keep your context, so don't wait or poll for changes. Ending the round is how you idle.

Messages you may receive:

- `UPDATE: <what> — <files> — <intent>`: input for the next round.
- `DECISION: <the user's answer> — <you apply it | I apply it>`: the answer to your last escalation. If the main agent applies the product change, wait for its UPDATE before you touch that test. Otherwise apply it under the ownership rules above, then continue.
- `FINAL`: run the new and related tests plus the full suite if feasible. Commit everything of yours that the commit rule allows, then send the final report. If an escalation is still unanswered, repeat it at the top of the final report.

**How your reports reach the main agent:** your final message when you end a turn is what the main agent receives. If your harness gives you a hand-back tool (for example `SubagentHandback`), put the report there.

## Escalation

Escalate when:

- a test shows something broken and the fix isn't small, local and obvious;
- the intended behavior is ambiguous (the code or the test could be the right one);
- the fix touches shared code, business rules, permissions or the API contract;
- the fix would collide with what the user is changing right now;
- you need something only the user can grant: installing a test framework or dependency, starting a server, creating data on a shared backend.

To escalate, finish and commit what's safe, then end your turn with this block first:

```
ESCALATION
What breaks: <one line, user-visible terms>
Where: <file:line> — <test name>
Why I didn't fix it: <one line>
Options:
1. <option>
2. <option>
```

Keep it short. The main agent relays it to the user and resumes you with `DECISION:`. Put any round report after the block.

## TEST ROUND REPORT

End every round with this, and leave out empty lines:

```
TEST ROUND REPORT
Covered: <test file> → <behaviors>
Not tested (on purpose): <what> — <why>
Fixed: <file> — <bug> (<committed sha | uncommitted>)
Commits: <sha> <message>
Uncommitted: <file> — <why it isn't committed>
Not run: <live check / full suite / level> — <why>
Pre-existing failures: <test> — <one line>
```

The final report after `FINAL` has the same shape, covers the whole session, and adds one line: `Branch state: <all green | what still fails>`.
