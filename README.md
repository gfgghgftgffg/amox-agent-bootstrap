# amox-agent-bootstrap

English | [简体中文](README.zh-CN.md)

Deployment instructions and configuration templates for personal Codex and Pi setups on Windows, macOS and Linux. Give the agent the matching setup document: it checks the computer, reuses compatible software, installs missing components and verifies the result while preserving unrelated configuration and credentials.

## Get started

Install the host you want to use, then send it one of these prompts. The setup documents cover the remaining dependencies, including Conda and the shared Python `codex` environment.

### Codex

```text
Read https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup.md
and follow it to configure this computer. Complete the installation,
verify the results, and report anything that still needs my input.
```

[setup.md](setup.md) covers Skills, Task Router, Codex settings and Python dependencies. Its global instructions live in [templates/AGENTS.md](templates/AGENTS.md).

### Pi

```text
Read https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup_for_pi.md
and follow it to configure this computer. Fetch the referenced pi/ files,
complete the installation, verify the results, and report anything
that still needs my input.
```

[setup_for_pi.md](setup_for_pi.md) covers nine packages, eight Skills, Task Router, Python dependencies and the [Pi configuration templates](pi/README.md). Pi needs a compatible Node.js runtime and Bash; the agent checks current upstream requirements before installing.

## Pi defaults

| Component | Configuration |
| --- | --- |
| Tools | Built-in codemode enabled with `defaultTools: ["+codemode"]`, alongside the usual tools |
| Skills | `create-readme` available automatically; `humanizer` and `shuorenhua` for prose editing |
| Explicit-only Skills | `grilling`, `meeting-summary-html` and `ian-xiaohei-illustrations` |
| Interface | pi-pretty's `claudecode` tool style; open-tui loads last for its editor and inline footer |
| Search | Sub2API-hosted Codex/OpenAI search first, Exa fallback for configured recoverable errors |
| Task Router | Activated explicitly with `/skill:task-routing` |
| Pi Sync | Manual session/mission sync to your own private repository |

`create-readme` is installed from [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/create-readme), without the rest of the collection. Pi includes only its name, short description and path at startup, then reads the full instructions when needed. README work uses that Skill for structure and `humanizer` / `shuorenhua` for English and Chinese editing.

Keep the package order in [settings.json](pi/settings.json), with open-tui last so pi-pretty does not replace its inline-footer editor. [Open-tui preferences](pi/open-tui.json) enable the inline footer, Chinese settings UI and session names, hide extension-status lines, and disable telemetry cost while retaining cumulative footer cost. Independent plugin widgets remain separate.

Statusline is not installed by default. Preserve existing installations; after setup and verification, ask whether to remove them. Removal or disabling requires explicit approval.

[Search routing](pi/README.md#search-routing) uses a model independent of the conversation model and reads the existing local relay token without storing another key. Deployment adapts the credential-helper path and relay endpoint. Live search tests require separate approval.

> [!IMPORTANT]
> Provide missing credentials locally, not in chat. Pi Sync needs [your own private SSH repository](pi/pi-sync-setup.md). Bootstrap does not run synchronization or paid model/image tests; missing credentials or destinations remain pending.

## Maintain the setup

Edit the matching setup document and templates to change future deployments. Codex and Pi have separate instruction files and installation targets; these templates are not a live inventory of any computer. Keep credentials, sessions, caches and backups out of Git.

The three amox lean packages are public on npm. Install unpinned package sources and run `pi update --extensions` when needed; this does not update Pi itself. Migrating an existing local source requires approval and must replace its registration without creating duplicates. Reload or restart Pi after configuration changes, then check the actual tool and terminal behavior.

Run the offline repository checks from the repository root with Node.js:

```sh
node --test tests/*.test.cjs
```

The checks validate configuration templates and use local credential fixtures. They do not call search providers or verify access to live models.
