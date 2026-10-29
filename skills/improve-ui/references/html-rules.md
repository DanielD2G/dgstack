# Rules for each HTML mockup

Each option is one self-contained `.html` file (inline `<style>`/`<script>`) that renders fully with a double click or over a local HTTP server.

## Identity fidelity (the hard part)

- Declare the identity's tokens on `:root` **with the project's own variable names** (e.g. `--color-primary`, `--radius-lg`, or names derived from the Tailwind theme keys if that's what the project uses). Components reference only these variables: no loose hex values, no new fonts.
- Same fonts as the product, loaded the same way where possible (Google Fonts link if that's the source; otherwise the closest available weight of the same family, noted in a comment).
- Icons: inline SVG only, never emojis. Use the product's own icon set first (copy the actual SVG paths from its library or source, same stroke width); follow `references/icons.md` for sourcing anything missing.
- Rebuild existing components to match their real look (button heights, paddings, borders, focus rings, hover states) rather than inventing new ones. If the option needs a component the product doesn't have, build it out of the existing visual vocabulary and note it in a comment at the top of the file.
- Copy tone and language from the product. Reuse its real labels where the element already has them, minus any emojis.
- No emojis anywhere: not as icons, bullets, decoration or in copy, even where the product itself uses them. `option-0-current.html` is the one exception: it stays faithful to what exists today. Options 1..N replace the product's emojis in the surrounding context too (with icons from the product's set, or nothing) and share that cleaned context with each other.
- Anything outside the identity must be listed as a "proposed token" in `decision.md`, and in an HTML comment at the top of the file.

## Structure

- Implement the option's structural spec faithfully. The structure is what's being evaluated, so it should be obvious at first glance how this option differs from option 0.
- Render the element **in context**: approximate the surrounding UI (background, what's above and below, nav) so the user can judge it in place. Keep the surroundings identical across options 1..N (copy them from option 0, with emojis replaced as described above) so only the element changes.
- Show the states that matter for this element (e.g. filled vs empty, error, loading) either stacked below the main view or via a small state switcher labeled "Preview state", visually separated from the product UI.
- At least one real interaction works (tabs switch, a sheet opens, a chip toggles) when the structure depends on it.

## Technical

- Mobile products: design at 375–430px; on wide viewports center the screen in a device-sized frame. Desktop products: look right at ~1440px and don't break at 375px.
- Prefer inline SVG over external libraries. If a library is needed, pin an exact version from cdnjs.cloudflare.com or cdn.jsdelivr.net/npm.
- Respect `prefers-reduced-motion`. Don't hide content behind entrance animations: an element that starts at `opacity: 0` looks broken in a background screenshot.
- No console errors, no horizontal overflow.
- `<title>`: "<product> · <option name>". First comment in the file: the structural spec in a few lines and any deviations from the identity.
