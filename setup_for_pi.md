# amox-agent-bootstrap — Pi

Give this file or repository to Pi on a new computer and ask:

> Read setup_for_pi.md, configure this computer accordingly, verify the installation, and report the results.

This is a task brief for Windows, macOS, and Linux, based on the user's current Pi installation. Complete the setup rather than handing the user commands. Read current upstream instructions and choose commands for the actual OS, architecture, shell, and host version.

## General Approach

- Check before installing; reuse compatible installations. Avoid duplicate packages, Skills, roles, and instruction blocks.
- Back up files before editing. Preserve unrelated user instructions, packages, credentials, and configuration; do not replace a whole agent directory.
- Respect `PI_CODING_AGENT_DIR` (default `~/.pi/agent`) and each package's effective configuration paths.
- Install the latest npm releases and safely update maintained source checkouts; do not add user-level version pins. The amox wrappers pin their own reviewed upstream dependencies: retain those pins. Check compatibility and report unsupported features instead of silently changing the requested behavior.
- Keep secrets, sessions, caches, backups, and generated runtime records out of this repository and reports.
- Missing credentials or models must not block independent steps. Do not make paid model calls, upload private files, or launch agents merely to verify setup.
- Fetch the referenced [pi/ files](pi/README.md) from this repository if working from this document alone.

## 1. Pi, Conda, and Dependencies

