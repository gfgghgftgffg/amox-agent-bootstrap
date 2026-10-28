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

[setup_for_pi.md](setup_for_pi.md) covers extensions, Skills, Task Router, Python dependencies and the [Pi configuration templates](pi/README.md). Pi needs a compatible Node.js runtime and Bash; the agent checks current upstream requirements before installing.

## Pi defaults

| Component | Configuration |
| --- | --- |
| Tools | Built-in codemode enabled with `defaultTools: ["+codemode"]`, alongside the usual tools |
| Skills | `create-readme` available automatically; `humanizer` for prose editing |
| Explicit-only Skills | `anti-defensive-writing`, `grilling`, `meeting-summary-html` and `ian-xiaohei-illustrations` |
| Interface | pi-tidy for tool folding/diffs; pi-starline loads last for the editor, user-message frames and clickable pill footer |
| Appearance | Catppuccin Mocha, Maple Mono NF CN and 95% terminal opacity |
| Search | Sub2API-hosted Codex/OpenAI search first, Exa fallback for configured recoverable errors |
| Task Router | Explicit `/skill:task-routing`; shared rules in the Router checkout, Skills and scoped codemode enabled for children; no global Pi Router block |
| Pi Sync | Manual session/mission sync to your own private repository |
| Autoresearch | pi-autoresearch with three explicit-only Skill wrappers; experiment loops start only on request |

See [Pi setup](setup_for_pi.md) for package order, UI migration and Skill installation, and [Pi configuration](pi/README.md) for credential paths and search routing. Bootstrap applies **Catppuccin Mocha to both Pi and the active terminal profile**. Font installation and opacity remain user-managed; see the [appearance guide](pi/appearance.md).

> [!IMPORTANT]
> Provide missing credentials locally, not in chat. Pi Sync needs [your own private SSH repository](pi/pi-sync-setup.md). Bootstrap does not run synchronization or paid model/image tests; missing credentials or destinations remain pending.

## Maintain the setup

Edit the matching setup document and templates to change future deployments. Keep credentials, sessions, caches and backups out of Git.

Update Pi packages with `pi update --extensions`; this does not update Pi itself. Reload or restart Pi after configuration changes. Installation and migration instructions are in [Pi setup](setup_for_pi.md).

Run the offline repository checks from the repository root with Node.js:

```sh
node --test tests/*.test.cjs
```

The checks validate configuration templates and use local credential fixtures. They do not call search providers or verify access to live models.
