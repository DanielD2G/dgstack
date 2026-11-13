---
name: mocking-up-ui
description: Draws HTML mockups of every piece of front end a change will touch, before it is planned or built, so nobody improvises UI during implementation. Infers every screen the flow needs (asking when unsure), researches real references for the pieces that are new or complex, then draws 2 or 3 options per piece in the product's visual identity for the user to choose from. Covers new fields inside the existing component, modified components, new modals and screens, and every step of a multi-step flow. Use it when brainstorming hands over a design doc with a UI map, and whenever the user wants to see how a new field, control, modal, step or screen would look before building it ("dibujame cómo quedaría el campo nuevo", "maquetá el wizard antes de hacerlo", "mostrame opciones para meter este filtro en la tabla", "mock up the new settings step", "how would this field look in the checkout form?"). Not for redesigning an element for its own sake (improve-ui) or exploring brand-new looks (build-design).
---

# Mocking Up UI

Answer the user in the language they write to you in, not the language this skill is written in. The mockup copy uses the product's own language and tone.

Agents build front ends badly when they improvise: they invent spacing,
reach for colors and components the product doesn't use, drop states,
forget screens the flow needs, and draw each step of a flow as if it
came from a different product. This skill moves every visual decision
to before the plan:

1. **Work out every screen** the change needs, and ask whenever you're
   not sure one is wanted.
2. **Research how to do the pieces that are new or complex**, on real
   references.
3. **Draw the options** in the product's identity, and let the user pick.

The implementer then copies a picture instead of inventing one.

What you deliver: for every row of the UI map, a chosen HTML mockup
that covers the states that row lists, or an explicit skip.

Tell the user in one line when each phase starts.

## 1. Start from the UI map

Read `references/ui-map.md`: it defines the map, what gets drawn and
what gets skipped, how behavior shapes the drawing (a wizard means every
step), and the coverage check you finish with.

- **Coming from brainstorming:** the approved design doc has a
  `## UI map`. Read the whole doc, not just the map: the flow, the data
  and the copy are in there.
- **Called directly:** build the map yourself from the request and the
  code: every screen and component the change touches, with its source
  file and the states it shows.

Output folder: next to the design doc,
`docs/dgpowers/mockups/YYYY-MM-DD-<topic>/` with the same date and topic
as the spec; `mockups/<topic>/` when there is no spec. One subfolder per
piece (`<piece-slug>/`). Never overwrite earlier work: add `-2`.

## 2. Infer every screen, and ask when unsure

This is the step that matters most. A screen nobody listed is a screen
the implementer will invent, so find them all now. Follow "Inferring
every screen" in `references/ui-map.md`: walk the flow as the person
using it, from the entry point to where they end up, and write down
everything they would see on the way, including what happens on back,
cancel, error, empty, limit, success, and on a phone.

Sort what you found:

