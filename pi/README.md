# Pi configuration files

These files capture the current personal Pi configuration without credentials or runtime history. Follow [../setup_for_pi.md](../setup_for_pi.md), not a blind copy of this directory.

| Repository file | Installation target |
| --- | --- |
| [AGENTS.md](AGENTS.md) | `<agent-dir>/AGENTS.md`, after substituting verified Conda/Python paths |
| [settings.json](settings.json) | Merge into `<agent-dir>/settings.json`; omit machine-generated `lastChangelogVersion` |
| [sub2api.json](sub2api.json) | `<agent-dir>/sub2api.json`; preserve existing credentials, otherwise leave `YOUR_API_KEY` and report the file path for the user to edit |
| [open-tui.json](open-tui.json) | `<agent-dir>/open-tui.json` |
| [pi-btw.json](pi-btw.json) | `<agent-dir>/pi-btw.json` |
| [pi-pretty.json](pi-pretty.json) | Effective pi-pretty config directory (`PRETTY_CONFIG_DIR` when set, otherwise its agent-directory default); set `toolStyle: "claudecode"` and preserve unrelated preferences |
| [subagents.json](subagents.json) | `<agent-dir>/subagents.json`; 50 background slots, model display, strict role dispatch, and native lean workflows |
| [pi-sync-suite.json](pi-sync-suite.json) | `<agent-dir>/pi-sync-suite.json`; replace the SSH URL placeholders with the user's own private sessions repository and render `{{SYNC_REPO_DIR}}` as an absolute local path; preserve an existing destination |
| [routing.toml](routing.toml) | Stable Task Router source configuration passed with `--config`; do not copy generated agents from another host |

`<agent-dir>` is `PI_CODING_AGENT_DIR`, otherwise `~/.pi/agent`.

JSON plugin configurations capture this computer's non-sensitive preferences. The subagent template merges global defaults with the preferences saved by the agent UI in `~/.pi/subagents.json`, deploying them as global defaults on new computers. All ten package entries are unversioned npm sources, including `@gfgghgftgffg/pi-web-access-lean`, `@gfgghgftgffg/rpiv-todo-lean` and `@gfgghgftgffg/pi-subagents-lean`. Install the latest releases through Pi; no amox source checkout or local prefix is needed for normal installation. The AGENTS template has two local path placeholders and the current Router-managed policy. The router configuration matches this computer's role-map model choices; updating dependency sources must not replace those choices with the Router repository's example defaults.

Skill installation and the required `disable-model-invocation: true` setting are covered in [setup_for_pi.md](../setup_for_pi.md). Neither global AGENTS template automatically triggers a grilling interview.

Install the three lean subagent/web/todo facades from npm using the sources in settings; do not install the workspace root or separately load upstream engines. During migration, replace old local amox paths and `@ssk_dev` registrations rather than appending duplicates. A retained source checkout or old prefix is not the active extension after migration. Task Router uses flat `agents/tr_*.md` and the lean `web_access` tool; generate roles with the current [task-router](https://github.com/gfgghgftgffg/task-router) Pi installer.

The Pi Skill list now includes [Ian Xiaohei Illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations). Install the repository's inner `ian-xiaohei-illustrations/` Skill directory with its references and assets, or reuse an already discoverable complete copy; do not duplicate the locally nested copy. Set `disable-model-invocation: true` in its installed `SKILL.md` frontmatter, including on existing installations and after upstream updates. Pi then omits its name, description and path from the default startup Skill prompt listing; `/skill:ian-xiaohei-illustrations` explicitly loads its instructions. Keep it discoverable rather than deleting or disabling the Skill entirely. Restart or reload to refresh discovery; existing conversation context is not erased. Image generation depends on actual host/model support, not merely Skill discovery.

Apply `toolStyle: "claudecode"` from [pi-pretty.json](pi-pretty.json), preserving other pi-pretty settings. Check `PRETTY_CONFIG_DIR` and the installed extension's path resolution before writing; restart Pi because this style is read at startup. This changes presentation, not the Pi theme or model defaults.

The Pi Sync template contains **placeholder repository details**, not a usable shared destination. Each user must configure their own private sessions repository and local checkout path; follow the separate [English guide](pi-sync-setup.md) or [中文说明](pi-sync-setup.zh-CN.md). Do not use the bootstrap author's personal sessions repository or this project as the destination. If the user's repository details are missing, leave Pi Sync pending configuration and continue other setup steps.

The Pi Sync template retains the manual session/mission policy, not Pi Sync's default configuration-sync scope. `safeRootFiles` and `safeDirs` are intentionally empty. Raw sessions can contain secrets; verify the SSH remote is a private repository you control before explicitly syncing. Do not run `/sync-setup` during bootstrap: it defaults to automatic mode and performs an initial pull and push. Keep `syncLocalPackagePaths: false`; the maintained lean packages now use portable npm declarations, so local-path syncing is not needed. Install them from npm on each device. Omit `lastConfigSyncAt` and `lastChatSyncAt` from templates, and never copy a checkout, sessions or backups into this repository.

Only the redacted [sub2api.json](sub2api.json) template belongs in this repository: its token must remain `YOUR_API_KEY`. Keep the populated local file, `auth.json`, actual API keys, session logs, model caches, missions, installation manifests, backup history, and generated verification artifacts out of Git. No local package-source patches are included or required by this snapshot.
