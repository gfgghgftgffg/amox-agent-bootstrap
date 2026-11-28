# Pi Configuration Templates

[Template map](#template-map) • [Interface](#interface) • [Search routing](#search-routing) • [Related guides](#related-guides)

Configuration templates and helper files deployed by [setup_for_pi.md](../setup_for_pi.md). Resolve `<agent-dir>` from `PI_CODING_AGENT_DIR`, or `~/.pi/agent` when unset. Back up any file before modifying it, and preserve existing tokens and unrelated settings.

## Template map

| Source file | Target path and deployment action |
| --- | --- |
| [AGENTS.md](AGENTS.md) | `<agent-dir>/AGENTS.md`; substitute verified Conda and Python paths |
| [settings.json](settings.json) | Merge template-owned keys into `<agent-dir>/settings.json` |
| [starline.json](starline.json) | Copy to `<agent-dir>/starline.json` |
| [themes/catppuccin-mocha.json](themes/catppuccin-mocha.json) | Copy to `<agent-dir>/themes/catppuccin-mocha.json` |
| [sub2api.json](sub2api.json) | Merge into `<agent-dir>/sub2api.json` by provider name; keep existing tokens |
| [web-search.json](web-search.json) | Copy to `<agent-dir>/web-search.json`; match the GPT-only relay provider name |
| [read-sub2api-search-key.cjs](read-sub2api-search-key.cjs) | Copy next to deployed `sub2api.json` only when using the [standalone API-key alternative](#standalone-api-key-alternative) |
| [pi-btw.json](pi-btw.json) | Copy to `<agent-dir>/pi-btw.json` |
| [pi-high-level.json](pi-high-level.json) | Merge into `<agent-dir>/pi-high-level.json` |
| [autoresearch-skill.md](autoresearch-skill.md) | Render `<agent-dir>/skills/autoresearch-{create,finalize,hooks}/SKILL.md` ([instructions](../setup_for_pi.md#autoresearch-skills)) |
| [subagents.json](subagents.json) | Copy to `<agent-dir>/subagents.json` |
| [amox-pi-sync.json](amox-pi-sync.json) | Copy to `<agent-dir>/amox-pi-sync.json`; fill private SSH URL and absolute checkout path |
| [routing.toml](routing.toml) | Copy to a stable local path and pass to the Task Router installer |
| [prompts/de-ai.md](prompts/de-ai.md) | Copy to `<agent-dir>/prompts/de-ai.md` and install the [de-ai Skill](../skills/de-ai/SKILL.md) |

## Interface

Deploy [settings.json](settings.json), [starline.json](starline.json), and [themes/catppuccin-mocha.json](themes/catppuccin-mocha.json) using the [interface steps](../setup_for_pi.md#interface) and [package order](../setup_for_pi.md#2-packages):

- `pi-tidy` enables `frameMessages: true`, right-aligns user messages (`userMessageAlign: "right"`) with `messageBorderColors.user: "syntaxKeyword"`, and omits `finalReplyStyle` so final replies use the package default.
- `pi-starline` renders Nerd Font pills, compact editor padding (`editorPaddingY: 0`), full working directory paths, automatic thinking colors, and a right-side `pi-sync` pill.
- Apply Catppuccin Mocha to both Pi and the active terminal profile following [appearance.md](appearance.md) ([简体中文](appearance.zh-CN.md)). Font installation (`Maple Mono NF CN`) and terminal background opacity (`95%`) stay with the user.

## Search routing

Deploy [web-search.json](web-search.json) with these routing settings:

| Key | Value and behavior |
| --- | --- |
| `searchRouting.providers` | `["exa", "openai"]` |
| `searchRouting.fallbackOn` | `["empty", "domain-miss", "unsupported", "transient", "quota", "network", "invalid-response"]` |
| `openaiSearchProviders` | `["sub2api-gpt-only"]` (registered in `sub2api.json`) |
| `openaiUseProviderBaseUrl` | `true`; builds `<relay baseURL>/v1/responses` and reuses Pi's resolved provider credential |
| `openaiSearchModel` | `"gpt-6.2-sol"`, independent of the active chat model |
| `openaiUseAlphaSearch` | `false` |
| `workflow` | `"none"` |

`exa` runs first because it requires no API key and returns bounded raw results, whereas the `openai` fallback runs a billed Responses turn through Sub2API. Explicit caller overrides such as `provider: "openai"` bypass `searchRouting` and hit the requested provider directly.

The fallback also handles an empty Exa result or one without any matches for the requested domain, alongside errors (`quota`, `network`, `invalid-response`, `unsupported`, `transient`). Do not add `off-topic`, which requires a Cloudflare Workers AI or typesafe judge model not configured here. Do not set `searchRouting.useCurrentModel`, which only accepts official OpenAI, ChatGPT Codex, or Azure endpoints.

Because `openaiUseProviderBaseUrl` reads the credential already resolved for `sub2api-gpt-only`, `web-search.json` stores neither an API key nor a duplicate relay URL.

> [!NOTE]
> Preserve unrelated fetch settings in existing `web-search.json` files. Obtain user approval before removing conflicting top-level `provider` or `searchProvider` keys or stripping `web_search` from `serverTools.responses` in `sub2api.json`; keep other hosted server tools intact. Live search tests also require explicit approval.

### Standalone API-key alternative

Use [read-sub2api-search-key.cjs](read-sub2api-search-key.cjs) only when the relay credential cannot be resolved through Pi's provider registry:

1. Set `openaiResponsesUrl` to the full `<relay baseURL>/v1/responses` URL, configure `openaiApiKey` to invoke the deployed helper script, and remove `openaiUseProviderBaseUrl`. An explicit `openaiResponsesUrl` takes precedence over a derived URL.
2. Place `read-sub2api-search-key.cjs` in the same directory as the deployed `sub2api.json`. It reads `sub2api-gpt-only.token` (or legacy `sub2api.token`) and resolves literal keys or `${ENV_VAR}` references.
3. If `sub2api.json` uses a command-backed token (`!...`), leave that provider untouched and ask the user for a separate `openaiApiKey` source.

> [!CAUTION]
> Never run `read-sub2api-search-key.cjs` directly in a logged or recorded terminal session: it writes the resolved secret to stdout.

## Related guides

- Install [Skills](../setup_for_pi.md#3-skills) and generate [Task Router roles](../setup_for_pi.md#5-task-router) via [setup_for_pi.md](../setup_for_pi.md).
- Configure manual session sync with [pi-sync-setup.md](pi-sync-setup.md) ([简体中文](pi-sync-setup.zh-CN.md)). Bootstrap never runs sync transfers.
- Keep real API keys, sessions, sync repositories, caches, and backups out of Git.
