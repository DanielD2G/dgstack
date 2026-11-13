# Extracting the visual identity

Goal: know the product's visual language well enough that a new version of the element is indistinguishable in style from the rest of the app. Exact values beat impressions: "radius 22px, 2.5px navy border, hard 0 6px 0 shadow" is useful; "rounded and playful" is not.

## 1. Code

Search the repo (ignore `node_modules`, build output) for:

| What | Where it usually lives |
|---|---|
| CSS variables | `globals.css`, `app.css`, `index.css`, `:root {` / `[data-theme]` / `.dark {` blocks |
| Tailwind | `tailwind.config.*` (`theme.extend`), Tailwind v4 `@theme {` blocks in CSS |
| Theme objects | `theme.ts`, `createTheme(` (MUI), `extendTheme(` (Chakra), styled-components `ThemeProvider`, Vuetify/Quasar config |
| Design tokens | `tokens.json`, `*.tokens.json`, Style Dictionary config, a `design-system`/`ui` package in a monorepo |
| shadcn/ui | `components.json`, `components/ui/*` (variants live in `cva(` calls) |
| SCSS/LESS | `_variables.scss`, `$primary:` etc. |
| Fonts | `next/font` imports, `@font-face`, Google Fonts `<link>`, `fontFamily` in the theme |
| Icons | imports from `lucide-react`, `@heroicons`, `react-icons`, `@phosphor-icons`, a local `icons/` folder. If there is no icon set (or the product uses emojis as icons), pick one per `references/icons.md` that matches the identity's stroke and corner style, and record it here |
| Components | Button, Input, Select, Card, Dialog/Modal/Sheet, Tabs, Badge/Chip, Toast; read their variants and sizes |

Also read the target element's own source and 2–3 sibling components on the same screen. Local patterns often matter more than the global theme.

If the "product" is a single HTML file or a mockup (no repo structure), the identity is whatever that file defines: read its `:root` variables and its CSS.

## 2. Live app

1. **Is it running?** Check `.claude/launch.json`, `package.json` scripts (`dev`, `start`, `serve`) for the expected port, then `lsof -nP -iTCP -sTCP:LISTEN | grep -E 'node|vite|next|python|ruby|php|bun|deno'`. Try the URL in the browser.
2. **Running:** open the route that contains the element. Screenshot the element, then the full screen, then 2–3 other representative screens. If tokens are ambiguous, read real values with the browser's JS tool, e.g. `getComputedStyle(document.querySelector('<selector>'))`, or collect the CSS variables on `:root`.
3. **Not running:** ask the user before starting anything. Use AskUserQuestion with the exact command (e.g. `npm run dev` on port 3000) and say why you want to see it. Starting a server may need env vars or secrets (if the repo has a `.env.lock`, the `lock` skill covers running with them), install dependencies or touch databases, so it's their call. If they say yes, start it with the preview/launch tooling or a background shell, and stop it when you're done unless they want it kept. If they say no, work from code plus any screenshots they provided.
4. Don't log in with real credentials or change data in the app. If the element sits behind auth and you can't reach it, ask the user for a screenshot.

## 3. Write `identity.md`

```
# Identity: <product>
Sources: <files read, screens captured>

## Color
<token name> = <value> — <role: background / surface / text / muted / accent / border / success / danger…>
(light and dark if both exist)

## Typography
Display: <family, weights>; Text: <family, weights>; Mono: <…>
Scale actually in use: <sizes/line-heights for titles, body, labels, captions>
Treatments: <uppercase labels with tracking? tabular numbers? …>

## Shape and depth
Radii: <values and where each is used>
Borders: <widths/colors>
Shadows: <exact values; e.g. hard offset vs soft blur>
Spacing rhythm: <base unit, common paddings/gaps>

## Components available
<Button variants/sizes, Input, Tabs, Card, Dialog/Sheet… with what they look like>

## Iconography and illustration
<icon set, stroke width, size; illustration style if any>

## Motion
<durations/easing, what animates>

## Voice
<language, formality, how CTAs are phrased; emoji use as an observation only: mockups never use emojis, so if the product relies on them, list where under "Inconsistencies found" and which icon from the product's set would replace each>

## Do / Don't
<5-10 rules that capture the feel, e.g. "Do: chunky 2.5px navy outlines on interactive surfaces. Don't: soft blurred shadows.">

## Inconsistencies found
<hardcoded values, competing styles; which one you chose to follow>
```

## 4. Write `tokens.json`

Used by `scripts/check_brand.py`. Include every color the identity legitimately uses (all themes) and every font family:

```json
{
  "colors": ["#1d2b4f", "#ffffff", "#f7c948", "#ef7461", "#6fcf9f", "#eef5ff"],
  "fonts": ["Baloo 2", "Nunito"],
  "allow": ["transparent", "currentColor"]
}
```

Colors in any CSS form (hex, rgb(), hsl()) are fine; the checker normalizes them. Alpha variants of a listed color are accepted automatically.