Reuse compatible Pi, Node.js, Git, and shell installations. If Pi is absent, follow the [official installation instructions](https://github.com/earendil-works/pi). Install the latest release and verify its current requirements; Node.js 22.19 or newer is required by the current packages. The documented npm alternative is `npm install -g --ignore-scripts @earendil-works/pi-coding-agent`. Verify `pi --version` and the shell actually used by Pi, including supported Bash availability on Windows.

Find Conda through PATH, environment variables, and common installation locations. If missing, install the appropriate official Miniforge release into a user-owned directory and verify its download. Do not replace system Python.

Reuse the Conda environment `codex`, shared with Codex. Create it with Python 3.12 if absent; retain an existing compatible version. **Use this environment for all Python execution and dependencies**, never system Python, base, or `pip --user`. Use its interpreter for pip and scripts, for example `conda run -n codex python -m pip ...`.

Check that `pypdf` imports and install it only if missing. Install other dependencies only when required by the packages or Skills below, preferring Conda where supported or an official user-level installation.

## 2. Pi Packages

Configure these **10 user-level npm packages** through `pi install npm:<name>` without `--local` or version pins. This includes all three maintained amox lean extensions: npm is now the normal installation and update source. Keep the order in [pi/settings.json](pi/settings.json), preserving unrelated declarations. Do not also copy their entrypoints into extension discovery directories.

| Package source / identity | Purpose / source |
| --- | --- |
| `npm:@indexyz/pi-provider-sub2api` | Relay provider and model discovery; [source](https://github.com/5aaee9/pi-agent-extensions/tree/main/pi-provider-sub2api) |
| `npm:@narumitw/pi-btw` | Side conversation; [source](https://github.com/narumiruna/pi-extensions/tree/main/packages/pi-btw) |
| `npm:pi-open-tui` | Terminal interface; [source](https://github.com/OldSuns/pi-open-tui) |
| `npm:@narumitw/pi-statusline` | Status line; [source](https://github.com/narumiruna/pi-extensions/tree/main/packages/pi-statusline) |
| `npm:@heyhuynhgiabuu/pi-pretty` | Tool/transcript presentation; [source](https://github.com/buddingnewinsights/pi-pretty) |
| `npm:@gfgghgftgffg/pi-web-access-lean` | Search, fetch and source checking through `web_access`; [source](https://github.com/gfgghgftgffg/amox_pi_extensions_lean/tree/main/packages/pi-web-access-lean) |
| `npm:@gfgghgftgffg/rpiv-todo-lean` | Task tracking through `todo`; [source](https://github.com/gfgghgftgffg/amox_pi_extensions_lean/tree/main/packages/rpiv-todo-lean) |
| `npm:@gfgghgftgffg/pi-subagents-lean` | Subagents and native workflows through `subagent`; [source](https://github.com/gfgghgftgffg/amox_pi_extensions_lean/tree/main/packages/pi-subagents-lean) |
| `npm:@monotykamary/pi-retry` | Automatic retry and continuation; [source](https://github.com/monotykamary/pi-retry) |
| `npm:pi-sync-suite` | Manual session/mission sync; [source](https://github.com/MuratAitov/pi-sync) |

### Maintained Lean Packages and Migration

Read [amox_pi_extensions_lean](https://github.com/gfgghgftgffg/amox_pi_extensions_lean) and the three package READMEs. Requires Pi >=1.1.0, Node >=22.19.0, npm and Git. Verify each package's current npm `latest` metadata and host requirements, then install without a version suffix. Do not interpret authentication/network errors as package absence:

```text
pi install npm:@gfgghgftgffg/pi-web-access-lean
pi install npm:@gfgghgftgffg/rpiv-todo-lean
pi install npm:@gfgghgftgffg/pi-subagents-lean
```

A source checkout, root `npm ci` and the per-extension Git installation scripts are no longer needed for normal installation. The wrappers still pin their reviewed upstream engines; do not remove those internal dependency pins or register the engines separately.

For an existing setup, back up settings and inspect `pi list`. Remove each replaced facade with `pi remove <source>` using the actual npm declaration or the resolved absolute local package path. Local paths shown in settings are relative to that settings file; resolve them before calling the CLI from another directory. Include paths under `lean-packages` and any old `@ssk_dev` npm sources or version pins. Install or retain one unversioned maintained npm source for each facade. Preserve provider, UI, permissions and unrelated extensions; do not delete the old checkout or prefix just to unregister it. Complete migration before reloading so `subagent`, `web_access` and `todo` each load exactly once. Equivalent names from local and npm sources are not automatically deduplicated.

For later upgrades, use `pi update npm:@gfgghgftgffg/pi-web-access-lean` (and the corresponding todo/subagents commands), or `pi update --extensions` to update all configured extensions. Plain `pi update` updates Pi itself. Recheck runtime metadata/schema and Router compatibility after upgrades; retain the same routing configuration if regenerating Router files.

Use `pi list` and startup diagnostics to distinguish configured, installed, and loaded packages. Restart Pi after changes. UI/footer extensions may compete for host hooks; report actual conflicts rather than silently removing packages.

### Provider and Retry Setup

- Use [pi/sub2api.json](pi/sub2api.json) as the relay configuration template. Deploy it to `<agent-dir>/sub2api.json`, keeping `YOUR_API_KEY` as the placeholder unless a valid token already exists. Do not ask the user to send the key or fill it in yourself. In the final report, tell the user to edit the deployed file's `sub2api.token` themselves, giving its actual absolute path. Do not enable paid priority modes or hosted tools for setup.
- The lean web package exposes one `web_access` tool for search/check/fetch/get/help. Follow its current provider setup, reusing credentials or supported keyless paths. Tool registration alone does not prove authenticated search works. Do not install optional video/browser tools unless requested.
- `pi-retry` uses its defaults; this snapshot adds no `piRetry` overrides. It owns retries while loaded and disables the host's native retry scheduler. Check `/retry status` without intentionally failing model calls. Retries and output-limit auto-continuation may create additional billed turns; do not add another retry scheduler or test these with paid requests.

## 3. Skills

Install these **seven user Skills** into `<agent-dir>/skills/`, or reuse complete discoverable copies without duplicate registration. Include scripts, references, and assets, not just `SKILL.md`. Keep needed source checkouts in stable user-owned directories.

| User Skill | Source | Requirements |
| --- | --- | --- |
| `design-taste-frontend` | https://github.com/Leonxlnx/taste-skill | Install the primary Skill, currently `skills/taste-skill/`, using its frontmatter name. Optional variants are not requested. |
| `humanizer` | https://github.com/blader/humanizer | Include the full Skill and referenced resources. |
| `meeting-summary-html` | https://github.com/gfgghgftgffg/meeting-summary-html | Include `scripts/prepare_meeting_input.py` and references; run helpers with the `codex` interpreter. |
| `shuorenhua` | https://github.com/MrGeDiao/shuorenhua | Include the full Skill and reference files. |
| `task-routing` | https://github.com/gfgghgftgffg/task-router | Generate with the Pi installer in section 5, not a Codex bundle. |
| `grilling` | https://github.com/mattpocock/skills/blob/main/docs/productivity/grilling.md | Documentation URL; install the actual Skill, currently `skills/productivity/grilling/`. |
| `ian-xiaohei-illustrations` | https://github.com/helloianneo/ian-xiaohei-illustrations | Install the inner `ian-xiaohei-illustrations/` directory with `SKILL.md`, references and example assets; retain attribution to Ian and set `disable-model-invocation: true` for explicit-only use. |

After downloading or reusing `grilling`, `meeting-summary-html` and `ian-xiaohei-illustrations`, set `disable-model-invocation: true` in each installed `SKILL.md`, inside the opening `---` block. If the field already exists, set it to `true`. Reapply this local setting after upstream Skill updates. Invoke them explicitly with `/skill:grilling`, `/skill:meeting-summary-html` or `/skill:ian-xiaohei-illustrations`; do not add an automatic interview trigger or a replacement Skill inventory to AGENTS.md. Generated `task-routing` is also explicit-only.

For `ian-xiaohei-illustrations`, this excludes its name, description and path from Pi's default Skill prompt listing at startup; the full Skill text is loaded when its explicit command is invoked. Keep it installed and discoverable so that command still works. Verify the parsed flag and its absence from the rendered Skill prompt, not just the presence of the YAML line. Restart or reload after changes; already injected context is not retroactively removed from the current conversation.

Text meeting preparation requires no ASR key. Media transcription requires `DASHSCOPE_API_KEY`; report missing credentials without blocking text summaries, and do not upload media for verification.

Verify all seven intended Skills and their resources, allowing preserved unrelated Skills. Pi discovers nested Skill directories: reuse a complete existing `ian-xiaohei-illustrations/ian-xiaohei-illustrations/SKILL.md` layout rather than copying a second Skill beside it. For a fresh setup, copy only the inner Skill directory to `<agent-dir>/skills/ian-xiaohei-illustrations/`, with its references/assets and upstream attribution. The source instructions mention Codex's `image_gen`; Pi installation alone does not provide that tool. Use an actually supported host image-generation tool/model when needed, report unavailable generation separately from Skill installation, and do not generate or upload images merely to verify setup.

## 4. Fixed Settings and Plugin Configurations

Merge [pi/settings.json](pi/settings.json) into the effective global settings, preserving unrelated keys. All ten requested package entries are portable unversioned npm sources. Replace superseded local amox/old npm registrations by package identity, retain the template order and avoid duplicate facades. Apply these requested preferences:

- `defaultProvider`: `sub2api`
- `defaultModel`: `gpt-6.1-sol`
- `defaultThinkingLevel`: `medium`
- `enabledModels`: `["sub2api/*"]`
- `tuiMode`: `fullscreen`; `theme`: `dark`

Keep these personal defaults and report missing models/providers or unsupported thinking levels; do not substitute another model. Preserve other provider credentials even though `enabledModels` scopes model selection to Sub2API. Do not copy machine-generated `lastChangelogVersion` or a local version pin.

Back up and apply these fixed non-sensitive configurations. On a fresh installation copy them verbatim except for the Pi Sync repository and path substitutions described below; otherwise replace template-owned values while recursively preserving unrelated object keys. Arrays are complete requested values, not append-only lists, except existing Pi Sync scope conflicts require review rather than expansion.

| Fixed source | Effective target |
| --- | --- |
| [pi/open-tui.json](pi/open-tui.json) | `<agent-dir>/open-tui.json` |
| [pi/pi-btw.json](pi/pi-btw.json) | `<agent-dir>/pi-btw.json` |
| [pi/pi-pretty.json](pi/pi-pretty.json) | Effective pi-pretty config directory; set `toolStyle: "claudecode"`, preserving unrelated settings |
| [pi/subagents.json](pi/subagents.json) | `<agent-dir>/subagents.json` |
| [pi/sub2api.json](pi/sub2api.json) | `<agent-dir>/sub2api.json`; preserve existing credentials, otherwise leave `YOUR_API_KEY` for the user to edit |
| [pi/pi-sync-suite.json](pi/pi-sync-suite.json) | `<agent-dir>/pi-sync-suite.json`; supply the user's own private repository SSH URL, render the local checkout path, and follow the manual-only rules below |

For `sub2api.json`, `YOUR_API_KEY` is a placeholder, not a usable token. If it remains, report the provider as pending and tell the user to edit `sub2api.token` in the deployed file themselves. Continue independent setup steps without waiting for the key.

Apply the full [pi/subagents.json](pi/subagents.json) configuration. It combines this computer's global defaults and project-scoped preferences for use as global defaults on the new computer. Key settings include `maxConcurrent: 50` for direct background agents, `showModel: true` to display their effective model/thinking, `fallbackSubagent: "none"`, `strictAgentFiles: true`, and `workflowsEnabled: true`. `maxConcurrentForeground: 0` and `defaultMaxTurns: 0` mean unlimited. Project `.pi/subagents.json` overrides global fields; report effective differences. Restart Pi after configuration and role changes.

BTW selects `sub2api/gpt-6.1-sol` with `thinkingLevel: "medium"`; verify its selection separately from the main model. Keep the requested value and report any unsupported thinking level. No package-source patches or runtime evidence directories need migration.

### pi-pretty: Claude Code Tool Style

Install or update `npm:@heyhuynhgiabuu/pi-pretty` to its latest release, then merge [pi/pi-pretty.json](pi/pi-pretty.json). Set **`toolStyle: "claudecode"`**, replacing `default`; this is not the `theme` setting, and does not change the main Pi theme or model. Resolve `PRETTY_CONFIG_DIR` and the installed extension's path handling first: current pi-pretty 0.7.x defaults to `<home>/.pi/agent` (using `HOME` or the OS home directory), not automatically a custom `PI_CODING_AGENT_DIR`. With a custom Pi home, ensure the extension reads the intended config directory rather than writing a file it will ignore. Preserve other renderer, FFF and indicator preferences; do not enable broad home/root indexing. Restart Pi to apply this startup-read setting. The style uses private host rendering APIs, so check compatibility and actual terminal appearance separately from JSON parsing or SDK loading.

### Pi Sync: Manual Session/Mission Policy

Read the current [Pi Sync README](https://github.com/MuratAitov/pi-sync) and the dedicated [sessions repository setup guide](pi/pi-sync-setup.md) ([中文](pi/pi-sync-setup.zh-CN.md)). The extension is `npm:pi-sync-suite` (not `npm:pi-sync`); its file is `<agent-dir>/pi-sync-suite.json`.

**Every user must configure their own private sessions repository.** The template uses `git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git`; replace both names with the user's actual SSH destination. Do not use the bootstrap author's personal sessions repository, this bootstrap repository, or the extension source repository. Reuse a valid existing user destination without repointing it. For a fresh setup, request the user's intended repository URL if it cannot be found in existing configuration. If it is unavailable, keep Pi Sync pending configuration and continue independent setup; do not deploy a placeholder as a ready-to-use destination, invent a repository, or run sync commands. Creating a remote repository or changing SSH keys requires a separate user request.

For a fresh installation with a confirmed destination, render `{{SYNC_REPO_DIR}}` as the absolute `<agent-dir>/sync-suite-repo` path using JSON serialization (escape Windows backslashes), set the actual `repoUrl`, then deploy the full [pi/pi-sync-suite.json](pi/pi-sync-suite.json). On other computers use the same remote but each computer's own absolute local path. Check that a populated checkout belongs to that remote; do not reuse this project or an unrelated checkout. Preserve an existing `repoUrl`, `repoDir` and local sync timestamps; do not repoint or replace an existing checkout. Preserve unrelated settings and report scope conflicts rather than silently expanding an existing policy.

This snapshot deliberately uses `autoMode: "manual"`, disables all chat automation, environment prompts and automatic cleanup, and selects only `missions` and raw `sessions`. Empty `safeRootFiles`/`safeDirs` mean it does **not** sync settings, Skills or other default config paths. The `sessions` entry in `dangerouslyAllowedNames` is the explicit exception to `neverSyncNames`; leave other sensitive-name exclusions intact. Raw sessions and missions can contain prompts, tool output, paths and secrets: confirm the destination is a private repository the user controls before any later explicit sync. Bootstrap must not run `/sync-setup`, `/sync-push`, `/sync-pull`, cleanup or remote/session tests. `/sync-setup` defaults to full-auto and performs an initial pull and push, so it is not an inert setup command.

Keep `syncLocalPackagePaths: false`. The maintained lean packages now use portable npm declarations; install them from npm on each computer rather than syncing local package directories. Do not include sync timestamps, repository contents, session files or backups in bootstrap Git. Verify config parsing and command registration without executing synchronization; report SSH access or remote privacy as unverified if not checked independently.

## 5. Task Router for Pi

Read the current [Task Router README](https://github.com/gfgghgftgffg/task-router) and [Pi adapter documentation](https://github.com/gfgghgftgffg/task-router/blob/main/docs/pi.md). Its executor is **`@gfgghgftgffg/pi-subagents-lean` from amox_pi_extensions_lean over `@tintinweb/pi-subagents`**; search uses **`@gfgghgftgffg/pi-web-access-lean`**. Install those maintained npm facades first, not old local amox paths or `@ssk_dev` packages. The Router's recorded review baseline may predate the current npm release; do not treat that baseline as an install pin or proof of live execution. Verify the actual installed package/dependency versions and help/schema when updating.

Keep the source checkout and a working copy of [pi/routing.toml](pi/routing.toml) in a stable user-owned directory. Safely update the Router checkout to the current maintained source before installation, preserving local changes. Keep the existing `routing.toml` model choices: the repository's example defaults are not a migration target. The bootstrap configuration records the installed role-map models, selection hints, 30 requested concurrent children, and five repair follow-ups. Verify `glm-5.3`, `deepseek-flash`, `gpt-6.1-sol`, and `gpt-6-astra` and their exact Pi thinking support without paid generation. Omitted providers inherit the actual parent provider; do not rely on fuzzy matching, provider fallback, or clamping.

From the Router checkout, use the actual absolute configuration path:

```text
npm ci
node cli.mjs doctor --host pi --config <absolute-routing-config>
node cli.mjs install --host pi --config <absolute-routing-config>
node cli.mjs install --host pi --config <absolute-routing-config> --apply
```

Respect `PI_CODING_AGENT_DIR`, or pass a matching `--pi-home`. Preserve installer backups, manifests, and conflict protections. The installer generates **flat `agents/tr_*.md`**, the complete `skills/task-routing/`, and one `pi-task-router` AGENTS block. It handles previously managed layouts through its manifest; do not bypass conflicts or hand-edit generated files. Keep Codex and Pi homes separate.

Generated roles deliberately do not pin model/thinking in frontmatter: the role map is authoritative. Every fresh direct launch must supply exact `model: "provider/id"` and separate `thinking` in the lean tool's JSON input; native workflow `agent()` uses `agentType`, `model`, and `effort`. Do not append a thinking suffix to the model ID. Project role overrides may change effective tools or lock model fields, so check them before dispatch. Replaced child prompts do not inherit AGENTS.md: the parent must supply applicable instructions in the brief.

Use `/agents` and `subagent({ op: "help", input: "run" })` to inspect loaded types and schema without launching children. Use `pi --list-models` for available IDs; it does not prove thinking support. `doctor` is offline/static: without a verified credential-free registry snapshot, model availability and thinking remain `UNVERIFIED`. Supply `--catalog` only from actual host metadata, never a fabricated list. Confirm search-role selectors expose `ext:pi-web-access-lean/web_access` and prohibit shell/mutation tools. Selectors use the unscoped short package name even though runtime packages now use `@gfgghgftgffg`; do not add the scope to the selector. Registration in the parent alone is not proof of child loading. Engine 0.22.0 discovers agents/workflows declared by installed packages by default; inspect actual role definitions, sources, project overrides and trust. Do not turn off discovery or broaden trust silently.

Task Router can use direct subagents or **lean's native `subagent` operation `workflow`**, selected by stage decision structure rather than agent count. Native workflows use `agent()/parallel()/pipeline()` and run in the background. Their host concurrency cap is independent of direct background agents' `maxConcurrent: 50` pool; the Router's own maximum and stricter host limits still apply. In the reviewed 0.22.0 engine, workflow `effort` does not accept `off`; report unsupported routes instead of silently dropping or changing thinking.

Restart Pi or `/reload` after installing roles, then activate only when requested with `/skill:task-routing`. Installation does not authorize delegation. Pi's `-p` is print mode, not a profile flag. The Router's recommended orchestrator (`gpt-6-astra`, `medium`) does not change the normal Pi default (`gpt-6.1-sol`, `medium`).

## 6. Fixed Global AGENTS.md

Use [pi/AGENTS.md](pi/AGENTS.md), not the Codex [templates/AGENTS.md](templates/AGENTS.md). Substitute only these verified absolute paths:

- `{{CONDA_PATH}}`: Conda executable.
- `{{PYTHON_PATH}}`: the `codex` environment's Python interpreter.

Check effective global context-file precedence, including `AGENTS.override.md`. On a fresh installation render the template verbatim after dependencies and Router installation. Otherwise back up and update corresponding quality, Python, proxy, Requirement Alignment, Workflow, and router entries, preserving unrelated instructions and exactly one Pi router block. Do not paraphrase or add a Skill inventory or automatic interview rule.

Retain installer-managed block protections. If a newer Router changes its policy block, report the discrepancy rather than blindly overwriting it. Do not render unresolved paths or claim missing dependencies are installed. Use the recorded proxy `127.0.0.1:7897` only when available and network access is failing or slow; do not force a permanent system proxy.

## 7. Verification and Report

1. Verify Pi, Node, Git, shell, and the `codex` interpreter with a successful `pypdf` import.
2. Verify all 10 package declarations, resources, actual amox package identities/dependency versions and startup diagnostics, including exactly one each of the lean `subagent`, `web_access`, and `todo` tools and `/retry status`. Check for duplicate facades; distinguish installed from loaded. Use the Router's optional `scripts/check-pi-runtime.mjs` with trusted installed Pi SDK/subagents/web package directories for offline schema, discovery and scope checks; it does not prove live model execution.
3. Verify seven user Skills with resources, including the references and example assets for `ian-xiaohei-illustrations`, with only one discoverable copy. Confirm `grilling`, `meeting-summary-html` and `ian-xiaohei-illustrations` have parsed `disableModelInvocation: true` from `disable-model-invocation: true`, and remain discoverable for explicit Skill commands. Confirm `ian-xiaohei-illustrations` is absent from the default rendered Skill prompt listing, without generating an image or invoking a model. Do not confuse image-planning instructions with verified image-generation capability.
4. Run the meeting preparation helper on a temporary local text fixture without ASR or uploads.
5. Parse deployed JSON and compare template-owned values with [pi/](pi/README.md), excluding real credential values from comparisons and reports. If the Sub2API token remains `YOUR_API_KEY`, report it as pending and give the user the deployed file's absolute path and the `sub2api.token` field to edit; do not collect or populate the key. Verify subagent concurrency, model display, fallback/strict-file/workflow settings and both main-model and BTW `medium` thinking. Verify pi-pretty resolves `toolStyle: "claudecode"` from its effective configuration while preserving unrelated preferences; report any host rendering incompatibility. Distinguish saved defaults, model metadata, and live operation.
6. Verify flat Router roles, their references and tool selectors, exact model/thinking policies, and one Pi AGENTS block. Distinguish static `doctor` success from runtime support; do not dispatch children or paid inference merely for verification.
7. Verify Pi Sync config parsing and the four `/sync-*` commands without running synchronization. Confirm the user supplied their own private repository SSH URL (no repository-name or checkout-path placeholders), manual mode, only missions/sessions in scope, no copied timestamps, and local-package syncing disabled. Preserve an existing remote/checkout and report any policy or SSH/privacy uncertainty. If the destination is missing, report Pi Sync as pending configuration and give the user the target configuration file path and `repoUrl`/`repoDir` fields to complete; do not claim sync readiness.
8. Compare global instructions with the rendered template; check no unresolved placeholders, duplicate blocks, or automatic interview trigger. Preserve unrelated instructions and confirm repeated setup does not duplicate registrations.

Report each item as newly installed, reused, pending configuration, or failed, including effective paths, installed versions, source commits, saved defaults, and restart/activation requirements. Give concrete blockers and next steps. Do not describe static checks or partial setup as full operational success.
