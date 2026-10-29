# dgstack

The agent skills I use every day, cleaned up so anyone can use them. They are
written for Claude Code and work in any harness that loads `SKILL.md` skills,
like Codex. Their trigger phrases cover both English and Spanish.

## Skills

| Skill | Say | What it does |
|---|---|---|
| `build-design` | "make me a login page", "generame 3 opciones en html" | Researches real references on Dribbble and similar sites, has subagents debate directions, and builds 3 to 5 HTML mockups you can compare side by side. |
| `improve-ui` | "quiero mejorar este modal", "redesign this card in our style" | Redesigns one existing element of your product: extracts its identity from the code and the running app, then proposes 3 better structures that stay on brand. |
| `quick-change` | "modo cambio rápido", "quitemos ese botón" | Small front-end tweaks with a small diff, and a scope guard that stops and warns you when a "small" change would touch data, endpoints or shared components. |
| `backtrack-for-test` | "testeá lo que cambiamos", "backtrack for test" | Backfills tests for code that changed without them, deciding what deserves a test and writing it in the project's own setup. |
| `subagent-for-test` | "testeá en segundo plano", "subagent for test" | Runs `backtrack-for-test` in a background agent that follows your changes on the same branch, while you keep working. |
| `debug-it-quick` | "debugeá esto", "tira 502", "se cayó" | Maps every system that could be involved (containers, cloud, database, DNS, CI, your machine), fans out cheap parallel scouts, and digs in only where they find something. |

Some skills call others. Install the ones they need too:

- `subagent-for-test` uses `backtrack-for-test`.
- `quick-change` offers `subagent-for-test` when you enter the mode.
- `build-design` and `improve-ui` point to each other: one explores new looks, the other respects an existing identity.

## Install

With the [`skills`](https://github.com/vercel-labs/skills) CLI:

```bash
npx skills add DanielD2G/dgstack
```

Or by hand:

```bash
git clone https://github.com/DanielD2G/dgstack
cp -R dgstack/skills/* ~/.claude/skills/   # Claude Code
cp -R dgstack/skills/* ~/.codex/skills/    # Codex
```

To install a single skill, copy only its folder, for example
`cp -R dgstack/skills/quick-change ~/.claude/skills/`.

## Requirements

- `python3` for `improve-ui`'s brand check and for serving mockups locally.
- A harness with subagents for `subagent-for-test`. `build-design`,
  `improve-ui` and `debug-it-quick` use them too, and fall back to doing the
  work in a single agent, slower, when there are none.
- A browser the agent can drive to preview mockups and screenshot your app. In
  the Claude desktop app that is the built-in browser pane.
- `debug-it-quick` uses whatever CLIs your systems need (`docker`, `kubectl`,
  `aws`, `gh`, ...), already authenticated.

## Make them yours

These are starting points. Edit them. Put personal settings in your
`CLAUDE.md` or `AGENTS.md` instead of the skill files, so you can update the
skills without losing them.

Each skill keeps its evals in `skills/<name>/evals/`. To work on a skill, use
the [skill-creator](https://github.com/anthropics/skills) workflow; its
`<name>-workspace/` folders are ignored by git.

## License

[MIT](LICENSE)
