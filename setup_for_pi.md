# Pi setup

Configure Pi on Windows, macOS or Linux using the [pi/ templates](pi/README.md). Respect `PI_CODING_AGENT_DIR` (default `~/.pi/agent`), back up changed files and preserve unrelated settings and credentials. Use unpinned user-level package sources. Do not make paid model calls, launch agents or transfer private data for setup checks.

## 1. Runtime and Python

- Reuse compatible Pi, Node.js, Git and Bash. Install Pi using its [official instructions](https://github.com/earendil-works/pi) if absent. Current packages require Node >=22.19; tidy's bash/write previews require Pi >=1.3. Check current package requirements.
- Reuse Conda, or install official Miniforge in a user-owned directory.
- Reuse the `codex` environment, or create it with Python 3.12. Use its interpreter for all Python scripts and dependencies, not system Python, base or `pip --user`.
- Install `pypdf` if absent and verify its import.

## 2. Packages

Install the following packages with `pi install npm:<name>`, without `--local` or version pins. Keep the order in [settings.json](pi/settings.json), placing starline last after preserved unrelated packages.

| Package | Purpose |
| --- | --- |
| `npm:@indexyz/pi-provider-sub2api` | Relay provider and model discovery |
| `npm:@narumitw/pi-btw` | Side conversation |
| `npm:@gfgghgftgffg/pi-web-access-lean` | `web_access` |
| `npm:@gfgghgftgffg/rpiv-todo-lean` | `todo` |
| `npm:@gfgghgftgffg/pi-subagents-lean` | `subagent` and native workflows |
| `npm:@monotykamary/pi-retry` | Retry and continuation |
| `npm:pi-sync-suite` | Manual session/mission sync |
| `npm:pi-autoresearch` | Autonomous experiment loop; disable bundled Skill discovery with `skills: []` |
| `npm:pi-tidy` | Tool folding and diff presentation |
| `npm:pi-starline` | Editor, user messages and pill footer |

This setup replaces `@heyhuynhgiabuu/pi-pretty`, `pi-open-tui` and `@narumitw/pi-statusline`. Back up settings, remove those confirmed old packages with `pi remove <actual-source>`, and preserve their preference files. Leave unrelated extensions unchanged.

Read the [amox package instructions](https://github.com/gfgghgftgffg/amox_pi_extensions_lean). For existing `@ssk_dev` or local facades, obtain approval before source migration and remove only the replaced registrations. Keep one tool per name; do not separately load upstream engines. Normal npm installation needs no amox checkout. Update packages later with `pi update --extensions`.

## 3. Skills

Install complete Skills, including scripts, references and assets, under `<agent-dir>/skills/`. Reuse existing copies without duplicates.

| Skill | Source / installation |
| --- | --- |
| `design-taste-frontend` | [taste-skill](https://github.com/Leonxlnx/taste-skill), only `skills/taste-skill/` |
| `create-readme` | [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/create-readme), only `skills/create-readme/` |
| `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) |
| `anti-defensive-writing` | [Kiterlin/anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing), install only the root `SKILL.md` and license |
| `meeting-summary-html` | [meeting-summary-html](https://github.com/gfgghgftgffg/meeting-summary-html), including preparation scripts |
| `task-routing` | Generate through the installer in section 5 |
| `autoresearch-create` | Render an explicit-only wrapper; see below |
| `autoresearch-finalize` | Render an explicit-only wrapper; see below |
| `autoresearch-hooks` | Render an explicit-only wrapper; see below |
| `grilling` | [source](https://github.com/mattpocock/skills/blob/main/docs/productivity/grilling.md), actual Skill at `skills/productivity/grilling/` |
| `ian-xiaohei-illustrations` | [source](https://github.com/helloianneo/ian-xiaohei-illustrations), inner `ian-xiaohei-illustrations/` with references, assets and attribution |

Set `disable-model-invocation: true` in `anti-defensive-writing`, `grilling`, `meeting-summary-html` and `ian-xiaohei-illustrations`, including reused copies.

Leave `disable-model-invocation` absent or `false` in `create-readme`, `design-taste-frontend` and `humanizer`.

Media transcription for `meeting-summary-html` requires `DASHSCOPE_API_KEY`; text preparation requires no ASR key.

### Autoresearch Skills

Keep the `pi-autoresearch` package entry in object form with `skills: []` as in [settings.json](pi/settings.json). Load its extension, but expose its three Skills only through explicit-only wrappers.

For each of `autoresearch-create`, `autoresearch-finalize` and `autoresearch-hooks`, render [autoresearch-skill.md](pi/autoresearch-skill.md) to `<agent-dir>/skills/<name>/SKILL.md`. Replace `{{SKILL_NAME}}` with that name and `{{UPSTREAM_SKILL_PATH}}` with the verified absolute path to `skills/<name>/SKILL.md` in the installed `pi-autoresearch` package. For managed npm installs the package normally lives at `<agent-dir>/npm/node_modules/pi-autoresearch`; verify rather than copying another host's path. Keep `disable-model-invocation: true` and preserve unrelated custom instructions in reused wrappers.

The wrappers read upstream files from the installed package, so package updates also update their workflows. Do not edit the npm Skill files directly.

The extension registers `/autoresearch` independently of Skill discovery. The wrappers keep the original Skill names available to explicit `/skill:` calls and the extension's internal calls, while `disable-model-invocation: true` hides them from automatic model selection.

| Bundled Skill | Purpose |
| --- | --- |
| `autoresearch-create` | Define the objective, metric, commands and scope; prepare session files and begin experiments |
| `autoresearch-finalize` | Organize kept experiments into reviewable branches |
| `autoresearch-hooks` | Author optional before/after iteration hooks, such as notifications or research fetching |

Use `/autoresearch <goal>` to activate experiment mode and start setup, or resume when `.auto/prompt.md` exists. Use `/autoresearch dashboard` to inspect results, `/autoresearch off` to stop while preserving records, and `/autoresearch finalize` to stop the mode before loading the finalize Skill. Do not substitute direct `/skill:autoresearch-create` or `/skill:autoresearch-finalize` calls for these lifecycle commands: the Skill calls alone do not activate or stop experiment mode. Invoke `/skill:autoresearch-hooks <request>` explicitly when hook configuration is needed.

Do not start a loop, run benchmarks or create/revert commits during bootstrap checks.

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
- Queue pill off, leaving Pi's native pending-message text visible.

Apply **Catppuccin Mocha to both Pi and the current terminal** using the [appearance guide](pi/appearance.md) ([中文](pi/appearance.zh-CN.md)). Deploy the Pi theme, detect the actual terminal, back up its configuration, and import/select the official Mocha scheme for the active profile. Preserve unrelated settings. Registering a scheme without selecting it is not complete. If the terminal cannot be configured from this host, report terminal theme as pending, not complete.

Font installation and opacity remain user-managed: **Maple Mono NF CN**, **95% opacity**.

### Provider, search and sync

- Deploy [sub2api.json](pi/sub2api.json), preserving existing credentials. If absent, leave `YOUR_API_KEY` and tell the user the local file and `sub2api.token` field to edit privately.
- Deploy [web-search.json](pi/web-search.json) and its credential helper using the [search routing instructions](pi/README.md#search-routing): Sub2API/OpenAI first, Exa fallback. Render the helper path and relay endpoint; preserve unrelated fetch settings. Resolve conflicting provider overrides/native search injection with approval.
- Deploy [Pi Sync](pi/pi-sync-setup.md) ([中文](pi/pi-sync-setup.zh-CN.md)) using the user's private SSH repository and absolute checkout path. Keep manual mode, sessions/missions-only scope and `syncLocalPackagePaths: false`. Leave missing destinations pending. Do not run sync, `/sync-setup` or cleanup during bootstrap.
- Keep retry defaults and inspect `/retry status`.

## 5. Task Router

Read the current [Router README](https://github.com/gfgghgftgffg/task-router) and [Pi adapter guide](https://github.com/gfgghgftgffg/task-router/blob/main/docs/pi.md). Keep a stable checkout and working copy of [routing.toml](pi/routing.toml), preserving its model choices.

Use `<router-checkout>/AGENTS.md` as the single shared rule file read by all Router parents and roles. Keep environment requirements in shared rules portable: use the local Conda `codex` environment and resolve executable/interpreter paths before use. Do not copy personal absolute paths or unresolved placeholders from the [Pi global instruction template](pi/AGENTS.md); only the deployed host-global file needs rendered local paths. On existing setups, preserve independently edited shared rules and merge only requested changes; do not reset the file on reruns. It is a separate editable copy, not a continuing mirror of global instructions. Generated roles reference its absolute path, so moving the checkout requires reinstalling Router. Do not replace it with another machine's unrendered paths.

From the Router checkout, use the actual absolute configuration path:

```text
npm ci
node cli.mjs doctor --host pi --config <absolute-routing-config>
node cli.mjs install --host pi --config <absolute-routing-config>
node cli.mjs install --host pi --config <absolute-routing-config> --apply
```

Respect `PI_CODING_AGENT_DIR` or pass a matching `--pi-home`. Let the installer generate `agents/tr_*.md` and `skills/task-routing/`. Preserve its backups and conflict protections. Pi Router installation does not modify global `AGENTS.md` or add a managed Router block.

Use the lean executor and `ext:pi-web-access-lean/web_access` search selector. All generated Pi roles must have `skills: true`, `allowed_subagents: none`, `prompt_mode: replace` and `inherit_context: false`, plus `ext:builtin:codemode/codemode` in their tool selectors. Skills load on demand; codemode can call only the role's existing permitted tools. Keep mutation limits, denied delegation tools and permission hooks unchanged. Verify the shared-file instruction, role/model settings and tool scope without dispatch. Routing activates only through `/skill:task-routing` or an explicit instruction, not merely by installation.

## 6. Global instructions

Deploy [pi/AGENTS.md](pi/AGENTS.md), substituting verified `{{CONDA_PATH}}` and `{{PYTHON_PATH}}`. On existing installations, update the corresponding sections while preserving unrelated instructions. Do not add a Router block; remove an existing `pi-task-router:start/end` block when applying this setup, preserving all surrounding text. Respect `AGENTS.override.md`. Use the optional `127.0.0.1:7897` proxy only if it exists and networking needs it.

## 7. Verification

- Verify Pi, Node, Git, Bash, the `codex` interpreter and `pypdf`.
- Check the packages in `settings.json` and their order; confirm removed UI packages are no longer registered. Keep one lean tool per name.
- Verify the listed Skills, their required resources and invocation flags. Verify only one installed `anti-defensive-writing/SKILL.md`. Test meeting preparation on a temporary local text fixture.
- Verify the three autoresearch wrappers are explicit-only, point to existing installed upstream Skills and retain original relative-reference resolution. Confirm the package has `skills: []`, no duplicate autoresearch Skills are loaded and no experiment loop was started.
- Verify Router's shared `AGENTS.md` has portable environment requirements, no personal paths or unresolved placeholders, and the roles reference it; check `skills: true`, codemode selection, unchanged role permissions and no global Pi Router block.
- Parse deployed JSON and check template values, rendered paths, Router roles and model settings without paid calls or delegation.
- Restart Pi; check tidy diffs, starline layout and native queue text.
- Verify Pi's `catppuccin-mocha` theme and the active terminal profile's Catppuccin Mocha scheme separately. Report both states; applying only the Pi theme does not complete theme setup.
- Report installed/reused/pending/failed items, effective paths and restart requirements.

Repository checks: `node --test tests/*.test.cjs`.
