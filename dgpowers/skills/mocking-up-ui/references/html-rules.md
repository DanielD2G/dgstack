# Rules for each HTML mockup

Each mockup is one self-contained `.html` file (inline `<style>` and
`<script>`) that renders fully over a local HTTP server or from disk.
The implementer will copy it, so build it the way the product is built.

## Identity fidelity (the hard part)

- Declare the identity's tokens on `:root` **with the project's own
  variable names** (`--color-primary`, `--radius-lg`, or names derived
  from the Tailwind theme keys if that's what the project uses).
  Components reference only these variables: no loose hex values, no new
  fonts.
- Same fonts as the product, loaded the same way where possible (a Google
  Fonts link if that's the source; otherwise the closest available weight
  of the same family, noted in a comment).
- Icons: inline SVG only, never emojis. Use the product's own icon set
  first (copy the actual SVG paths from its library or source, same
  stroke width); `references/icons.md` covers sourcing anything missing.
- Rebuild existing components to match their real look (button heights,
  paddings, borders, focus rings, hover states) rather than inventing new
  ones. If a piece needs a component the product doesn't have, build it
  out of the existing visual vocabulary and say so in the comment at the
  top of the file: the plan will need a task for it.
- Copy tone and language from the product. Reuse its real labels where
  they exist, minus any emojis. Copy the user or the design doc fixed
  (labels, messages, option names) goes in word for word; a better
  wording is a question for the user, not a silent change.
- No emojis anywhere: not as icons, bullets, decoration or in copy, even
  where the product itself uses them. `option-0-current.html` is the one
  exception: it stays faithful to what exists today. The other files
  replace the product's emojis in the surrounding context too (with icons
  from the product's set, or nothing).
- Anything outside the identity is a "proposed token": list it in
  `decision.md` and in the comment at the top of the file.

## Structure

- Render the piece **in context**: approximate the surrounding UI (page
  background, what's above and below, the nav) so the user judges it in
  place. Keep the surroundings identical across the options for one
  piece, copied from option 0, so only the piece changes.
- A new field or control is drawn inside its whole component, never on
  its own.
- An overlay (modal, sheet, drawer, popover) is drawn open over its
  context, with the trigger visible or noted.
- Show every state listed for the piece in the UI map, either stacked
  below the main view with a small caption each, or through a switcher
  labeled "Preview state" that is visually separate from the product UI.
- Use realistic data: real-looking names, amounts and dates, one long
  value that tests wrapping, no lorem ipsum, no "Item 1".
- At least one real interaction works when the structure depends on it
  (tabs switch, a disclosure opens, a chip toggles).
- **Flow steps:** each step is its own file (`step-1-<name>.html`, …),
  sharing the same frame, step indicator and navigation, with the
  current step marked. The last file is the end state.

## Technical

- Mobile products: design at 375-430px; on wide viewports center the
  screen in a device-sized frame. Desktop products: look right at about
  1440px and don't break at 375px.
- Prefer inline SVG over external libraries. If a library is needed, pin
  an exact version from cdnjs.cloudflare.com or cdn.jsdelivr.net/npm.
- Respect `prefers-reduced-motion`. Don't hide content behind entrance
  animations: an element that starts at `opacity: 0` looks broken in a
  background screenshot.
- No console errors, no horizontal overflow.
- `<title>`: "<product> · <piece> · <option name>". First comment in the
  file: the option's spec in a few lines, the existing components it
  reuses, any new component it needs, and any deviation from the
  identity.
