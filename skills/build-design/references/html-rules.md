# Rules for each HTML mockup

Each option is a single `.html` file that opens with a double click and renders fully, with no build step.

## Technical

- One self-contained file: HTML + inline `<style>` + `<script>`. No external images copied from the references.
- Fonts: Google Fonts via `<link>` (with preconnect). Always with a system fallback.
- External libraries only when they really add something, pinned to an exact version and loaded from cdnjs.cloudflare.com or cdn.jsdelivr.net/npm (e.g. `chart.js@4.4.1`). For simple charts prefer inline SVG: instant load and full control over the style.
- Icons: inline SVG only, never emojis. Follow `references/icons.md` for where to get them (Iconify, Simple Icons…), how to keep one consistent set per option, and when to have a subagent draw a missing one.
- Illustrations (mascots, spot art, maps): draw them as inline SVG in the option's own style. Keep them simple enough to look intentional — a few shapes with consistent stroke and fill beat a detailed drawing that falls apart.
- All colors, radii, shadows, spacing and fonts as custom properties on `:root`. No loose hex values inside components: that's what makes the option congruent and easy to tweak.
- Responsive: desktop screens must look good at 1440px and not break at 375px (no horizontal scroll; sidebar collapses, grids stack). Mobile screens are designed at 375–430px wide; on a wide viewport show them centered in a device-sized frame rather than stretched.
- No console errors.

## Content

- Exactly the content from the shared spec: same sections, same data, same copy. Data must be believable (plausible real names, sensible amounts, recent dates, coherent +/- changes).
- No lorem ipsum, "Item 1", "John Doe" or suspiciously round numbers (12,000, 50%).
- Show at least one interaction state: hover on rows/cards/buttons, an active nav item, a visible focus. If the screen warrants it, a small working toggle (tabs, date range, light/dark) adds a lot to the product feel.

## Aesthetics

- Follow the visual spec to the letter: it's what makes this option distinct. If something in the spec doesn't work once built, adjust it and note that in an HTML comment at the top of the file.
- The signature detail must be visible at first glance, not hidden below the fold.
- Clear hierarchy: one thing dominates, the rest supports it. Text contrast at least WCAG AA.
- Avoid generic tics: default purple-blue gradient, glassmorphism for no reason, the same huge radius on everything, emojis anywhere, identical grey shadows everywhere.
- Put the option's name in the `<title>` and, as the first comment in the file, a summary of the visual spec (tokens and fonts) so it can be iterated on without hunting for decision.md.
