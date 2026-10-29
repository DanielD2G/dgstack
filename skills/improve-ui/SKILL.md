---
name: improve-ui
description: Redesigns an existing piece of UI (a modal, form, card, header, section, page) inside a product that already has a visual identity, producing 3 HTML options that stay faithful to that identity while exploring better structures, informed by Dribbble/Behance research and a subagent debate. It first extracts the identity from the codebase (tokens, fonts, components) and, when possible, from screenshots of the running app. Use it whenever the user wants to improve, rework, restructure or renew an existing element of their product ("quiero mejorar este modal", "renovemos el header", "dame una mejor estructura para este formulario", "redesign this card in our style", "this settings page feels cluttered"), especially when they select or screenshot an element, point to a component file, or work inside a repo with an existing UI, even if they don't mention brand, identity or Dribbble. For exploring brand-new looks with no identity to respect, use build-design instead.
---

# improve-ui

Take one existing element of a product and propose **N better versions of it** (3 by default) that:

- **look like they already belong to the product.** This is the hard constraint: same tokens, fonts, icon set, components, radii, shadows and copy tone. A user should not be able to tell which option was "made by someone else";
- **explore structure, not style.** The options differ in how the element is organized: hierarchy, grouping, flow, interaction, density. They don't differ in palette or typography. Three recolors of the same layout are a failed run;
- come from **real references** (Dribbble, Behance, Mobbin…) studied for their structure and interaction patterns;
- sit next to the **current version** so the user compares before/after on equal terms.

Reply in the language the user wrote in. The mockup copy uses the product's own language and tone.

## Workflow

Follow the phases in order and tell the user in one line when each one starts.

### 1. Scope the target

Work out what element to redesign and why:

- **What:** an element the user selected (the selected-element payload includes its HTML, path and computed styles: use them), a screenshot, a component file, a URL/route, or a description. Find its source in the repo (search by visible text, class names, aria labels or the component name) and read it, including the components it uses.
- **Why:** what bothers them ("cluttered", "doesn't scale", "needs a better structure", "looks dated"). If they didn't say, infer it from the element itself and state your read in one line.
- **Constraints:** data and actions the element must keep, platform (mobile/desktop), states (empty, loading, error, filled, disabled), what surrounds it.

Ask only if you can't find the element at all. Output folder: `mockups/<slug>/` in the repo root unless the user says otherwise (if it exists, use `<slug>-2`; never overwrite earlier work).

### 2. Extract the visual identity

This phase decides whether the run succeeds. Read `references/identity-extraction.md` and follow it. In short:

1. **Code:** find the token sources (CSS variables, Tailwind config/theme, theme objects, design-token files), fonts, icon set, and the existing components (Button, Input, Card, Dialog, Tabs, Badge…) and their variants.
2. **Live app:** check whether a dev server is already running. If it is, open the app in the browser, screenshot the target element and 2–3 other screens to absorb the overall feel, and read computed styles where tokens are ambiguous. If it isn't running and you need to see it, **ask the user for permission before starting it**, with the exact command you'd run. If they decline, continue from code and whatever screenshots they gave you, and say so.
3. Write `mockups/<slug>/identity.md` (exact values, components, patterns, do/don't) and `mockups/<slug>/tokens.json` (machine-readable palette and fonts for the checker).

Rule for the rest of the run: **no new colors, fonts, icon sets, radii or shadows, and no emojis** (icons are inline SVG from the product's set; `references/icons.md` covers sourcing and drawing missing ones). If a direction truly needs something the identity lacks (e.g. a warning color that doesn't exist), derive it from existing tokens, flag it as a proposed new token in `decision.md`, and keep it to the minimum.

If the identity in the code is messy (hardcoded values, competing palettes), go by what is actually rendered most consistently, and tell the user what inconsistencies you found. That's useful information for them, not a reason to stop.

### 3. Research structural references

Read `references/inspiration-sources.md`. Search Dribbble, Behance and Mobbin for **this kind of element** (e.g. "flight search form", "booking widget", "settings modal", "checkout summary"), plus adjacent patterns that solve the same problem differently.

Use a real browser and look at screenshots. Here you're mining **structure and interaction**, so ignore their palettes and fonts. For each reference, write in `mockups/<slug>/research.md`: URL, title/author, how the element is organized (hierarchy, grouping, order, what's primary), the interaction pattern (inline editing, stepper, sheet, chips, progressive disclosure…), how it handles states and edge cases, and what it would solve in the user's current element.