- **Already in the map or stated in the request or design doc:** keep.
- **Implied but not stated** (a confirmation dialog, a success screen,
  an empty state, an error page, a mobile layout that changes, a state
  the doc describes but the map doesn't list): don't decide alone. Ask.

Ask in one message, before drawing anything, as a short list your human
partner can answer line by line: what you found, where it comes from,
and the question, for example "Closing the wizard with data typed asks
for confirmation (the doc says so, the map doesn't list it). Do you want
a screen for it?" Add each one they say yes to as a row; record the noes
in `decision.md`. If they don't answer a line, draw it: an extra mockup
costs minutes, a missing one costs an improvised screen.

In the same message, show the final list of pieces and, for each one,
whether it gets research and options or a single drawing. They can
trim it, add to it, or skip the drawing before you spend anything.

How many options each piece gets:

| Piece | Research | Options |
|---|---|---|
| A new screen, modal, or the step that sets the look of a flow | yes | 3 structural options |
| A new component or interaction pattern the product doesn't have (a stepper, a filter bar, an uploader, a date picker) | yes | 2 or 3 |
| A new field or control that follows a pattern the product already has | no | 2 placements |
| The other steps of a flow, once its look is picked | no | 1, in the chosen direction |
| A small addition to an existing piece (a hint text, one more option in a list) | no | 1, or skip with a reason |

The user can ask for more or fewer.

## 3. Extract the identity, once per run

Read `references/identity-extraction.md` and follow it, lightly. You
need enough to draw pieces that look native, not a brand audit:

- **Code:** tokens, fonts, icon set, the components the pieces use or
  sit inside, and two or three sibling components on the same screens.
  Look for how the product already solves similar things (other forms,
  other wizards, other empty states).
- **Live app:** if a dev server is already running, open the relevant
  screens in the built-in browser and screenshot them. If none is
  running, don't start one without asking (see the reference); the code
  is usually enough for this skill.

Write `identity.md` and `tokens.json` in the run folder. They serve
every piece in the run.

From here on: no new colors, fonts, icon sets, radii or shadows, and no
emojis. Icons are inline SVG from the product's set; `references/icons.md`
covers sourcing missing ones. If a piece truly needs something the
identity lacks, derive it from existing tokens and record it as a
proposed token in `decision.md`.

**No identity yet** (a new product with no UI): then the options also
explore visual direction, and the research in the next step covers
look as well as structure. Mention that the full exploration exists as
the build-design skill if they want it.

## 4. Research the pieces that need it

For each piece marked for research, find out how good products solve
this kind of component before you invent options. Read
`references/research.md` and follow it: a focused look at 4 to 8 real
references (Mobbin, Dribbble, Behance and similar, in the built-in
browser), studied for structure and interaction, not for their colors.

Write `<piece-slug>/research.md`: each reference with its URL and what
it does well, what the best ones have in common, the traps to avoid,
and 2 or 3 candidate directions that fit this product. The options you
draw come from here.

No debate and no critic subagents: the research is what grounds the
options, and the user is the one who judges them.

## 5. Rebuild the baseline

For each existing component that changes, build
`<piece-slug>/option-0-current.html`: a faithful rebuild of how it looks
today, in its context. It is what the options are compared against, and
the frame they reuse. Check it against the code or a screenshot.

For a new screen or step, take the shell (nav, page layout, background)
from the closest existing screen, so the new piece is drawn inside the
real product.

## 6. Write the option specs

For each piece with options, write a short spec per option in
`<piece-slug>/specs.md`:

- a name, and the references it comes from (for researched pieces);
- the structure, sketched in a few lines of ASCII or a bullet hierarchy;
- the existing components it reuses, and any new one it needs;
- how it shows each state the UI map lists;
- the one idea that makes it worth choosing.

Options for one piece differ in structure or placement (where the field
sits, how things group, inline versus disclosed, one page versus steps),
not in color. Prefer the product's own patterns; an option that departs
from them says why.

**Copy the user gave is copy.** Labels, messages and option names that
the user or the design doc fixed go into every mockup word for word. If
you think different wording would work better, draw what they asked for
and raise yours as a question when you show the options. Don't swap it
in on your own.

Before building, reread each spec once against the research and the
identity: drop an option that needs new tokens or a whole new component
without a clear gain, and make sure every state in the map has a place.

## 7. Build

Read `references/html-rules.md`. One file per option:
`<piece-slug>/option-1-<name>.html`, and so on.

For three or more files, you may parallelize: one builder subagent per
file, in a single message, each with `identity.md`, `tokens.json`, its
own spec only, the baseline file, the contents of
`references/html-rules.md` and its output path. These are builders,
not reviewers: they write their file and report back, without opening
the browser or installing anything to test it. The visual check in the
next step is yours. If the `frontend-design` skill is available, tell
them to load it.

For each piece, copy `assets/compare.html` to `<piece-slug>/index.html`
and fill `TITLE` and `OPTIONS`, with option 0 labeled "Current" first
when there is one. Set `<html lang>` to the user's language.

## 8. Verify before showing

1. **Brand check:** run
   `find <run> \( -name 'option-[1-9]*.html' -o -name 'step-*.html' \) -exec python3 <skill-dir>/scripts/check_brand.py <run>/tokens.json {} +`.
   It lists colors and fonts outside the identity, and any emoji. Fix
   every hit, except proposed tokens recorded in `decision.md`. Option 0
   is left out on purpose: it mirrors the product as it is.
2. **Visual check:** serve the run folder (`python3 -m http.server`) and
   open each file in the built-in browser when the environment has one
   (in the Claude desktop app, the browser pane: `mcp__Claude_Browser__*`).
   Use Claude in Chrome only if the user asks for it or there is no
   built-in browser, and never open the user's own browser (`open`,
   `xdg-open`, `webbrowser.open`). Check at the product's primary
   viewport, with animations finished. Next to option 0: does it look
   like the same product? Is the difference between options visible at a
   glance? Does every listed state render?
3. **Basics:** no console errors, no horizontal overflow, fonts load.

Verification uses the browser and the script above. Don't install
packages (jsdom, test runners) to check a mockup.

Fix before showing. Say what you couldn't verify.

## 9. Let the user choose

Show one piece at a time, or the pieces of one flow together: the
`index.html` path (loaded in the browser pane when possible), each
option in one line with the references behind it, and your
recommendation with its reason. Add any copy you'd change, as a
question. Ask which one they want. They can mix ("the grouping from 2
with the button from 3"): build that as `option-N-v2.html` and show it.

For a multi-step flow, once the step that sets the look is chosen, draw
the remaining steps and the end state in that direction
(`<flow-slug>/step-1-<name>.html`, …), list them in order in that
folder's `index.html`, and show them together for approval.

Record each choice:

- in `decision.md`: the chosen file per piece, what was dropped and why,
  the screens your human partner said no to, proposed tokens;
- in the design doc's `## UI map`: replace `draw` with the chosen file's
  path, and add the rows for screens they said yes to in step 2. Commit
  the mockups folder together with the design doc, so the plan can point
  at files that exist.

The user can stop drawing at any point ("skip the rest", "sin
maquetas"). Mark the remaining rows `skipped by user`, say in one line
what that means (the implementer reuses existing components and invents
nothing new for those pieces), and move on.

## 10. Close

Run the coverage check from `references/ui-map.md`. Fix any gap, or get
the user to agree to an explicit skip for it.

- **Coming from brainstorming:** the next step is the plan. Invoke
  writing-plans.
- **Called directly:** offer to write the plan or implement the chosen
  mockups with the project's own components. Don't touch app code until
  they say so.
