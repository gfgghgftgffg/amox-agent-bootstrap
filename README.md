# amox-agent-bootstrap

English | [简体中文](README.zh-CN.md)

Deployment instructions and configuration templates for personal Codex and Pi setups on Windows, macOS and Linux. The agent checks the computer, reuses compatible software, installs missing components and verifies the result. Existing unrelated configuration and credentials must be preserved.

## Codex

Install Codex, then give it this prompt:

```text
Read https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup.md
and follow it to configure this computer. Complete the installation,
verify the results, and report anything that still needs my input.
```

[setup.md](setup.md) covers Conda, the shared Python `codex` environment, Skills, Task Router and Codex settings. [templates/AGENTS.md](templates/AGENTS.md) contains its global instructions.

## Pi

Install Pi, then give it this prompt:

```text
Read https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup_for_pi.md
and follow it to configure this computer. Fetch the referenced pi/ files,
complete the installation, verify the results, and report anything
that still needs my input.
```

[setup_for_pi.md](setup_for_pi.md) covers ten packages, seven Skills (including explicit-only `ian-xiaohei-illustrations`), Task Router, Conda and the [Pi configuration templates](pi/README.md), with pi-pretty's `claudecode` tool style. The three amox lean packages are public on npm; install unpinned sources and run `pi update --extensions` when needed. Existing local-source migration requires approval and must replace, not duplicate, registrations.

Task routing is opt-in through `/skill:task-routing`. Pi Sync uses manual session/mission sync and requires [your own private repository](pi/pi-sync-setup.md). Bootstrap does not run sync or paid model/image tests.

## Configuration

Edit the corresponding setup document and templates to change the deployment. Codex and Pi use separate instruction files and installation targets. Templates are not a live inventory of any computer. Keep actual credentials, sessions, caches and backups out of Git; provide missing secrets locally, not in chat.
