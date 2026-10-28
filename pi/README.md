# Pi configuration templates

Deploy through [setup_for_pi.md](../setup_for_pi.md). `<agent-dir>` is `PI_CODING_AGENT_DIR`, otherwise `~/.pi/agent`. Back up changed files and preserve unrelated settings and credentials.

## File map

| File | Target / adaptation |
| --- | --- |
| [AGENTS.md](AGENTS.md) | `<agent-dir>/AGENTS.md`; render Conda/Python paths |
| [settings.json](settings.json) | Merge into `<agent-dir>/settings.json` |
| [starline.json](starline.json) | `<agent-dir>/starline.json` |
| [themes/catppuccin-mocha.json](themes/catppuccin-mocha.json) | `<agent-dir>/themes/catppuccin-mocha.json` |
| [sub2api.json](sub2api.json) | `<agent-dir>/sub2api.json`; preserve the existing token |
| [web-search.json](web-search.json) | `<agent-dir>/web-search.json`; render helper path and relay URL |
| [read-sub2api-search-key.cjs](read-sub2api-search-key.cjs) | Beside the deployed `sub2api.json` |
| [pi-btw.json](pi-btw.json) | `<agent-dir>/pi-btw.json` |
| [subagents.json](subagents.json) | `<agent-dir>/subagents.json` |
| [pi-sync-suite.json](pi-sync-suite.json) | `<agent-dir>/pi-sync-suite.json`; supply a private SSH remote and absolute checkout path |
| [routing.toml](routing.toml) | Stable configuration path for the Router installer |

## Interface

Use the nine unpinned npm packages in `settings.json`, with starline last. Replace pi-pretty, pi-open-tui and pi-statusline with pi-tidy + pi-starline; preserve old preferences for rollback. Update packages with `pi update --extensions`.

| Setting | Value |
| --- | --- |
| Tools | `defaultTools: ["+codemode"]`; retain existing tools |
| Theme | `catppuccin-mocha`; deploy the theme before selecting it |
| Diff backgrounds | `toolSuccessBg: "base"` for red/green highlights |
| Tidy | Message frames on, `frameUserMessages: false` |
| Starline editor | `editorPaddingY: 0`, `editorMetadataFormat: ""` |
| Directory | `pathDisplay: { "mode": "full", "depth": 0 }` |
| Thinking colors | Leave `colors.thinking` unset |
| Queue pill | Off; keep native pending-message text |
| Pill order | Model, thinking, subagents, directory, session name, runtime, Git, context, cost, session duration, time, extension statuses |

Restart Pi after deployment. `/starline` adjusts layout/colors; `/starline queue` opens queued messages from the keyboard.

**Apply Catppuccin Mocha to both Pi and the active terminal profile.** Deploy the Pi theme, then detect the terminal and import/select its official Mocha scheme after backing up the profile. Check both separately; a Pi-only change or an imported-but-unselected terminal scheme is incomplete. Report an inaccessible terminal as pending.

Font installation and opacity remain user-managed: **Maple Mono NF CN**, **95% opacity**. See [English](appearance.md) / [中文](appearance.zh-CN.md).

## Search routing

Use the values in `web-search.json`:

| Setting | Value / adaptation |
| --- | --- |
| Search order | `openai` → `exa`, with the template's recoverable-error list |
| Search model | `gpt-6.1-sol`, independent of the conversation model |
| `openaiApiKey` | Replace `{{SUB2API_SEARCH_KEY_SCRIPT}}` with the deployed helper's absolute path; JSON-escape it |
| `openaiResponsesUrl` | Derive from the existing relay `baseURL`: append `/v1/responses`, or `/responses` when it already ends in `/v1` |
| `openaiSearchProviders` | `[]` |
| `openaiUseAlphaSearch` | `false` |

The helper reads the adjacent Sub2API token, supporting literal values and `${ENV_VAR_NAME}`. Preserve command-backed credentials and request a separate approved search source. Do not run the helper directly in a recorded terminal: its stdout is the token.

Preserve unrelated fetch settings. With approval, remove conflicting top-level `provider`/`searchProvider` overrides and Sub2API `serverTools.responses` search injection. Keep other hosted tools. Do not set `searchRouting.useCurrentModel`. Live search tests require separate approval.

## Other configuration

- Install the Skills listed in [setup_for_pi.md](../setup_for_pi.md#3-skills), including complete resources and explicit-only flags. `anti-defensive-writing` is explicit-only; `humanizer` and `design-taste-frontend` remain available automatically.
- Generate Router roles on each host using `routing.toml`; do not copy generated agents. Maintain shared rules in the stable Router checkout’s `AGENTS.md`, keep environment requirements portable without personal paths or unresolved placeholders, and preserve custom edits. Generated Pi roles enable Skills and scoped codemode without widening tool permissions. Do not add a Router block to global Pi instructions.
- Keep Pi Sync manual and follow [English](pi-sync-setup.md) / [中文](pi-sync-setup.zh-CN.md). Bootstrap does not transfer data.
- Keep credentials, sessions, caches and backups out of Git.
