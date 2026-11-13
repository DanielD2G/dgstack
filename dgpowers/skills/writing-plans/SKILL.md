---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

Answer the user in the language they write to you in, not the language this skill is written in.

## Overview

Write implementation plans for an engineer who has not seen this codebase or this spec. Assume they write idiomatic code in the project's language once they know the exact interface and the exact test, and that they will make a reasonable choice wherever the plan leaves one open. What they cannot know is what you decided: which files, which names and signatures, which values from the spec, which tests prove each task. Document those. Give them the whole plan as bite-sized tasks arranged as a dependency graph, so tasks that don't need each other can be built at the same time. DRY. YAGNI. TDD. Frequent commits.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** If working in an isolated worktree, it is created at execution time by the skill that runs the plan (`subagent-driven-development` or `executing-plans`).

**Save plans to:** `docs/dgpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## Front End

Implementers build UI badly when they improvise it, so a plan never
leaves a visual decision open: every UI task points at the mockup the
user chose, and touches only the components the spec's UI map lists.
Read `../mocking-up-ui/references/ui-map.md` for the map's format and
its coverage check.

Before writing any task:

1. **Find the UI map** (`## UI map` in the spec). If the spec has none
   and the work touches anything a user sees, stop: tell your human
   partner, and build the map with them (brainstorming's Map the Front
   End step) before planning. `No front-end changes.` counts as a map.
2. **Run the coverage check** from the reference. If any row is still
   `draw`, a flow step has no mockup, a listed state isn't drawn or a
   chosen file is missing, stop and go back to mocking-up-ui for that
   piece, unless your human partner explicitly skips it (then mark the
   row `skipped by user`).
3. **Hold the map as the boundary.** If, while mapping files, you find a
   UI component the change must touch that the map doesn't list, stop
   and say so. It gets added to the map, drawn if it needs a mockup, and
   approved before you plan it. Never slip it into a task.

Then, in the tasks:

- Every task that changes UI gets a **UI:** block (see Task Structure):
  the map rows it implements, the chosen mockup file for each, and the
  states the task must reproduce. The implementer opens the file and
  builds to it.
- A `skip: same as <component> in <file>` row: the task says to reuse
  that component as it is.
- A `skipped by user` row: the task says to reuse existing components
  only, names the closest existing pattern to follow, and allows no new
  visual patterns.
- A UI task's **Files** list holds only components from the map, plus
  any new component a chosen mockup calls for (its top comment says so).

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Task Right-Sizing

A task is the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate. When drawing task boundaries: fold setup,
configuration, scaffolding, and documentation steps into the task whose
deliverable needs them; split only where a reviewer could meaningfully
reject one task while approving its neighbor. Each task ends with an
independently testable deliverable.

## Task Graph

A plan is a graph, not a list. Each task says which tasks it depends on,
and tasks with no path between them can be built at the same time by
different implementers. Think in the graph from the start: it decides
where task boundaries go, not just the order they run in.

**An edge exists when** task B needs something task A leaves behind:

- B consumes an interface, type, schema, migration or config A produces;
- B touches a file A creates or modifies (tests, barrel/index files,
  route registries, translation files, lockfiles and generated files
  count);
- B's tests need A's behavior to exist;
- both need the same exclusive resource (the next migration number, a
  port, a fixture they both rewrite).

**The rule that makes parallel work safe:** two tasks with no dependency
path between them touch disjoint files and neither consumes what the
other produces. If two tasks share a file, one depends on the other.
There are no exceptions to this; an implementer in its own worktree
cannot see what its neighbor is writing.

**Design for width, honestly.** After a first pass, look at each edge and
ask whether it is real or an accident of how you cut the tasks:

- When several tasks would all touch one shared file (a types file, a
  router, a schema), pull that shared piece into an earlier task of its
  own: define the interfaces, register the routes, add the columns. The
  tasks after it then fan out in parallel, each in its own files.
- When two tasks only meet at an interface, put the exact signatures in
  the earlier task's Produces block, so both sides can be written against
  it without waiting for each other's bodies.
- Don't invent parallelism. A chain is the right shape for work that is
  a chain, and a false "independent" costs a merge conflict or two
  implementations of the same thing. When unsure whether two tasks are
  independent, add the edge.

Number the tasks in an order that respects the edges (a task's number is
higher than every task it depends on), so the plan still reads top to
bottom and can be executed one task at a time.

Then group them into **waves** for the reader: wave 1 is every task with
no dependencies; each later wave is every task whose dependencies all
sit in earlier waves. The waves go in the plan header as a table (see
Plan Document Header). Each task's own `Depends on:` line is the source
of truth; the table is the picture.

## Step Granularity

**Each step is one action with a checkable result:**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Spec:** [path to the spec/design doc this plan implements — the plan
argues from the spec, so the spec travels with it; executors read both]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

## Task Graph

[One row per wave. Tasks in the same wave have no dependency path
between them and touch disjoint files, so they can be implemented at
the same time. A wave with one task is fine.]

| Wave | Tasks | Needs |
|------|-------|-------|
| 1 | Task 1 | nothing |
| 2 | Task 2, Task 3 | Task 1 |
| 3 | Task 4 | Task 2, Task 3 |

