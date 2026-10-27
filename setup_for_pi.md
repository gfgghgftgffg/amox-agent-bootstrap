# Pi setup

Configure Pi on Windows, macOS or Linux using the [pi/ templates](pi/README.md). Respect `PI_CODING_AGENT_DIR` (default `~/.pi/agent`), back up changed files and preserve unrelated settings and credentials. Use unpinned user-level package sources. Do not make paid model calls, launch agents or transfer private data for setup checks.

## 1. Runtime and Python

- Reuse compatible Pi, Node.js, Git and Bash. Install Pi using its [official instructions](https://github.com/earendil-works/pi) if absent. Current packages require Node >=22.19; tidy's bash/write previews require Pi >=1.3. Check current package requirements.
- Reuse Conda, or install official Miniforge in a user-owned directory.
- Reuse the `codex` environment, or create it with Python 3.12. Use its interpreter for all Python scripts and dependencies, not system Python, base or `pip --user`.
- Install `pypdf` if absent and verify its import.

## 2. Packages

Install these nine packages with `pi install npm:<name>`, without `--local` or version pins. Keep the order in [settings.json](pi/settings.json), placing starline last after preserved unrelated packages.

| Package | Purpose |
| --- | --- |
| `npm:@indexyz/pi-provider-sub2api` | Relay provider and model discovery |
| `npm:@narumitw/pi-btw` | Side conversation |
| `npm:@gfgghgftgffg/pi-web-access-lean` | `web_access` |
| `npm:@gfgghgftgffg/rpiv-todo-lean` | `todo` |
| `npm:@gfgghgftgffg/pi-subagents-lean` | `subagent` and native workflows |
| `npm:@monotykamary/pi-retry` | Retry and continuation |
| `npm:pi-sync-suite` | Manual session/mission sync |
| `npm:pi-tidy` | Tool folding and diff presentation |
| `npm:pi-starline` | Editor, user messages and pill footer |

This setup replaces `@heyhuynhgiabuu/pi-pretty`, `pi-open-tui` and `@narumitw/pi-statusline`. Back up settings, remove those confirmed old packages with `pi remove <actual-source>`, and preserve their preference files. Leave unrelated extensions unchanged.

Read the [amox package instructions](https://github.com/gfgghgftgffg/amox_pi_extensions_lean). For existing `@ssk_dev` or local facades, obtain approval before source migration and remove only the replaced registrations. Keep one tool per name; do not separately load upstream engines. Normal npm installation needs no amox checkout. Update packages later with `pi update --extensions`.

## 3. Skills

Install complete Skills, including scripts, references and assets, under `<agent-dir>/skills/`. Reuse existing copies without duplicates.

| Skill | Source / installation |
| --- | --- |
| `design-taste-frontend` | [taste-skill](https://github.com/Leonxlnx/taste-skill), only `skills/taste-skill/` |
| `create-readme` | [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/create-readme), only `skills/create-readme/`, not the whole collection |
| `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) |
| `meeting-summary-html` | [meeting-summary-html](https://github.com/gfgghgftgffg/meeting-summary-html), including preparation scripts |
| `shuorenhua` | [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) |
| `task-routing` | Generate through the installer in section 5 |
| `grilling` | [source](https://github.com/mattpocock/skills/blob/main/docs/productivity/grilling.md), actual Skill at `skills/productivity/grilling/` |
| `ian-xiaohei-illustrations` | [source](https://github.com/helloianneo/ian-xiaohei-illustrations), inner `ian-xiaohei-illustrations/` with references, assets and attribution |

Set `disable-model-invocation: true` in `grilling`, `meeting-summary-html` and `ian-xiaohei-illustrations`, including reused copies. Keep them available for explicit invocation; do not add automatic interview instructions.

For `create-readme`, preserve its short description and leave `disable-model-invocation` absent or `false`. Pi loads its full instructions on demand. Use it for README structure, then `humanizer` or `shuorenhua` for prose. Keep current introduction, usage and required deployment/maintenance instructions; link detailed configuration rather than duplicating it. Keep history and troubleshooting narratives out of README.

Run meeting preparation with the `codex` interpreter. Text needs no ASR key; media transcription requires `DASHSCOPE_API_KEY`. Leave transcription/image generation pending if credentials or supported tools are unavailable.

## 4. Configuration

Deploy the [file map](pi/README.md). Merge template-owned values while preserving unrelated object keys. Preserve unrelated package registrations and tool choices; do not copy machine-generated changelog versions or sync timestamps.

### Main settings

Apply [settings.json](pi/settings.json), [pi-btw.json](pi/pi-btw.json) and [subagents.json](pi/subagents.json):

- Keep the specified provider, model and thinking preferences; report unavailable models without substitution.
- Enable codemode with `defaultTools: ["+codemode"]`, retaining existing tools and the default `codemode.mode: "on"`.
- Set `hideThinkingBlock: true` and `theme: "catppuccin-mocha"`.
- Apply the full subagent template and report project-level overrides.

### Interface

Deploy [starline.json](pi/starline.json) and [themes/catppuccin-mocha.json](pi/themes/catppuccin-mocha.json) to the same relative paths under `<agent-dir>` before selecting the theme.

- Tidy: message frames on, `frameUserMessages: false`; other features use upstream defaults.
- Theme: keep `toolSuccessBg: "base"` for red/green diff backgrounds.
- Starline: Nerd Font icons, Mocha pastel pills, `editorPaddingY: 0`, `editorMetadataFormat: ""`.
- Keep `colors.thinking` absent for automatic thinking-level colors; remove an existing fixed override.
- Directory: `pathDisplay: { "mode": "full", "depth": 0 }`.
- Pill order: model, thinking, subagents, cwd, sessionName, runtime, git, context, cost, sessionDuration, time, extensionStatus.
- Queue pill off, leaving Pi's native pending-message text visible. `/starline queue` opens queue details from the keyboard.

Apply **Catppuccin Mocha to both Pi and the current terminal** using the [appearance guide](pi/appearance.md) ([中文](pi/appearance.zh-CN.md)). Deploy the Pi theme, detect the actual terminal, back up its configuration, and import/select the official Mocha scheme for the active profile. Preserve unrelated settings. Registering a scheme without selecting it is not complete. If the terminal cannot be configured from this host, report terminal theme as pending, not complete.

Font installation and opacity remain user-managed: **Maple Mono NF CN**, **95% opacity**. Bootstrap must not install fonts, write font registry entries or copy machine-specific terminal paths.

### Provider, search and sync

- Deploy [sub2api.json](pi/sub2api.json), preserving existing credentials. If absent, leave `YOUR_API_KEY` and tell the user the local file and `sub2api.token` field to edit privately.
- Deploy [web-search.json](pi/web-search.json) and its credential helper using the [search routing instructions](pi/README.md#search-routing): Sub2API/OpenAI first, Exa fallback. Render the helper path and relay endpoint; preserve unrelated fetch settings. Resolve conflicting provider overrides/native search injection with approval.
- Deploy [Pi Sync](pi/pi-sync-setup.md) ([中文](pi/pi-sync-setup.zh-CN.md)) using the user's private SSH repository and absolute checkout path. Keep manual mode, sessions/missions-only scope and `syncLocalPackagePaths: false`. Leave missing destinations pending. Do not run sync, `/sync-setup` or cleanup during bootstrap.
- Keep retry defaults and inspect `/retry status`.

## 5. Task Router

Read the current [Router README](https://github.com/gfgghgftgffg/task-router) and [Pi adapter guide](https://github.com/gfgghgftgffg/task-router/blob/main/docs/pi.md). Keep a stable checkout and working copy of [routing.toml](pi/routing.toml), preserving its model choices.

From the Router checkout, use the actual absolute configuration path:

```text
npm ci
node cli.mjs doctor --host pi --config <absolute-routing-config>
node cli.mjs install --host pi --config <absolute-routing-config>
node cli.mjs install --host pi --config <absolute-routing-config> --apply
```

Respect `PI_CODING_AGENT_DIR` or pass a matching `--pi-home`. Let the installer generate `agents/tr_*.md`, `skills/task-routing/` and one managed AGENTS block. Preserve its backups and conflict protections.

Use the lean executor and `ext:pi-web-access-lean/web_access` search selector. Verify roles/model settings without dispatch. Routing activates only through `/skill:task-routing` or an explicit instruction, not merely by installation.

## 6. Global instructions

Deploy [pi/AGENTS.md](pi/AGENTS.md), substituting verified `{{CONDA_PATH}}` and `{{PYTHON_PATH}}`. On existing installations, update the corresponding sections while preserving unrelated instructions and exactly one Router block. Respect `AGENTS.override.md`. Use the optional `127.0.0.1:7897` proxy only if it exists and networking needs it.

## 7. Verification

- Verify Pi, Node, Git, Bash, the `codex` interpreter and `pypdf`.
- Check the nine packages and their order; confirm removed UI packages are no longer registered. Keep one lean tool per name.
- Verify eight complete Skills, the three explicit-only flags and automatically available `create-readme`. Test meeting preparation on a temporary local text fixture.
- Parse deployed JSON and check template values, rendered paths, Router roles and model settings without paid calls or delegation.
- Restart Pi; check tidy diffs, starline layout and native queue text. Keep Pi Sync manual and its status panel unchanged.
- Verify Pi's `catppuccin-mocha` theme and the active terminal profile's Catppuccin Mocha scheme separately. Report both states; applying only the Pi theme does not complete theme setup.
- Report installed/reused/pending/failed items, effective paths and restart requirements. Font installation and opacity remain user-managed.

Repository checks: `node --test tests/*.test.cjs`.
