# amox-agent-bootstrap — Pi

On Windows, macOS or Linux, configure this computer using these instructions and the [pi/ templates](pi/README.md). Read current upstream instructions, choose commands for the actual OS and verify the result.

## General rules

- Check before installing; reuse compatible software. Back up changed files and preserve unrelated packages, instructions and credentials.
- Respect `PI_CODING_AGENT_DIR` (default `~/.pi/agent`). Do not replace the whole agent directory or duplicate registrations.
- Use current unpinned user-level package sources; preserve each amox package's reviewed upstream dependency pins.
- Keep secrets, sessions, caches and backups out of Git and reports. Do not make paid model calls, launch agents or upload private files to verify setup.
- Missing credentials or models leave that component pending; continue independent steps and report the actual paths and blockers.

## 1. Runtime and Python

Reuse compatible Pi, Node.js, Git and shell installations. If needed, install the latest Pi using its [official instructions](https://github.com/earendil-works/pi); the npm alternative is `npm install -g --ignore-scripts @earendil-works/pi-coding-agent`. Current packages require Node >=22.19. Verify `pi --version` and supported Bash availability, including on Windows.

Find Conda through PATH, environment variables and common locations; install official Miniforge into a user-owned directory only if absent. Reuse the shared `codex` environment, or create it with Python 3.12. Use its interpreter for **all Python execution and dependencies**, never system Python, base or `pip --user`. Verify `pypdf` imports and install it only if missing. Install other dependencies only when required below.

## 2. Packages

Install these ten user-level packages through unversioned `pi install npm:<name>` sources, without `--local`. Keep [settings.json](pi/settings.json) order and preserve unrelated entries.

| Package | Purpose |
| --- | --- |
| `npm:@indexyz/pi-provider-sub2api` | Relay provider and model discovery |
| `npm:@narumitw/pi-btw` | Side conversation |
| `npm:pi-open-tui` | Terminal interface |
| `npm:@narumitw/pi-statusline` | Status line |
| `npm:@heyhuynhgiabuu/pi-pretty` | Tool/transcript presentation |
| `npm:@gfgghgftgffg/pi-web-access-lean` | `web_access` |
| `npm:@gfgghgftgffg/rpiv-todo-lean` | `todo` |
| `npm:@gfgghgftgffg/pi-subagents-lean` | `subagent` and native workflows |
| `npm:@monotykamary/pi-retry` | Retry and continuation |
| `npm:pi-sync-suite` | Manual session/mission sync |

Read the [amox README](https://github.com/gfgghgftgffg/amox_pi_extensions_lean) and package configuration requirements. All three packages are public on npm and require Pi >=1.1.0. Verify current npm `latest` metadata and host requirements; report authentication/network errors instead of treating them as package absence. Install without `@version`; later updates use `pi update --extensions`, which neither upgrades Pi nor schedules automatic updates. Normal installation needs no amox checkout, root `npm ci` or local installation scripts.

On an existing installation, obtain approval before source migration. Back up settings, identify exact old entries with `pi list`, remove only the replaced `@ssk_dev` or local facades using `pi remove <exact-source>`, then install the npm sources. Resolve local paths relative to their settings file before using the CLI from another directory. Do not delete old checkouts or prefixes just to unregister them. Keep one each of `web_access`, `todo` and `subagent`; do not separately load upstream engines or copy entrypoints into discovery directories. Preserve provider, UI, permissions and unrelated extensions. Restart Pi and report actual hook conflicts rather than removing packages silently.

## 3. Skills

Install complete Skills, including referenced resources, under `<agent-dir>/skills/`; reuse compatible copies without duplicates.

| Skill | Source / installation |
| --- | --- |
| `design-taste-frontend` | [taste-skill](https://github.com/Leonxlnx/taste-skill), primary `skills/taste-skill/` only |
| `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) |
| `meeting-summary-html` | [meeting-summary-html](https://github.com/gfgghgftgffg/meeting-summary-html), including preparation scripts |
| `shuorenhua` | [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) |
| `task-routing` | Generate through the Pi installer in section 5 |
| `grilling` | [source](https://github.com/mattpocock/skills/blob/main/docs/productivity/grilling.md), actual Skill at `skills/productivity/grilling/` |
| `ian-xiaohei-illustrations` | [Ian Xiaohei Illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations), inner `ian-xiaohei-illustrations/` directory with references, example assets and Ian attribution |

Set `disable-model-invocation: true` in `grilling`, `meeting-summary-html` and `ian-xiaohei-illustrations` frontmatter, including reused copies and after upstream updates. Keep them discoverable for explicit `/skill:<name>` invocation; do not add automatic interview instructions. Reuse a complete nested Xiaohei installation instead of creating a duplicate. Verify parsed `disableModelInvocation: true` and absence from the default startup Skill prompt; reload does not erase existing conversation context. Xiaohei image generation requires an actual supported host tool/model; installation alone does not prove generation works, and setup must not generate or upload images.

Run meeting preparation scripts with the `codex` interpreter. Text preparation needs no ASR key; media transcription needs `DASHSCOPE_API_KEY`, but verification must not upload media.

## 4. Configuration

Deploy files according to the [pi/ file map](pi/README.md). Merge template-owned settings while recursively preserving unrelated object keys; arrays use the requested template values except package entries retain unrelated registrations. Omit machine-generated `lastChangelogVersion`, version pins and sync timestamps. Use each package's npm source and remove superseded facade registrations with approval.

Keep the model/provider/thinking preferences in `settings.json`, `pi-btw.json` and `routing.toml`; do not substitute models when unavailable. Apply the full `subagents.json`; project `.pi/subagents.json` may override global defaults, so report effective differences. Do not migrate package-source patches or runtime records.

Apply `toolStyle: "claudecode"` from `pi-pretty.json`, preserving other preferences. Check `PRETTY_CONFIG_DIR` and the installed extension's path resolution: its default is `<home>/.pi/agent`, not automatically a custom `PI_CODING_AGENT_DIR`. Do not broaden file indexing. Restart Pi and check actual terminal compatibility; JSON parsing alone does not verify its private host-rendering APIs.

Preserve existing Sub2API credentials; otherwise leave `YOUR_API_KEY` in deployed `sub2api.json` and tell the user its absolute path and `sub2api.token` field to edit privately. Do not collect the token or enable paid priority modes. Check web provider credentials or supported keyless configuration separately; tool registration does not prove authenticated search. Keep retry defaults and inspect `/retry status` without causing failures or adding another scheduler.

Configure Pi Sync through its [dedicated guide](pi/pi-sync-setup.md) ([中文](pi/pi-sync-setup.zh-CN.md)). It requires the user's own private SSH repository and an absolute local checkout path. Preserve existing destinations. Keep manual mode, sessions/missions-only scope and `syncLocalPackagePaths: false`. Missing destination details leave it pending. Bootstrap must not run synchronization, `/sync-setup` or cleanup.

## 5. Task Router

Read the current [Task Router README](https://github.com/gfgghgftgffg/task-router) and [Pi adapter guide](https://github.com/gfgghgftgffg/task-router/blob/main/docs/pi.md). Use the amox `pi-subagents-lean` executor and `pi-web-access-lean` search facade, not old `@ssk_dev` packages. Verify installed metadata and schema without launching children.

Keep a maintained Router checkout and a working copy of [routing.toml](pi/routing.toml) in stable user-owned directories. Preserve its model choices and selection hints; do not replace them with upstream example defaults. From the Router checkout, use the actual absolute configuration path:

```text
npm ci
node cli.mjs doctor --host pi --config <absolute-routing-config>
node cli.mjs install --host pi --config <absolute-routing-config>
node cli.mjs install --host pi --config <absolute-routing-config> --apply
```

Respect `PI_CODING_AGENT_DIR` or use a matching `--pi-home`. The installer manages flat `agents/tr_*.md`, the complete `skills/task-routing/` and one `pi-task-router` AGENTS block. Preserve its backups and conflict protections; do not hand-edit generated files or mix Codex and Pi homes.

Check `/agents`, lean help and `pi --list-models` without dispatch. `doctor` is static; without verified host metadata, report model availability/thinking as unverified rather than inventing a catalog. Search-role selectors use `ext:pi-web-access-lean/web_access`, without the npm scope, and must not allow shell or mutation tools. Do not broaden project trust or disable discovery to force acceptance.

Restart Pi or `/reload` after installation. Routing is activated only by `/skill:task-routing`; installation does not authorize delegation. Its orchestrator preference does not replace the normal Pi default.

## 6. Global instructions

Use [pi/AGENTS.md](pi/AGENTS.md), not the Codex template. Render `{{CONDA_PATH}}` with the verified Conda executable and `{{PYTHON_PATH}}` with the `codex` interpreter. Respect effective context-file precedence, including `AGENTS.override.md`.

On a fresh installation deploy the rendered template; otherwise update its corresponding instruction sections while preserving unrelated instructions and exactly one installer-managed Router block. Report conflicts rather than overwriting newer managed content. Use `127.0.0.1:7897` only if that proxy exists and networking is slow or failing; do not set a permanent system proxy.

## 7. Verification and report

- Verify Pi, Node, Git, shell, the `codex` interpreter and a successful `pypdf` import.
- Check ten package declarations, actual installed versions/sources and startup diagnostics. Confirm one lean tool per name, no upstream duplicates and `/retry status`. Distinguish configured, installed and loaded.
- Verify seven complete Skills and the three explicit-only settings, including parsed flags and Xiaohei's absence from the startup Skill prompt. Run meeting preparation on a temporary local text fixture, without ASR or uploads.
- Parse deployed JSON and compare template-owned values without exposing secrets. Report effective main/BTW/subagent model settings, pi-pretty style/path, project overrides and any pending provider or Sync configuration.
- Verify generated Router roles, selectors, model/thinking policies and one AGENTS block. Keep static validation separate from live execution; no paid inference or delegation for setup.
- Check Pi Sync command registration and manual configuration without transfers. Verify repository privacy/access only through non-transfer checks; report anything not checked.
- Report each component as installed, reused, pending or failed, with effective paths, versions, source commits and restart requirements. Repeated setup must not duplicate registrations.
