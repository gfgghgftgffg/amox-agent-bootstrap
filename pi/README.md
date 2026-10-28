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
| [autoresearch-skill.md](autoresearch-skill.md) | Render three `<agent-dir>/skills/autoresearch-*/SKILL.md` wrappers; see [setup](../setup_for_pi.md#autoresearch-skills) |
| [subagents.json](subagents.json) | `<agent-dir>/subagents.json` |
| [pi-sync-suite.json](pi-sync-suite.json) | `<agent-dir>/pi-sync-suite.json`; supply a private SSH remote and absolute checkout path |
| [routing.toml](routing.toml) | Stable configuration path for the Router installer |

## Interface

Deploy the values in [settings.json](settings.json), [starline.json](starline.json) and the [theme](themes/catppuccin-mocha.json). See [interface settings](../setup_for_pi.md#interface) and [package migration](../setup_for_pi.md#2-packages).

Apply Catppuccin Mocha to both Pi and the active terminal profile using the [appearance guide](appearance.md) ([中文](appearance.zh-CN.md)). Font installation and opacity remain user-managed: **Maple Mono NF CN**, **95% opacity**.

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

- Install [Skills](../setup_for_pi.md#3-skills) and generate [Router roles](../setup_for_pi.md#5-task-router) using the deployment instructions.
- Keep Pi Sync manual and follow [English](pi-sync-setup.md) / [中文](pi-sync-setup.zh-CN.md). Bootstrap does not transfer data.
- Keep credentials, sessions, caches and backups out of Git.