Close with **4 to 6 candidate structural directions**: short name, which references inspire it, what changes versus the current element and which problem it solves. They must differ in structure from each other and from the current version.

### 4. Subagent debate

Read `references/debate.md` and launch its three critics **in parallel** (one message): product/UX, brand guardian, and front-end engineer. Give each one the brief, the paths to `identity.md`, `research.md` and the current element's source or screenshot, and the response format.

If you can't spawn subagents, run the three critiques yourself as separate written passes, each committing to a ranking before you read the next, and say so.

Then moderate:

- Pick N directions with strong arguments from more than one role. A direction the brand guardian says can't be done in-brand without new tokens is out, unless the gain is big and you flag it.
- Ensure structural diversity: each pair of options must differ in at least one of: overall layout, interaction pattern, information grouping/order. If two converge, replace the weaker.
- If a critic proposes a new direction that is clearly better than a picked one, you may swap it in. Otherwise record it under "for later" in `decision.md`.
- At most one short second round (SendMessage to the critics) for a strong disagreement.

Write `mockups/<slug>/decision.md`: chosen and dropped directions with reasons, critics' key points, proposed new tokens (if any), ideas for later.

### 5. Specs

**Shared content spec** (in `decision.md`): the real data, actions and copy of the element, taken from the current version (realistic sample values if it's dynamic), plus the states worth showing. Every option covers all of it. Structure is free; content is not: don't drop a capability without saying so in the option's notes.

**Per-option structural spec:** name, the structure (sketch the layout in a few lines of ASCII or a bullet hierarchy), the interaction pattern, which existing components it uses, how it handles the important states, and the one structural idea that makes it better than the current version.

### 6. Build

Read `references/html-rules.md`. Build:

- `mockups/<slug>/option-0-current.html`: a faithful HTML rebuild of the current element in its context, the baseline for comparison. Check it against a screenshot of the real one.
- `mockups/<slug>/option-1-<name>.html` … one per direction.

Each file renders the element **in context** (the surrounding area approximated: the hero above it, the page background, the nav), uses the identity's tokens under **the same variable names the project uses**, and the same fonts and icons. That way the winner is easy to port.

For 3+ options, launch one builder subagent per option in parallel, each with `identity.md`, `tokens.json`, the shared content spec, only its own structural spec, `option-0-current.html` as the visual reference, `references/html-rules.md`, and its output path.

Copy `assets/compare.html` to `mockups/<slug>/index.html`. Fill `TITLE` and `OPTIONS`, with option 0 labeled "Current" first, and set `<html lang>` to the user's language.

### 7. Verification

1. **Brand check (script):** run `python3 <skill-dir>/scripts/check_brand.py mockups/<slug>/tokens.json mockups/<slug>/option-[1-9]*.html`. It lists colors and fonts that aren't in the identity, and any emoji (see `references/icons.md`). Fix every hit, except colors that are proposed tokens flagged in `decision.md`. Option 0 is left out on purpose: it mirrors the current product.
2. **Visual check:** open each option over HTTP (`python3 -m http.server` in the folder), at the product's primary viewport (mobile 375px for mobile apps, ~1440px for desktop apps). Disable or wait out animations before screenshots, because paused animations from a background pane look like bugs. Compare each one side by side with option 0: does it look like the same product? Is the structural change visible at a glance?
3. **Basics:** no console errors, no horizontal overflow, fonts load, states render.

Fix before delivering. Say what you couldn't verify.

### 8. Delivery

Reply briefly:

- path to `index.html` (open it if possible);
- per option: name, what changes structurally and which problem it solves, inspiring references;
- your recommendation and why (from the debate), plus any proposed new tokens;
- invite mixing ("the grouping from 2 with the CTA from 3");
- offer to implement the chosen option in the real codebase with the project's own components. Don't touch app code until they say so.

Iterations ("2 but more compact", "combine 1 and 3") edit the existing mockups or add `option-N-v2`, keeping the identity and the content spec.
