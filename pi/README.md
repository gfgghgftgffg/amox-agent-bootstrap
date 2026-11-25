# Pi configuration templates

Deploy through [setup_for_pi.md](../setup_for_pi.md). `<agent-dir>` is `PI_CODING_AGENT_DIR`, otherwise `~/.pi/agent`. Back up changed files and preserve unrelated settings and credentials.

## File map

| File | Target / adaptation |
| --- | --- |
| [AGENTS.md](AGENTS.md) | `<agent-dir>/AGENTS.md`; render Conda/Python paths |
| [settings.json](settings.json) | Merge into `<agent-dir>/settings.json` |
| [starline.json](starline.json) | `<agent-dir>/starline.json` |
| [themes/catppuccin-mocha.json](themes/catppuccin-mocha.json) | `<agent-dir>/themes/catppuccin-mocha.json` |
| [sub2api.json](sub2api.json) | `<agent-dir>/sub2api.json`; merge by provider name and preserve existing tokens |
| [web-search.json](web-search.json) | `<agent-dir>/web-search.json`; render the relay provider name |
| [read-sub2api-search-key.cjs](read-sub2api-search-key.cjs) | Beside the deployed `sub2api.json`; only for the [standalone API-key alternative](#standalone-api-key-alternative) |
| [pi-btw.json](pi-btw.json) | `<agent-dir>/pi-btw.json` |
| [pi-high-level.json](pi-high-level.json) | Merge into `<agent-dir>/pi-high-level.json` |
| [autoresearch-skill.md](autoresearch-skill.md) | Render three `<agent-dir>/skills/autoresearch-*/SKILL.md` wrappers; see [setup](../setup_for_pi.md#autoresearch-skills) |
| [subagents.json](subagents.json) | `<agent-dir>/subagents.json` |
| [amox-pi-sync.json](amox-pi-sync.json) | `<agent-dir>/amox-pi-sync.json`; supply a private SSH remote and absolute checkout path |
| [routing.toml](routing.toml) | Stable configuration path for the Router installer |

## Interface

Deploy the values in [settings.json](settings.json), [starline.json](starline.json) and the [theme](themes/catppuccin-mocha.json). See [interface settings](../setup_for_pi.md#interface) and [package migration](../setup_for_pi.md#2-packages).

Apply Catppuccin Mocha to both Pi and the active terminal profile using the [appearance guide](appearance.md) ([中文](appearance.zh-CN.md)). Font installation and opacity remain user-managed: **Maple Mono NF CN**, **95% opacity**.

## Search routing

Use the values in `web-search.json`:

| Setting | Value / adaptation |
| --- | --- |
| Search order | `exa` → `openai` |
| `searchRouting.fallbackOn` | `empty`, `domain-miss`, `unsupported`, `transient`, `quota`, `network`, `invalid-response` |
| `openaiSearchProviders` | `["sub2api-gpt-only"]`, the GPT provider registered from `sub2api.json` |
| `openaiUseProviderBaseUrl` | `true`; derives `<relay baseURL>/v1/responses` from the resolved provider credentials |
| Search model | `gpt-6.2-sol`, independent of the conversation model |
| `openaiUseAlphaSearch` | `false` |

Exa is first because it needs no key and returns bounded raw results; the OpenAI/Codex step runs a full Responses turn and bills its tokens. A caller that names a provider bypasses this route entirely, so `provider: "openai"` still reaches the relay on demand.

`empty` and `domain-miss` are deliberate: a technically successful but unusable Exa response moves on to the OpenAI step instead of ending the search. Exa is semantic and rarely returns zero results, so in practice hard failures (`quota`, `network`, `invalid-response`, `unsupported`) are the common trigger. Do not add `off-topic`: it needs a Cloudflare Workers AI or typesafe judge model that this setup does not register.

The OpenAI step reuses the relay credential that Pi already resolves for the provider, so `web-search.json` holds no key and no second copy of the relay URL.

### Standalone API-key alternative

If the relay credential cannot be resolved through Pi's provider registry, set `openaiResponsesUrl` to the full Responses endpoint, set `openaiApiKey`, and drop `openaiUseProviderBaseUrl`; an explicit `openaiResponsesUrl` wins over the derived one. The helper reads the adjacent `sub2api-gpt-only` token and uses legacy `sub2api` when the GPT-only entry is absent. It supports literal values and `${ENV_VAR_NAME}`. Preserve command-backed credentials and request a separate approved search source. Do not run the helper directly in a recorded terminal: its stdout is the token.

Preserve unrelated fetch settings. With approval, remove conflicting top-level `provider`/`searchProvider` overrides and Sub2API `serverTools.responses` search injection. Keep other hosted tools. Do not set `searchRouting.useCurrentModel`: it only accepts official OpenAI, ChatGPT Codex and Azure endpoints, so a relay never qualifies. Live search tests require separate approval.

## Other configuration

- Install [Skills](../setup_for_pi.md#3-skills) and generate [Router roles](../setup_for_pi.md#5-task-router) using the deployment instructions.
- Keep Pi Sync manual and follow [English](pi-sync-setup.md) / [中文](pi-sync-setup.zh-CN.md). Bootstrap does not transfer data.
- Keep credentials, sessions, caches and backups out of Git.
