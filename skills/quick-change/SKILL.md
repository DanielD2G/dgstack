---
name: quick-change
description: Quick-change mode for small, mostly front-end tweaks to an existing app (remove a button, reword a label, turn a panel into a modal, tidy a layout, shorten an alert message), with a scope guard that stops and warns the user when a request that sounds small would actually touch other systems (new data, endpoints, caching or prefetch, shared components, business rules). Use it whenever the user asks to enter quick-change mode or says things like "modo cambio rápido", "cambio rápido", "quick change", "modo rápido", and also when they send a screenshot or a page path with a small UI request ("quitemos ese botón", "pasá esto a un modal", "mejoremos esto", "cambiá este texto"), even if they don't name the mode. Not for building new features, new screens or mockups.
---

# quick-change

The user is iterating on an existing app, usually the front end, in short loops: a screenshot or a path plus "remove this", "make this a modal", "improve this", "this alert should say less". They want each change done fast, with a small diff, and they assume the scope is the screen they are looking at.

Your job has two halves, and the second one matters more:

1. Make small changes quickly and cleanly.
2. **Protect the user's assumption about scope.** When a request that sounds small would actually reach into other systems, stop before editing and tell them, so they decide. A silent "I also added an endpoint and a cache" is the failure this mode exists to prevent.

Talk to the user in their language (usually Spanish), briefly.

## The mode is sticky

Once the user enters quick-change mode, handle every following request in the conversation with this flow until they leave it ("salí del modo", "exit quick change", or they clearly switch to planning a feature). Confirm entry in one line and, in the same message, ask once whether to start the background test agent, e.g. "Modo cambio rápido activo. ¿Arranco el agente de tests en segundo plano para que vaya testeando lo que cambiemos?"

- **Yes:** follow `subagent-for-test` to launch it, then ask for the first change. From then on, send it an update after each change (step 6) and pass on anything it escalates. When the user leaves the mode, close it as `subagent-for-test` describes (send `FINAL`). A red alert that moves one request out of the mode is not leaving it.
- **No:** don't ask again in this conversation. When they leave the mode, mention in one line that `backtrack-for-test` can backfill tests for what changed.

If the user's first message already includes a change, ask about the agent in one line and go ahead with the change; don't hold it up waiting for the answer.

## Per request

### 1. Locate

Find the exact code behind what the user points at:

- A **page path** (`/products/123`, `/settings/billing`): map it to the route file through the project's router (file-based routes, route config, etc.).
- A **screenshot**: use the visible text (labels, headings, button copy) to grep for the component; confirm by checking the surrounding structure matches.
- If two places match and you can't tell which one they mean, ask with the candidates. Don't guess between screens.
- If the request itself reads two ways ("que el modal se cierre solo después de guardar": closes automatically on save, or can only be closed after saving?), ask which one in one line before the scope check.

### 2. Scope check (before any edit)

Read the code you would touch, then answer these questions. They are cheap and catch most hidden scope:

- **Where does the data come from?** Is everything the change needs already in the component's props, state or the response it already receives? If not, the change needs new data, and that is not a front-end tweak.
- **Who else uses this?** Grep for the component, hook, style or string you'd modify. If other screens use it, changing it changes them too.
- **Does it change behavior, not just presentation?** Validation, permissions, pricing, what gets saved, what gets sent, analytics events, routing.
- **Does it cross a boundary?** Backend code, API contract, database, shared packages, config, feature flags, dependencies.
- **Does it have runtime cost?** Extra requests, prefetching, polling, heavy rendering, big lists.

Then classify:

**Green: do it.** Changes inside the screen's own files that don't alter what gets saved or sent:

- presentation: markup, styles, copy, hiding or moving elements, reordering;
- UI behavior: opening and closing, focus, loading states, client-side sort or filter of data already loaded;
- switching to an existing pattern (modal, drawer, tabs) built with components the project already has;
- using data the component already receives;
- a local override of a shared component through what it already supports (an existing variant, prop or className on this one instance).

**Yellow: do it, but say so up front.** A text or literal change in one file outside the screen, with no consumers other than this screen, e.g. rewording an alert message that the backend builds, or dropping a detail from it. If anything parses that value (other clients, tests that assert it, the front end matching on it), it is red. Before editing, write one line: what else you're touching and why ("Esto toca backend: solo el texto del mensaje en `orders/errors.py`"). Then proceed.

**Red: stop, don't edit, alert.** Anything that needs new data or new systems, or that changes things beyond what the user is looking at:

