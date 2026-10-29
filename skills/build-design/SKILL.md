---
name: build-design
description: Generates 3 to 5 HTML mockup options (aesthetic, congruent and easy to compare) for a page, screen or window, after researching real visual references on Dribbble and similar sites and having subagents debate which design directions are strongest. Use it whenever the user wants to ideate, mock up, prototype or explore visual options for a UI ("help me create a dashboard", "make me a login page", "give me ideas for the settings screen", "generate 3 options in html", "ayudame a crear un dashboard", "generame 3 opciones en html"), even if they don't say "skill", "mockup" or mention Dribbble, and also when they share a dribbble.com, behance.net, mobbin or similar link as inspiration. Not for implementing features inside an existing framework or fixing one-off CSS. To redesign an existing element inside a product that already has a visual identity, use improve-ui instead.
---

# build-design

Turn a UI request ("a dashboard for X") into **N HTML mockups** (3 by default, up to N if the user asks) that:

- actually look good, not like a generic AI template;
- come from **real references** you looked at, not from memory;
- are **congruent**: each one is internally coherent (a single token system), and across options they show **the same content** in different visual directions, so the user compares style against style rather than data against data;
- ship with an `index.html` to compare them side by side.

The user uses these to ideate: they want to quickly see options with personality and be able to say "I like the header from 2 with the colors from 3". Optimize for that.

Reply to the user in the language they wrote in; the mockup copy follows the language of the request unless the user says otherwise.

## Workflow

Follow the phases in order. Tell the user in one line when each phase starts (they are watching).

### 1. Brief (no interrogation)

Extract from the request: screen type, product/domain, end user, data or sections it must show, platform (desktop web, mobile, app window), constraints (brand, colors, dark mode, future framework) and how many options (default 3).

If something is missing, **assume something reasonable and say so** instead of asking. Only ask if the answer changes everything (e.g. "a dashboard for what?" with no hint at all). If you're inside a repo with an existing UI, quickly look at its colors/fonts/components: maybe one option should respect that identity.

Pick the output folder: `mockups/<slug>/` in the current working directory unless the user says otherwise (if it exists, use `<slug>-2`, etc.; never overwrite earlier work).

### 2. Visual research

Read `references/inspiration-sources.md` for URLs and how to navigate each site.

- Start with Dribbble: the matching tag or search page (`https://dribbble.com/tags/<tag>`, `https://dribbble.com/search/<query>`). Links the user shared go first.
- Use a real browser: the built-in browser if your environment has one (in the Claude desktop app, the browser pane), otherwise Claude in Chrome; load its skill first. Use Chrome over the built-in browser only if the user asks for it, and never open pages in the user's own browser (`open <url>`). Style is visual: **take screenshots and look at them**; page text is not enough. With no browser, fall back to WebFetch/WebSearch and say the research was thinner.
- Look at 8 to 15 shots, opening the 5–8 strongest in detail. Add 1 or 2 more sources (Mobbin, Land-book, Godly, Behance…) if Dribbble is thin or too uniform.
- Don't sign in, create accounts or accept anything beyond closing modals (decline non-essential cookies).

For each reference, write down in `mockups/<slug>/research.md`: URL, title/author, and what concretely makes it good — palette (approximate hex), typography (kind: grotesque, editorial serif, mono…), layout and grid, density, card/border/shadow treatment, how it shows data, the distinctive detail. Be specific: "narrow icon sidebar + KPIs in a 2×3 bento with one giant serif number" is useful; "modern and clean" is not.

Close `research.md` with **4 to 6 candidate directions**: each with a short name, which references inspire it, and its core idea in 2–3 lines. Make them differ along real axes (light/dark, density, typographic personality, layout structure, use of color, illustration style), not five variations of the same purple SaaS.

References are inspiration: extract principles, don't copy a shot pixel for pixel or embed its images in the mockups.

### 3. Subagent debate

The point is that the choice of directions doesn't rest on your taste alone. Read `references/debate.md` and launch the three critics it describes **in parallel** (a single message): product/UX, art direction, and front-end/design system. Each one gets the brief, the full `research.md` and its role, and returns its ranking with arguments.

If you cannot spawn subagents in this environment, run the three critiques yourself as separate, explicitly written passes (one per role, each committing to a ranking before you read the next), and say so.

Then synthesize (you are the moderator, not another voter):

- Pick N final directions. What wins is what has strong arguments from more than one role; if a direction is brilliant for one role and very risky for another, keep it only if you can mitigate the risk.
- Ensure diversity: the N must clearly differ on at least two axes. If they end up too similar, swap the weakest for the best distinct alternative.
- If there's a strong disagreement you can't settle from the arguments, run a short second round: send the critics (via SendMessage, if they're still alive) the others' positions and ask for a brief response. No more than two rounds.

Write in `mockups/<slug>/decision.md` what was chosen, what was dropped and why (a few lines per direction), including each critic's key points.

### 4. Shared spec + per-option specs

Before writing HTML, lock down what makes the options comparable:

**Shared content spec** (in `decision.md`): the sections/components on the screen, concrete and realistic sample data (names, numbers, dates, states — no lorem ipsum, no "Item 1"), the copy for titles and buttons. Every option shows this. They may reorder or re-prioritize it if the direction calls for it, but they don't invent or drop content.

**Per-option visual spec**: an evocative name, tokens (background, surfaces, text, accent, states; in hex), Google Fonts (display + text, with weights), type scale, radii, shadows/borders, base spacing, grid, chart and icon style, illustration style if any, and **one signature detail** that makes it memorable (a huge number, a texture, a chart treatment, an asymmetric layout, a mascot…).

### 5. Build

Read `references/html-rules.md`. Build one file per option: `mockups/<slug>/option-1-<name>.html`, `option-2-…`, etc.

For 3+ options, parallelize: launch one subagent per option in a single message, each with the shared content spec, **only** its own visual spec, the output file path and the contents of `references/html-rules.md`. If the `frontend-design` skill is available, tell them to load it. If you build them yourself (or there are few), follow the same rules.

Copy `assets/compare.html` to `mockups/<slug>/index.html` and fill in the `TITLE` and `OPTIONS` list in its script with the files and a one-line description of each option.

### 6. Verification

Open each option in the built-in browser, as in phase 2 (local file or a `python3 -m http.server` in the folder; never `open` it in the user's browser), and screenshot it at desktop width (~1440px) and mobile (375px) — for a mobile-first screen, mobile is the primary check. Check:

- nothing is broken: fonts not loading, empty charts, horizontal overflow, unreadable text, console errors;
- no emojis anywhere and one consistent SVG icon set per option (run the scan in `references/icons.md`);
- it follows its own spec and the content spec (same content everywhere);
- it reads as its own direction, not the others with a different color.

Fix what's wrong before delivering. If something couldn't be verified (no browser, for instance), say so.

### 7. Delivery

Reply briefly:

- path to `index.html` (and open or show it if the environment allows);
- per option: name, one-line idea, which references inspired it;
- which one you recommend and why (what came out of the debate), without hiding doubts;
- invite mixing: "tell me what you like about each and I'll build a combined one".

If they then ask to iterate ("2 but darker", "the header from 1 with the table from 3"), edit the existing files or generate `option-N-v2` while keeping the content spec; don't redo the research unless the screen type changes.
