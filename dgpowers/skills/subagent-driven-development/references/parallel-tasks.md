# Running Tasks in Parallel

Part of subagent-driven-development. Read it when the plan has a Task
Graph and more than one task is ready at the same time.

The plan's graph says which tasks need each other. Tasks with no
dependency path between them touch disjoint files, so different
implementers can build them at once. Each one works in its own git
worktree, gets its own review, and is merged back when its review is
clean. You are the scheduler: you never implement, you keep the graph
moving.

## The ready set

A task is **ready** when every task in its `Depends on:` line is merged
into the plan's branch. At any moment:

- dispatch every ready task that isn't already running, up to **four
  implementers at once** (more than that and you lose track of the
  reports, and the machine runs four test suites at a time);
- when a task merges, recompute the ready set: tasks behind it may now
  be free, even while others from the same wave are still in review.

The wave table in the plan header is the picture of this; each task's
`Depends on:` line is the truth. If they disagree, go by the lines and
ledger the mismatch.

**One ready task and nothing else running:** run it the ordinary way, in
the plan's own working tree, with no worktree and no merge. Worktrees
are for when two tasks are in flight together.

**No task graph in the plan** (an older plan with no `Depends on:`
lines): run the tasks one at a time in order. Don't infer a graph the
planner didn't write.

## One worktree per running task

For each task you are about to run alongside another, from the plan's
working tree:

```
bash scripts/task-worktree add PLAN_FILE N
```

It prints `path=`, `branch=` and `base=`. Record all three in the ledger
(`Task <N>: started (worktree <path>, branch <branch>, base <base7>)`).
`base` is the task's BASE for its review range.

A fresh worktree is a bare checkout: no installed dependencies, no
untracked config such as `.env`. Before dispatching, run the project's
setup in it (the install command, copying the untracked config the tests
need), or tell the implementer the exact commands as the first step of
its dispatch. If setup is so heavy that it costs more than the parallel
run saves, run those tasks one at a time and ledger that ruling.

Dispatch all the implementers of the ready set **in one message**, so
they start together. Each dispatch is the ordinary one (brief path,
report path, interfaces, constraints) with two differences:

- "Work from:" is the task's worktree path. The implementer commits
  there, on the task's branch, and never touches another directory.
- The brief and report files stay in the plan's workspace; pass their
  absolute paths.

## Review, fix, merge

Each task runs its own loop, independently of its neighbors:

1. **Review package**, from the plan's working tree:
   `bash scripts/review-package PLAN_FILE <base> <branch>`. Worktrees
   share one repository, so the task's branch is visible from here.
2. **Task review** and, if needed, the **fix loop**, exactly as for a
   sequential task. Fix rounds resume the implementer in its worktree.
   One task's fix loop never holds up another task's review.
3. **Merge**, as soon as the review is clean (or its findings are parked
   at the cap): `bash scripts/task-worktree merge PLAN_FILE N`. Merge one
   task at a time, never two at once.
4. **Run the full test suite** on the plan's branch after the merge,
   before dispatching anything that depends on it. Each task's tests ran
   against an older base; this is where two tasks that pass alone and
   fail together show up. Two merges landing back to back can share one
   run.
5. **Clean up:** `bash scripts/task-worktree remove PLAN_FILE N`, then
   append `Task <N>: complete (merged <merge7>, commits <base7>..<head7>,
   review clean)` to the ledger and mark the todo.

Reviewers can run in parallel too: they only read.

## When it goes wrong

- **Merge conflict** (`task-worktree merge` exits 3, merge aborted): the
  graph said these tasks were independent and they weren't. Don't
  resolve it yourself. Ledger `Ruling: Task <N> conflicts with Task <M>
  on <files> — missing edge in the plan`, then resume the task's
  implementer in its worktree with: merge the plan's branch into yours,
  resolve the conflict keeping both tasks' behavior, re-run your tests.
  Its resolution gets a scoped re-review, then merge again.
- **Suite red after a merge:** the merged tasks interact. Use
  systematic-debugging to find which pair, then dispatch the fix to the
  implementer of the later-merged task, on the plan's branch, with a
  failing test first. It gets a scoped re-review like any fix.
- **A task is BLOCKED or NEEDS_CONTEXT:** handle it as usual
  (references/handling-reports.md). The other running tasks carry on;
  only tasks that depend on the blocked one wait.
- **A task discovers it needs a file another running task owns:** it
  stops and reports. Rule on it: usually the task waits for the other to
  merge, then you remove its worktree, cut a new one from the updated
  branch and re-dispatch. Ledger the missing edge.
- **Your harness has no way to run several subagents at once, or the
  repository can't make worktrees:** run the tasks one at a time in task
  order. The graph still tells you the order is safe.

## Before the final review

Every task is merged, `bash scripts/task-worktree list PLAN_FILE` prints
nothing, and the suite is green on the plan's branch. The final
whole-branch review then runs over the merged branch as usual.