- needs data the front end doesn't have (new field, endpoint, query, computed value);
- needs a new mechanism: caching, prefetch, background jobs, a global store, a recommendation or search logic;
- edits a shared component, style or hook that other screens use, unless the user explicitly said they want it everywhere ("en todos lados");
- changes business rules, permissions, validations, or the API contract;
- adds a new capability rather than adjusting an existing one (export, upload, notifications), unless it works entirely with what the screen already has;
- needs a migration, a new dependency, or config/env changes;
- grows past a handful of files or into a second screen.

When you're unsure about which systems a change touches, treat it as red: a ten-second question is cheaper than an unwanted subsystem. When you're unsure about what the user meant, that's not a red alert; ask in one line (step 1).

### 3. The red alert

Keep it short and concrete. Format:

> ⚠️ **Esto no es un cambio rápido.**
> **Pediste:** <the request in one line>
> **Lo que implica:** <what it really requires, naming the systems: "no hay datos de productos similares; habría que crear un endpoint y una lógica de similitud, y probablemente prefetch para que no tarde">
> **Opciones:**
> 1. <a reduced version that does fit the mode, if one exists: "mostrar productos de la misma categoría, que ya vienen en la respuesta">
> 2. Hacerlo completo como feature, fuera de este modo (lo planificamos).
> 3. Dejarlo.

Then wait for their choice. Offer the reduced version only if it is genuinely useful, not a token gesture; if there isn't one, drop it and renumber. If the reduced version has a catch, state it in the option ("obligatorio solo en el formulario; el backend sigue aceptando vacío").

If they pick the full version, leave quick-change mode for that request and treat it as normal feature work: plan it first (use the project's planning or brainstorming skill, or plan mode, if available) and get the plan approved before building. Come back to the mode after, if they want.

### 4. Make the change

- Smallest diff that does the job. Follow the file's existing patterns, naming and styling approach.
- No opportunistic refactors, renames or cleanups. If you notice something else worth fixing, mention it in one line at the end; don't fix it.
- **Re-check scope while you work.** If halfway through you find the change needs more than you classified (the data isn't there after all, the component is shared after all), stop and give the red alert then. Don't push through.
- When a change is a removal, remove what becomes dead with it (unused imports, the handler only that button used, its styles), but nothing beyond that.

### 5. Verify, quickly

Pick what's proportional and available:

- Type-check or lint the touched files when the project has it and it's fast.
- If a dev server for this checkout is already running, use it; never start a second one next to it. If none is running and one is easy to start, start it, and if the background test agent is running, tell it in the next update. Then open the page in the built-in browser if your environment has one (in the Claude desktop app, the browser pane; Claude in Chrome only if the user asks for it or there is no built-in browser, and never the user's own browser via `open <url>`) and take a screenshot to confirm the change looks right, including the state the user mentioned (the modal open, the alert showing).
- If you couldn't verify visually, say so.

### 6. Report

Two or three lines, no more:

- what changed and in which files;
- the scope level only if it was yellow (what else you touched), so the user can see it;
- how you verified it, or that you didn't;
- plus one line, only if you noticed something else worth fixing (step 4).

If the background test agent is running, send it the update for this change now (see `subagent-for-test`), and if it escalated something, put that first in your message.

Don't commit unless the user asks. Then wait for the next request.

## Examples

| Request | Level | Why |
|---|---|---|
| "Quitemos ese botón" (button rendered only on this page) | Green | Markup in the page file; also remove its now-unused handler. |
| "Quitemos ese botón" (button lives in a shared `Header` used on 12 pages) | Red | Removing it changes 12 screens. Options: hide it only here (green if `Header` already has a prop for it, otherwise a new prop), or remove it everywhere. |
| "Este botón en verde" (shared `<Button variant="primary">`, ~40 uses) | Green if an existing variant fits (`variant="success"` on this instance); red if it means editing the primary variant itself. |
| "Que el campo teléfono sea obligatorio" (backend accepts empty) | Red | Validation is a business rule. Reduced option: required only in this form, stating that the backend still accepts empty. |
| "Exportá esta tabla a CSV" (paginated server-side, 25 of ~3,000 rows loaded) | Red | Full export needs an endpoint. Reduced option: export the visible page client-side. |
| "Pasá este formulario a un modal" | Green | Use the project's existing `Dialog`/`Modal`; same form, same submit. Red if there's no modal component and one would have to be built or installed. |
| "Que esta alerta no diga el ID completo" (message built in the backend) | Yellow | One-line backend change; announce it before editing. |
| "En el menú de productos que se vean los similares" | Red | No similar-products data exists; needs an endpoint, similarity logic, probably prefetch. Offer a reduced version if the response already has something usable (same category). |
| "Ordená la tabla por fecha" | Green if the data is already loaded and sorted client-side; red if the table is paginated server-side (needs an API sort param). |
| "Mostrá el stock en la card" | Green if `stock` is already in the product object the card receives; red if it isn't. |
