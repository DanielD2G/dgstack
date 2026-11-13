# Which browser to use

This skill opens pages twice: to look at references while researching,
and to check each mockup before showing it. Use the first browser on this
list that your session actually has. Check your tool list; don't assume.

1. **T3 Code's browser (MCP server `t3-code`).** When the session runs
   inside T3 Code, its preview panel is the browser the user is looking
   at. Tools are named `mcp__t3-code__preview_*`:
   - `preview_open` / `preview_navigate` to load a URL;
   - `preview_snapshot` for a screenshot;
   - `preview_click`, `preview_type` and `preview_act` to interact;
   - `preview_evaluate` to run JavaScript (computed styles, checks);
   - `preview_resize` for the mobile viewport.
2. **Claude's built-in browser (MCP server `Claude_Browser`).** In the
   Claude desktop app, the browser pane, with tools named
   `mcp__Claude_Browser__*` (`preview_start` with a `url`, `navigate`,
   `computer` for screenshots and clicks, `read_page`, `javascript_tool`,
   `resize_window`). Load its own skill first if one is available.
3. **Codex's in-app browser.** In the Codex app, the bundled Browser
   plugin opens the in-app browser panel. The agent drives it through the
   `node_repl` MCP server (`agent.browsers.get("iab")`); asking for
   `@Browser` brings it in. If the plugin isn't enabled, tell the user
   once that turning it on (Plugins, Browser) gives Codex a browser to
   check mockups with.

**None of them:** research falls back to web search (say the research
was thinner), and the visual check is skipped (say so plainly when you
show the options; the brand check still runs, it doesn't need a
browser).

Rules that apply to all of them:

- Claude in Chrome, or any other browser extension that drives the
  user's own browser, only when the user asks for it.
- Never open the user's own browser: no `open <url>`, `xdg-open`,
  `webbrowser.open`, or a script that calls them.
- Open your own tab and close it when you're done. Other agents may be
  using the same browser; never touch tabs you didn't open.
- A tool that fails twice on the same page is a reason to move to the
  next browser on the list, with the error in your notes, not to keep
  retrying.
