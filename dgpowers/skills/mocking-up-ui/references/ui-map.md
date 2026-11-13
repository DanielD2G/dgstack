# The UI map

The UI map is the contract between `brainstorming`, `mocking-up-ui` and
`writing-plans`. It lists every piece of front end a change touches,
before anyone plans or builds it, and records which mockup the user
chose for each piece.

Why it exists: agents build front ends badly when they improvise. They
invent spacing, reach for colors and components the product doesn't use,
drop states, and draw each step of a flow as if it belonged to a
different product. The fix is to settle every visual decision before
implementation: know exactly which components change, and give the
implementer a picture the user chose instead of a blank space to fill.

The map lives in the design doc, in a section called `## UI map`. When a
change touches nothing a user sees, the section says so in one line
(`No front-end changes.`), so a reader can tell it was checked and not
forgotten.

## Format

```markdown
## UI map

Flow: <how the user moves through the change, in one or two lines>

| # | Screen / component | Source | Change | Behavior and states | Mockup |
|---|---|---|---|---|---|
| 1 | <screen › component> | <file path, or "new: <planned path>"> | <what changes> | <what it does; the states it shows> | <status> |
```

Example:

```markdown
## UI map

Flow: Billing › "Add card" opens a modal wizard (card → address → confirm),
then returns to Billing with the new card selected.

| # | Screen / component | Source | Change | Behavior and states | Mockup |
|---|---|---|---|---|---|
| 1 | Billing › payment methods card | src/billing/PaymentMethods.tsx | new "Add card" button | opens the wizard; disabled with a tooltip at 5 cards | draw |
| 2 | Add card wizard › step 1: card | new: src/billing/AddCardWizard.tsx | new screen | inline validation errors; loading while the card is verified | draw |
| 3 | Add card wizard › step 2: address | new: src/billing/AddCardWizard.tsx | new screen | "same as account address" checkbox prefills and locks the fields | draw |
| 4 | Add card wizard › step 3: confirm | new: src/billing/AddCardWizard.tsx | new screen | error state if the card is declined | draw |
| 5 | Invoice row | src/billing/InvoiceRow.tsx | label "Pending" → "Due" | none | skip: copy only |
```

Columns:

- **Screen / component:** where it lives, from the outside in
  (`Checkout › shipping step › address form`). One row per piece that
  gets its own mockup or its own skip decision.
- **Source:** the file that renders it today, found in the code, not
  guessed. For a new piece, `new:` and the path you expect it to have.
- **Change:** what is different: a new field, a new screen, a moved
  control, a new state.
- **Behavior and states:** what it does when used and every state the
  user can see (empty, filled, loading, error, disabled, success, with
  and without optional data). The mockup has to show each one.
- **Mockup:** one of
  - `draw`: still to be drawn;
  - the path of the chosen mockup file, once the user picked it;
  - `skip: <reason>`: nothing visual is being decided (see below);
  - `skipped by user`: the user chose not to draw it.

## What gets drawn

Draw every piece where the implementer would otherwise have to make a
visual decision:

- a new screen, page, step, modal, sheet, drawer, popover or toast;
- a new field, control, column, filter or button on an existing
  component (where it goes and how it groups is the decision);
- a layout change: something moves, regroups, appears or disappears;
- a state the user will see that the product has no existing pattern
  for (a first empty state, a new kind of error, a locked mode).

Skip, with the reason in the Mockup column, when nothing visual is
being decided:

- copy-only changes (a label, a message, a translation);
- behavior with no visual change (validation logic, sorting, a request
  that now goes elsewhere);
- reusing an existing component exactly as it already renders somewhere
  else: name it, `skip: same as <component> in <file>`.

When unsure, draw it. A mockup costs minutes; an improvised screen costs
a rework, and the user only finds out once it's built.

## Behavior shapes what gets drawn

Think about how the piece is used, not just what it looks like at rest:

- **Multi-step flow** (wizard, onboarding, checkout, any stepper): every
  step is its own row and gets its own mockup, plus how the user moves
  between steps (step indicator, back and next, what's saved) and the
  end state (success, confirmation, where they land). Explore options
  on the step that sets the look, usually the first or the densest;
  once the user picks, draw the remaining steps in that direction.
- **Modal, sheet, drawer, popover:** draw the trigger in its context and
  the open overlay over that context.
- **New field on an existing component:** draw the whole component with
  the field in place, not the field alone, in empty, filled and error
  states when it validates.
- **Conditional UI** (shown only for some users or data): draw it with
  and without the condition.
- **Lists and tables:** draw them with realistic data, including a long
  value and the empty case when it can happen.
- **Responsive:** draw the product's primary viewport. Add the other one
  only when the layout changes materially, not just reflows.
- **A minor change** (one label, a column the table already knows how to
  render): skip it, with the reason.

## Inferring every screen

A screen nobody listed is a screen the implementer will invent. The map
is only as good as its list of screens, so build it by walking the flow,
not by reading the request once.

Walk it as the person using it, from the entry point to where they end
up, and at every point ask what they see:

- **Getting in:** where the entry point lives, and what it looks like
  when it can't be used (disabled, limit reached, no permission, nothing
  to act on yet).
- **Each step:** what's on screen, what they can do, what's required.
- **While waiting:** loading, verifying, saving.
- **When it goes wrong:** field errors, a rejected request, a failed
  save, no connection, a timeout.
- **Leaving early:** back, cancel, close with data typed, refresh.
- **Nothing there:** empty lists, a filter with no results, a first-time
  user.
- **Too much there:** long names, many items, the maximum.
- **The end:** success, confirmation, where they land, what changed on
  the page they came from (a new row, a toast, an updated counter).
- **Elsewhere:** emails, notifications or other screens that show the
  result; a phone layout that changes, not just reflows.

Everything you find is one of:

- **stated:** the request, the design doc or the map already says it.
  It goes in the map.
- **implied:** the flow needs it or the doc mentions it in passing, but
  nobody asked for a screen. Don't decide alone: ask your human partner
  whether they want a screen for it, all the doubts in one message, each
  with where it comes from. A yes becomes a row; a no is written down so
  the plan knows it was considered.

When in doubt whether something is stated or implied, treat it as
implied and ask. A question costs a line; a screen the user didn't know
about shows up only when it's already built.

## Skipping

The user can skip the drawing for any row, or for all of them ("sin
maquetas", "skip the mockups", "dale directo"). Mark those rows
`skipped by user` and say in one line what that means: for those pieces,
the implementer reuses existing components and the closest existing
pattern, and invents nothing new. Don't argue past that line.

Skipping removes the drawing, never the map. The list of components a
change touches is always written down, because it is what lets the plan
say exactly which UI files each task may touch.

## Coverage check

Run this before `writing-plans` starts, and again in `writing-plans`:

1. The flow was walked (see Inferring every screen) and every implied
   screen was either added as a row or explicitly declined.
2. No row is still `draw`.
3. Every row is either a chosen mockup path, `skip: <reason>`, or
   `skipped by user`.
4. Every step of every multi-step flow has its own chosen mockup, and so
   does the flow's end state.
5. Every state in "Behavior and states" is visible in the chosen mockup
   (on the page or through its "Preview state" switcher).
6. Every chosen path exists on disk.

A gap goes back to `mocking-up-ui` for the missing piece, or becomes an
explicit skip the user agreed to. Never paper over it in the plan.
