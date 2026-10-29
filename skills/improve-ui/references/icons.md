# Icons, never emojis

## No emojis

Don't use emojis anywhere in a mockup: not as icons, bullets, status markers, decoration, or inside copy ("¡Hola! 👋", "📅 Fechas"). They render differently on every OS, can't take the design's color, stroke or size, and are the fastest tell of a generic AI mockup. Where an emoji would go, use an SVG icon or nothing.

## Where icons come from

Every icon is inline SVG pasted into the file (no runtime icon fetching, so the file stays self-contained). In order of preference:

1. **The product's own icon set**, when there is one (improve-ui): copy its SVGs from the project.
2. **[Iconify](https://icon-sets.iconify.design/)**: 200k+ icons from open sets (Lucide, Tabler, Phosphor, Material Symbols, Iconoir, Mingcute…). It has an API you can use from Bash:
   - Search: `curl -s "https://api.iconify.design/search?query=<term>&limit=32"`. Add `&prefixes=lucide,tabler` to stay within chosen sets. The response lists matching icons and each set's license.
   - Get the SVG: `curl -s "https://api.iconify.design/<set>/<name>.svg"`, e.g. `https://api.iconify.design/lucide/plane.svg`.
3. **[Simple Icons](https://simpleicons.org/)** for brand logos (airlines, payment methods, social networks): `curl -s "https://cdn.simpleicons.org/<slug>"`.
4. **[thesvg](https://github.com/glincker/thesvg)** and **[freeicons.io](https://freeicons.io/)** when the above don't have it.

Pick **one set per option** (or the product's set) and stick to it: same grid, stroke width, line caps and fill style. Mixing sets looks off even when each icon is fine. Respect licenses: prefer MIT/Apache/ISC/CC0 sets, and note set and license in the file's top comment, e.g. `Icons: Lucide (ISC)`.

After pasting, make icons inherit the design: `stroke="currentColor"`/`fill="currentColor"` instead of hardcoded colors, size through CSS, and `aria-hidden="true"` unless the icon is the only label (then give it an accessible name).

## When nothing fits: draw it with a subagent

For a custom concept, a mascot or a spot illustration no set covers, delegate it to a subagent rather than improvising inline. Brief it with: what the icon must show, the target set's specs (viewBox, e.g. `0 0 24 24`; stroke width; caps/joins; filled or outline; corner style), 1–2 SVGs from the chosen set as style references, and the output (a single optimized inline `<svg>` with `currentColor`). Check the result rendered at its real size before using it.

## Check

Before delivering, scan the outputs for emojis:

```bash
python3 -c "import re,sys;p=re.compile('[\U0001F000-\U0001FAFF☀-➿️]');[print(f,i+1,l.strip()[:80]) for f in sys.argv[1:] for i,l in enumerate(open(f,encoding='utf-8')) if p.search(l)]" mockups/<slug>/*.html
```

No output means clean. Fix every hit.
