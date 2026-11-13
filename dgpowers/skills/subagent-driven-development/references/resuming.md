# Resuming From an Existing Ledger

Part of subagent-driven-development. This plan's workspace
already has a ledger at `<workspace>/progress.md`.

If the ledger's first line names your plan file, tasks with a `Task <N>:
complete` line are DONE — do not re-dispatch them; resume at the first
task without one. A task whose last line is a fix round is mid-loop:
resume the loop at the next round. A ledger whose first line names a
different plan file — or a stray ledger at the old flat path
`.dgpowers/sdd/progress.md` — is another plan's progress: leave it in
place and start your own, fresh.

With parallel tasks, more than one task can be mid-flight. A task with a
`Task <N>: started (worktree …)` line and no `complete` line was running
in its own worktree: run `bash scripts/task-worktree list PLAN_FILE`. If
its worktree is there, look at its branch (`git log <base>..<branch>`)
and its report file to see how far it got, then resume its loop at that
point: review if it has commits and a report, merge if its review was
clean, otherwise re-dispatch the implementer in the same worktree. A
worktree with no ledger line is debris from an interrupted start: remove
it and dispatch the task again. Then recompute the ready set from the
`complete` lines.
