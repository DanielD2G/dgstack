# Researching a piece

Research is for pieces that are new or complex: a new screen or modal,
the step that sets a flow's look, or a component or interaction pattern
the product doesn't have yet. A field that follows an existing pattern,
a hint text or a label doesn't get researched.

The goal is narrow: find how good products solve **this kind of
component**, so the options you draw are grounded in patterns that work
instead of in your first idea. You are mining structure and interaction,
not style: the product's identity already decides colors, fonts and
shapes.

## 1. Know what you're looking for

Before you search, write one line per piece: what the person is trying
to do with it, and what makes it hard ("add a card without leaving the
page, with a verification step that can fail", "narrow a list of
invoices by status, where some filters can return nothing").

Then the search terms: the component's common names ("add payment
method", "card form", "stepper modal", "filter chips", "segmented
control", "status filter table"), plus the product's domain.

## 2. Look at real references

Use the built-in browser when the environment has one (in the Claude
desktop app, the browser pane: `mcp__Claude_Browser__*`); Claude in
Chrome only if the user asks for it or there is no built-in browser.
Never open the user's own browser. Structure is visual: take screenshots
and look at them; page text is not enough.

Sources, in order of usefulness for this job (URLs and how to navigate
each are in `inspiration-sources.md`):

1. **Mobbin**: real production screens, the best source for how shipped
   products handle a flow. If it asks for a login, skip it.
2. **Dribbble and Behance**: search the component name. Plenty of pretty
   but unusable shots: keep the idea, filter what wouldn't survive real
   data.
3. **The product's own neighbors**: well-known products in the same
   domain (a store, a bank, a booking site) often solve the same
   component; look at their public pages when they're reachable without
   signing in.

Look at 8 to 15 results and open the 4 to 8 strongest. Don't sign in,
create accounts or accept anything beyond closing modals (decline
non-essential cookies). With no browser, use WebSearch and say the
research was thinner.

## 3. Write `<piece-slug>/research.md`

```markdown
# Research: <piece>

What the person is doing: <one line>. What makes it hard: <one line>.

## References
1. <URL> — <title / product>. Structure: <how it's organized, what comes
   first>. Interaction: <stepper, inline validation, chips, sheet…>.
   States: <how it shows errors, loading, empty, success>. Worth taking:
   <the one thing>.
...

## What the best ones have in common
<3 to 5 lines: the patterns that keep showing up in the good ones>

## Traps
<what looked good but fails with real data, long text, errors or small
screens>

## Candidate directions for this product
1. <name> — <structure in two lines>; from references <n, m>; fits
   because <why, given the product's patterns and components>.
2. ...
```

Two or three candidate directions, different in structure. They become
the option specs in the next step. If the research shows one pattern is
clearly the standard and the alternatives are worse, say so: two good
options beat three where one is filler.
