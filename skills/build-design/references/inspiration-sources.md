# Inspiration sources

## Dribbble (primary)

- Tag: `https://dribbble.com/tags/<tag>` — hyphenated or underscored depending on the tag, e.g. `ui-ux-dashboard`, `dashboard`, `saas-dashboard`, `login`, `settings-page`, `landing-page`, `mobile-app`, `fintech`, `analytics`. If a tag 404s or has little content, try variants or search.
- Search: `https://dribbble.com/search/<query>` with the query in kebab-case, e.g. `https://dribbble.com/search/crm-dashboard`.
- Shot: `https://dribbble.com/shots/<id>-<slug>` — shows the large image, sometimes several, and related tags (useful for finding more).
- Useful URL filters on search: `?timeframe=year` or `?timeframe=month` to see recent work instead of the same old classics.

How to navigate:
1. Open the tag/search page, take a screenshot and scroll 2–3 times to see the grid.
2. Use `get_page_text` or `find` to pull links to the shots that caught your eye.
3. Open the best ones and screenshot them (zoom into interesting areas: header, cards, charts, tables, illustrations).
4. If a sign-up modal appears, close it; if it blocks the page, move on to another source.

Beware: Dribbble has a lot of "dribbble-ware" (pretty but unusable screens, absurd data, illegible contrast). Take the visual ideas and filter out what wouldn't work in a real product; the debate critics will flag it too.

## Other sources

Use 1–2 if Dribbble falls short, is too uniform, or the screen type calls for it:

| Source | URL | Good for |
|---|---|---|
| Mobbin | `https://mobbin.com/search/apps/web?content_type=screens&q=<query>` | Real production product screens (may require login: if so, skip it) |
| Land-book | `https://land-book.com/?search=<query>` | Landing pages and marketing sites |
| Godly | `https://godly.website` | Sites with strong personality, motion, bold type |
| Lapa Ninja | `https://www.lapa.ninja/?s=<query>` | Landings by category |
| SaaS Landing Page | `https://saaslandingpage.com` | SaaS landings |
| Behance | `https://www.behance.net/search/projects/<query>` | Full case studies with a visual system |
| Awwwards | `https://www.awwwards.com/websites/<tag>/` | Award-winning, experimental sites |

## What to record for each reference

- URL and title/author
- Palette: background, surface, text, accent (approximate hex)
- Typography: likely family or kind, size contrast, use of caps/tracking
- Layout: navigation (sidebar/topbar/tab bar), grid, density, asymmetry
- Surfaces: radii, borders, shadows, blur, gradients, textures
- Data: chart types, how KPIs are highlighted, tables
- Illustration: style, line weight, how it's integrated with the UI
- Distinctive detail: what makes it memorable
- Risks: what wouldn't work in a real product
