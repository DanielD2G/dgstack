# dgstack

Personal collection of agent skills. Each skill lives in `skills/<name>/` with a `SKILL.md` and optional `references/` and `assets/`.

## Conventions

- **Write every skill in English**: `SKILL.md`, references, assets, file and folder names, and the `name`/`description` frontmatter. Trigger phrases in the description may include Spanish examples, since the user often asks in Spanish.
- A skill's instructions should tell the agent to answer the user in the user's language, not in the language the skill is written in.
- **Icons, never emojis:** skills that produce UI must forbid emojis in the output (as icons, bullets, decoration or in copy) and use inline SVG icons instead, sourced from the product's own set, [Iconify](https://icon-sets.iconify.design/), [Simple Icons](https://simpleicons.org/), [thesvg](https://github.com/glincker/thesvg), [freeicons.io](https://freeicons.io/) or similar, or drawn by a subagent when nothing fits. Skills are self-contained, so each one carries its own `references/icons.md` (keep the copies in sync; `skills/build-design/references/icons.md` is the canonical one).
- **Browsers:** any skill that opens pages, previews or screenshots must say to use the built-in browser when the environment has one (in the Claude desktop app, the browser pane: `mcp__Claude_Browser__*`). Claude in Chrome is only for when the user asks for it or there is no built-in browser. A skill never opens the user's own browser (`open <url|file>`, `xdg-open`, `webbrowser.open`, or a script that calls it). This applies to agents working on this repo too, for example when showing the skill-creator eval viewer: generate it with `--static` and load the file in the browser pane.
