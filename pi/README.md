# Pi configuration files

These files capture the current personal Pi configuration without credentials or runtime history. Follow [../setup_for_pi.md](../setup_for_pi.md), not a blind copy of this directory.

| Repository file | Installation target |
| --- | --- |
| [AGENTS.md](AGENTS.md) | `<agent-dir>/AGENTS.md`, after substituting verified Conda/Python paths |
| [settings.json](settings.json) | Merge into `<agent-dir>/settings.json`; omit machine-generated `lastChangelogVersion` |
| [sub2api.json](sub2api.json) | `<agent-dir>/sub2api.json`; preserve existing credentials, otherwise leave `YOUR_API_KEY` and report the file path for the user to edit |
| [open-tui.json](open-tui.json) | `<agent-dir>/open-tui.json` |
| [pi-btw.json](pi-btw.json) | `<agent-dir>/pi-btw.json` |
| [subagents.json](subagents.json) | `<agent-dir>/subagents.json`; 50 background slots, model display, strict role dispatch, and native lean workflows |
| [pi-sync-suite.json](pi-sync-suite.json) | `<agent-dir>/pi-sync-suite.json`; replace the SSH URL placeholders with the user's own private sessions repository and render `{{SYNC_REPO_DIR}}` as an absolute local path; preserve an existing destination |
| [routing.toml](routing.toml) | Stable Task Router source configuration passed with `--config`; do not copy generated agents from another host |

`<agent-dir>` is `PI_CODING_AGENT_DIR`, otherwise `~/.pi/agent`.

JSON plugin configurations capture this computer's non-sensitive preferences. The subagent template merges global defaults with the preferences saved by the agent UI in `~/.pi/subagents.json`, deploying them as global defaults on new computers. Seven package entries are unversioned npm sources; three are local amox lean package directories created by the repository installer, not npm packages. Their relative paths assume the default `~/.pi/agent` and `~/.pi/lean-packages` layout. For a custom agent directory, retain the installer's actual registered paths instead of blindly copying these relative entries. The AGENTS template has two local path placeholders and the current Router-managed policy. The router configuration matches this computer's role-map model choices; updating dependency sources must not replace those choices with the Router repository's example defaults.

Skill installation and the required `disable-model-invocation: true` setting are covered in [setup_for_pi.md](../setup_for_pi.md). Neither global AGENTS template automatically triggers a grilling interview.

Install the three lean subagent/web/todo facades from [amox_pi_extensions_lean](https://github.com/gfgghgftgffg/amox_pi_extensions_lean) with its per-extension scripts; do not install the workspace root or separately load upstream engines. Replace the old `@ssk_dev` registrations rather than appending duplicates. Task Router uses flat `agents/tr_*.md` and the lean `web_access` tool; generate roles with the current [task-router](https://github.com/gfgghgftgffg/task-router) Pi installer.

The Pi Sync template contains **placeholder repository details**, not a usable shared destination. Each user must configure their own private sessions repository and local checkout path; follow the separate [English guide](pi-sync-setup.md) or [中文说明](pi-sync-setup.zh-CN.md). Do not use the bootstrap author's personal sessions repository or this project as the destination. If the user's repository details are missing, leave Pi Sync pending configuration and continue other setup steps.

The Pi Sync template retains the manual session/mission policy, not Pi Sync's default configuration-sync scope. `safeRootFiles` and `safeDirs` are intentionally empty. Raw sessions can contain secrets; verify the SSH remote is a private repository you control before explicitly syncing. Do not run `/sync-setup` during bootstrap: it defaults to automatic mode and performs an initial pull and push. Keep `syncLocalPackagePaths: false`; local lean package paths are machine-specific and must be installed on each device independently. Omit `lastConfigSyncAt` and `lastChatSyncAt` from templates, and never copy a checkout, sessions or backups into this repository.

Only the redacted [sub2api.json](sub2api.json) template belongs in this repository: its token must remain `YOUR_API_KEY`. Keep the populated local file, `auth.json`, actual API keys, session logs, model caches, missions, installation manifests, backup history, and generated verification artifacts out of Git. No local package-source patches are included or required by this snapshot.