## Review Focus

[The five input classes or failure modes the spec implies but no task's
tests exercise that are most likely to bite a person using this software
— one line each, naming the input or condition and the behavior a
reasonable person would expect, most likely first. The spec is a vision
document: it says what the software must do, not everything it will
meet, and its silence on an input is not permission for that input to
break the program. Write the list here, once, with the spec in front of
you. Then, for each line, add the test that pins it to the task that
owns the code, in that task's own step style.]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Depends on:** [Task numbers this task needs finished first, or "none".
Every task whose output it consumes or whose files it touches.]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

**UI:** (only for tasks that change what a user sees)
- Implements: UI map rows [#] — [screen › component]
- Mockup: `docs/dgpowers/mockups/<run>/<piece>/<chosen-file>.html`
- States to reproduce: [empty, filled, error, ... as the map lists them]
- Build to the mockup: same layout, grouping, copy and states, using the
  project's existing components and tokens. Nothing on screen that the
  mockup doesn't show.

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Implement `function(input: InputType) -> ResultType` in `exact/path/to/file.py`**

One line on the approach when the signature and the test leave a choice
(which library call, which data structure); a code block only for an
algorithm they do not determine.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## What a Step Contains

A step is done when the implementer can write exactly one reasonable thing
from it. That is the whole requirement: unambiguous, not complete. Each kind
of step carries what makes it unambiguous and nothing more:

- **A test step:** the test's name and its assertions, as code, with the
  spec's exact values in them.
- **A code step:** the exact signature (name, parameters, return type), the
  file it lives in, and the specific values the spec pins. The implementer
  writes the body. A body appears only for an algorithm the signature and
  tests do not determine, or for exact copy the spec fixes.
- **A verification step:** the command to run and the output that means it
  passed.
- **A reference to another task:** that task's Interfaces block says what
  to use; the plan does not repeat that task's code.

A plan is the set of decisions the implementer cannot make alone. A plan
longer than the code it describes has written the code instead. Lines that
decide nothing ("TBD", "handle edge cases", "add appropriate validation",
"write tests for the above", a type or function no task defines) are the
opposite failure, and the self-review catches both.

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Step scan:** Every step must let the implementer write exactly one reasonable thing, and no step may carry more than that: a line that decides nothing is a gap, a function body the signature and tests already determine is a transcript. Fix both.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

**4. Task graph:** For every pair of tasks with no dependency path between them, compare their Files lists: any shared file means a missing edge. Check each task's Consumes against its `Depends on:` (it may only consume from tasks it depends on, directly or through them), that no task depends on a higher-numbered one, and that the header's wave table matches the `Depends on:` lines. Then look once more for width: is there a shared file or interface you could pull into an earlier task so that the tasks behind it stop depending on each other?

**5. Review Focus:** For each input class or failure mode the spec implies, is there a task whose tests exercise it? The five uncovered ones most likely to bite a person go in the Review Focus section, and each line there gets its test added to the owning task. An empty section means you checked and found none, not that you skipped the check.

**6. UI coverage:** Every row of the UI map maps to a task (a skipped drawing is still a change to build); every flow step has its own task or a task that names it; every UI task has a UI block with an existing mockup path or the skip rule; no task touches a UI component the map doesn't list.

**7. Proportion:** Compare the plan's length to the spec's. A plan several times longer than the spec it implements is a transcript of the program, not a plan. If code blocks are most of the document, replace bodies with signatures, test names and assertions, and check that each step is still unambiguous.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving and self-reviewing the plan, link it for your human partner
to read. If they have already explicitly supplied an execution method, ask
them to review the plan and confirm it captures what they want; wait for that
review before implementation, then use the preserved method. Otherwise, ask
them to review the plan and choose an execution method before implementation.

**When no execution method has already been supplied:**

**"Plan complete and saved to `docs/dgpowers/plans/<filename>.md`. Please review the plan. Which execution approach would you prefer?**

- **Subagent-driven** - A fresh subagent implements each task and a fresh reviewer checks it, then a whole-branch review at the end. Tasks in the same wave of the plan's graph run at the same time, each in its own worktree. Most thorough, and the fastest on a wide graph; costs a fresh context per task and per review.
- **Native** - I implement every task myself in this session, one at a time in task order, then one fresh reviewer on the most capable model checks the whole branch. Cheapest and fastest; no independent review until the end. Runs well with a mid-tier session model, since the plan carries the design.

**For this plan I recommend <one of the two>, because <one sentence from the plan: how wide its graph is (how many tasks can run at once), how much the tasks depend on each other's interfaces, what a shipped mistake would cost>. Does the plan capture what you want, and which approach should we use?"**

**When an execution method has already been supplied:**

**"Plan complete and saved to `docs/dgpowers/plans/<filename>.md`. Please review the plan. Does it capture what you want?"**

**If Subagent-driven chosen:**
- **REQUIRED SUB-SKILL:** Use subagent-driven-development

**If Native chosen:**
- **REQUIRED SUB-SKILL:** Use executing-plans
