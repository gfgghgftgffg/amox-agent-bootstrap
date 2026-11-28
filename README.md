# amox-agent-bootstrap

English | [简体中文](README.zh-CN.md)

![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![Hosts](https://img.shields.io/badge/hosts-Codex%20%7C%20Pi-blue?style=flat-square)
![Node](https://img.shields.io/badge/Node.js-%3E%3D22.19-3c873a?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12%20(codex)-3776ab?style=flat-square)

[Quick start](#quick-start) • [Pi defaults](#pi-defaults) • [Repository layout](#repository-layout) • [Maintenance](#maintenance)

Bootstrap guides and configuration templates for personal Codex and Pi environments on Windows, macOS, and Linux. Point an installed agent at the matching setup guide to inspect the machine, reuse compatible runtimes, install missing packages and Skills, and verify the deployment while keeping existing credentials and unrelated settings intact.

## Quick start

Install Codex or Pi first, then send it the corresponding prompt below. Each guide sets up Miniforge/Conda, the shared Python 3.12 `codex` environment, Skills, and Task Router.

### Set up Codex

```text
Read https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup.md
and follow it to configure this computer. Complete the installation,
verify the results, and report anything that still needs my input.
```

[setup.md](setup.md) installs Codex Skills, Task Router (`codex -p task-routing`), `config.toml` defaults, and Python packages, and renders [templates/AGENTS.md](templates/AGENTS.md) into `CODEX_HOME`.

### Set up Pi

```text
Read https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup_for_pi.md
and follow it to configure this computer. Fetch the referenced pi/ files,
complete the installation, verify the results, and report anything
that still needs my input.
```

[setup_for_pi.md](setup_for_pi.md) installs Pi extensions, Skills, Task Router, Python dependencies, and the [pi/ templates](pi/README.md). Pi requires a compatible Node.js runtime (`>=22.19` for current packages) and Bash; the agent verifies current upstream version requirements before installing.

## Pi defaults

| Area | Default setup |
| --- | --- |
| Tools | Enables `defaultTools: ["+codemode"]` alongside standard built-in tools |
| Automatic Skills | `create-readme`, `design-taste-frontend`, `humanizer` |
| Explicit-only Skills | `anti-defensive-writing`, `amox-grill-me`, `meeting-summary-html`, `ian-xiaohei-illustrations`, `de-ai`, and three `autoresearch-*` wrappers |
| Interface | `pi-tidy` frames messages, right-aligns user prompts (`userMessageAlign: "right"`) with a `syntaxKeyword` border, uses the package default for final replies, and renders tool diffs; `pi-starline` provides the editor and clickable pill footer |
| Appearance | Applies Catppuccin Mocha to both Pi and the active terminal profile; user-installed Maple Mono NF CN font and 95% terminal opacity ([appearance guide](pi/appearance.md)) |
| Web search | Routes `exa` first, falling back to `sub2api-gpt-only` (`gpt-6.2-sol`) on configured recoverable errors |
| Reply summaries | `amox-high-level` on demand via `/hl` or `+hl` |
| Task Router | Explicit `/skill:task-routing` backed by `<router-checkout>/AGENTS.md`, with `skills: true` and scoped `codemode` on child roles and no global Pi Router block |
| Persistent goals | `pi-goal-x-lean` paired with `pi-subagents-lean` workflows, started only on `/goal` |
| Session sync | `amox-pi-sync` in manual `sessions`-only mode using [your private SSH repository](pi/pi-sync-setup.md) |
| Autoresearch | `pi-autoresearch` (`skills: []`) exposed via explicit-only Skill wrappers and `/autoresearch` |

See [setup_for_pi.md](setup_for_pi.md) for package order, legacy UI migration, and Skill installation, and [pi/README.md](pi/README.md) for template targets and search fallback rules.

> [!IMPORTANT]
> Enter missing API keys and SSH remotes directly on the local machine rather than in chat. Bootstrap leaves unconfigured credentials or sync destinations pending and does not execute sync transfers, benchmarks, or paid model/image calls.

## Repository layout

| Path | Contents |
| --- | --- |
| [setup.md](setup.md) | Automated deployment and verification steps for Codex |
| [setup_for_pi.md](setup_for_pi.md) | Automated deployment, migration, and verification steps for Pi |
| [templates/AGENTS.md](templates/AGENTS.md) | Global instruction template for Codex |
| [pi/](pi/README.md) | Pi configuration templates, Catppuccin Mocha theme, search key helper, and appearance/sync guides |
| [skills/amox-grill-me/](skills/amox-grill-me/SKILL.md) | Bundled explicit-only plan-interview Skill |
| [skills/de-ai/](skills/de-ai/README.md) | Multi-hop translation and regex rewriting pipeline (`.docx`, `.md`, `.txt`) |
| `tests/` | Offline Node.js contract and configuration tests |

## Maintenance

Edit the setup guides and template files in this repository to update future deployments. Keep real tokens, session logs, sync checkouts, caches, and backups out of Git.

Update installed Pi extensions without upgrading Pi core:

```sh
pi update --extensions
```

Reload or restart Pi after changing configuration or packages.

Run the offline test suite from the repository root:

```sh
node --test tests/*.test.cjs
```

The suite checks JSON templates, Skill and Router contracts, local Markdown links, and credential-helper failure modes using temporary fixtures without network or model calls.
