# Pi configuration templates

Deploy through [setup_for_pi.md](../setup_for_pi.md). `<agent-dir>` is `PI_CODING_AGENT_DIR`, otherwise `~/.pi/agent`. Back up existing files and preserve unrelated settings and credentials.

| File | Target or required adaptation |
| --- | --- |
| [AGENTS.md](AGENTS.md) | `<agent-dir>/AGENTS.md`; render verified Conda/Python paths |
| [settings.json](settings.json) | Merge into `<agent-dir>/settings.json`; keep one source per package |
| [sub2api.json](sub2api.json) | `<agent-dir>/sub2api.json`; preserve an existing token or leave `YOUR_API_KEY` for the user |
| [open-tui.json](open-tui.json) | `<agent-dir>/open-tui.json` |
| [pi-btw.json](pi-btw.json) | `<agent-dir>/pi-btw.json` |
| [pi-pretty.json](pi-pretty.json) | Effective pi-pretty config directory (`PRETTY_CONFIG_DIR`, otherwise its home-directory default); `toolStyle: "claudecode"` |
| [subagents.json](subagents.json) | `<agent-dir>/subagents.json` |
| [pi-sync-suite.json](pi-sync-suite.json) | `<agent-dir>/pi-sync-suite.json`; use the user's own private SSH remote and an absolute local checkout path |
| [routing.toml](routing.toml) | Stable local configuration for the Task Router Pi installer; preserve its model choices |

The nine package entries are unpinned npm sources, including the three public amox facades. Normal installation needs no amox checkout or local prefix. Update with `pi update --extensions`. With approval, replace superseded local/old npm registrations rather than declaring both; do not separately load upstream engines.

Remove `@narumitw/pi-statusline` declarations, including disabled object-form entries; it is no longer part of this setup. Retain the nine packages in [settings.json](settings.json) in their exact relative order, with open-tui last after any preserved unrelated packages. Both pi-pretty styles install an editor; open-tui must load afterward to draw its inline footer in its own editor borders. Do not alphabetize the list. Restart fully and inspect the actual terminal.

[open-tui.json](open-tui.json) enables the inline footer, Chinese settings UI and session names, hides hostname and extension-status lines, and disables telemetry cost while retaining cumulative footer cost. Independent widgets, such as Pi Sync's own status panel, remain visible. `hideThinkingBlock: false` in [settings.json](settings.json) keeps full thinking visible; the one-line preview is only used when thinking is hidden.

Generate Router roles on each host; do not copy generated agents. Skill installation, including explicit-only Xiaohei illustrations, is specified in the setup document. Resolve pi-pretty's actual config directory before deployment: its default is not necessarily a custom Pi home. Preserve unrelated preferences and restart for the tool style to apply. Follow the [Pi Sync guide](pi-sync-setup.md) ([中文](pi-sync-setup.zh-CN.md)) for its manual-only policy; bootstrap must not synchronize data.

Keep populated credentials, sessions, missions, caches, generated files and backups out of this repository.
