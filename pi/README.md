# Pi configuration templates

Deploy through [setup_for_pi.md](../setup_for_pi.md). `<agent-dir>` is `PI_CODING_AGENT_DIR`, otherwise `~/.pi/agent`. Back up existing files and preserve unrelated settings and credentials.

| File | Target or required adaptation |
| --- | --- |
| [AGENTS.md](AGENTS.md) | `<agent-dir>/AGENTS.md`; render verified Conda/Python paths |
| [settings.json](settings.json) | Merge into `<agent-dir>/settings.json`; keep one source per package |
| [sub2api.json](sub2api.json) | `<agent-dir>/sub2api.json`; preserve an existing token or leave `YOUR_API_KEY` for the user |
| [web-search.json](web-search.json) | `<agent-dir>/web-search.json`; adapt the relay Responses URL and render `{{SUB2API_SEARCH_KEY_SCRIPT}}` as below |
| [read-sub2api-search-key.cjs](read-sub2api-search-key.cjs) | `<agent-dir>/read-sub2api-search-key.cjs`; reads the adjacent `sub2api.json` locally without duplicating its key |
| [open-tui.json](open-tui.json) | `<agent-dir>/open-tui.json` |
| [pi-btw.json](pi-btw.json) | `<agent-dir>/pi-btw.json` |
| [pi-pretty.json](pi-pretty.json) | Effective pi-pretty config directory (`PRETTY_CONFIG_DIR`, otherwise its home-directory default); `toolStyle: "claudecode"` |
| [subagents.json](subagents.json) | `<agent-dir>/subagents.json` |
| [pi-sync-suite.json](pi-sync-suite.json) | `<agent-dir>/pi-sync-suite.json`; use the user's own private SSH remote and an absolute local checkout path |
| [routing.toml](routing.toml) | Stable local configuration for the Task Router Pi installer; preserve its model choices |

The nine package entries are unpinned npm sources, including the three public amox facades. Normal installation needs no amox checkout or local prefix. Update with `pi update --extensions`. With approval, replace superseded local/old npm registrations rather than declaring both; do not separately load upstream engines.

This template does not install `@narumitw/pi-statusline`; it must not remove or disable an existing installation, including disabled object-form entries or separately discovered copies. After all installation and verification steps, explain any footer conflict and ask whether the user wants to remove it. Make registration changes only with explicit approval; otherwise preserve it and report the conflict as unresolved. Retain the nine requested packages in [settings.json](settings.json) in their exact relative order, with open-tui last after any preserved unrelated packages. Both pi-pretty styles install an editor; open-tui must load afterward to draw its inline footer in its own editor borders. Do not alphabetize the list. Restart fully and inspect the actual terminal.

[open-tui.json](open-tui.json) enables the inline footer, Chinese settings UI and session names, hides hostname and extension-status lines, and disables telemetry cost while retaining cumulative footer cost. Independent widgets, such as Pi Sync's own status panel, remain visible. `hideThinkingBlock: false` in [settings.json](settings.json) keeps full thinking visible; the one-line preview is only used when thinking is hidden.

Generate Router roles on each host; do not copy generated agents. Skill installation, including explicit-only Xiaohei illustrations, is specified in the setup document. Resolve pi-pretty's actual config directory before deployment: its default is not necessarily a custom Pi home. Preserve unrelated preferences and restart for the tool style to apply. Follow the [Pi Sync guide](pi-sync-setup.md) ([中文](pi-sync-setup.zh-CN.md)) for its manual-only policy; bootstrap must not synchronize data.

## Search routing

[web-search.json](web-search.json) routes `web_access` searches through the configured Sub2API/OpenAI Responses search first, then Exa for the listed recoverable errors. It uses `gpt-6.1-sol` independently of the main conversation model; Claude and other tool-capable conversation models can use the same search route. No Codex CLI or official Codex login is required when the relay provides search. The relay must accept the `web_search` tool, not just ordinary text requests.

Deploy [read-sub2api-search-key.cjs](read-sub2api-search-key.cjs) beside the deployed `sub2api.json`. Render `{{SUB2API_SEARCH_KEY_SCRIPT}}` in `openaiApiKey` with that script's absolute path (forward slashes on Windows); JSON-escape the resulting value. The script accepts a literal token or `${ENV_VAR_NAME}` and never prints configuration or credentials to stderr. It rejects placeholders, malformed/missing credentials and command-backed tokens. For an existing `!command` credential, preserve it and configure the search credential source separately with the user's approval; do not execute it during bootstrap or copy the real key into the template. Do not run the helper directly in a recorded terminal: its stdout is the secret.

Derive `openaiResponsesUrl` from the effective relay `baseURL`, appending `/v1/responses` (or `/responses` if it already ends in `/v1`). Keep `openaiSearchProviders: []` so search uses the real relay token rather than Pi's adapted Codex identity. Keep `openaiUseAlphaSearch: false`; Responses support does not imply `/alpha/search` support. `openaiApiKey` is an explicit credential source, so it does not accidentally select an unrelated `OPENAI_API_KEY`.

Merge these template-owned settings while preserving unrelated fetch/provider preferences. Remove superseded top-level `provider` and `searchProvider` overrides with approval: either overrides `searchRouting`. Do not set `searchRouting.useCurrentModel`; that official-endpoint route is not appropriate for this relay. Per-call explicit provider selection still overrides the default route. Authentication/configuration errors are not in the supported fallback list and may fail closed rather than trying Exa.

Do not also inject `web_search` through Sub2API `serverTools.responses`: that is a separate native-only path without this Exa fallback. On an existing installation, explain any such conflict and obtain approval before removing only the conflicting search definition; preserve other hosted tools. No extra Codex search extension is needed. Reload after deployment. Static validation does not prove search or fallback works; live search requires separate approval because it can consume relay quota. To test with approval, call `web_access` search without a provider override and inspect its reported provider; test failure routing separately without damaging the normal configuration.

Keep populated credentials, sessions, missions, caches, generated files and backups out of this repository.
