# amox-agent-bootstrap

English | [简体中文](README.zh-CN.md)

Personal Codex and Pi setup instructions for Windows, macOS, and Linux. Give the corresponding setup file to your agent and let it check the computer, install missing dependencies, and configure your tools and Skills.

## Codex Usage

Install Codex first, then send it this prompt:

```text
Read https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup.md
and follow it to configure this computer. Complete the installation,
verify the results, and report anything that still needs my input.
```

You can also download or clone this repository and ask Codex to follow the local `setup.md`.

## Codex Included

- Conda detection and Miniforge installation when needed.
- A shared `codex` environment for Python dependencies, including `pypdf`.
- Task routing: [task-router](https://github.com/gfgghgftgffg/task-router) (formerly `codex-task-router`); the profile and Skill remain `task-routing`.
- Meeting summaries: `meeting-summary-html`.
- Writing: `shuorenhua` and `humanizer`.
- Frontend design: `taste-skill` (`design-taste-frontend`).
- Task clarification: `grilling`, available for explicit use.
- A fixed [global AGENTS.md template](templates/AGENTS.md), with only local paths substituted and no repeated inventory of automatically discovered Skills.
- Global `config.toml` settings for memories, idle-sleep prevention, and multi-agent defaults (30 concurrent threads, `gpt-6-luna`, `medium` effort), with the requested Windows-only daemon setting. See [setup.md](setup.md) for exact values.

Codex chooses platform-appropriate commands, reuses compatible installations, and preserves existing configuration. Task routing requires compatible models and profile activation; meeting audio/video transcription requires `DASHSCOPE_API_KEY`. Text-only meeting preparation needs no ASR key.

Edit [setup.md](setup.md) to customize Codex installation and [templates/AGENTS.md](templates/AGENTS.md) to change its shared global instructions.

## Pi Usage

Install Pi first, then send it this prompt:

```text
Read https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup_for_pi.md
and follow it to configure this computer. Fetch the referenced pi/ files,
complete the installation, verify the results, and report anything
that still needs my input.
```

You can also clone this repository and ask Pi to follow the local [setup_for_pi.md](setup_for_pi.md). It uses the current personal Pi installation as its baseline, not a translation of Codex settings.

## Pi Included

- The shared `codex` Conda environment and `pypdf`.
- The 10 configured Pi packages, all installed from npm without version pins, including the three maintained lean packages from [amox_pi_extensions_lean](https://github.com/gfgghgftgffg/amox_pi_extensions_lean). Update them with `pi update --extensions`; installation sources and duplicate-free migration steps are listed in [setup_for_pi.md](setup_for_pi.md).
- Seven user Skills: `design-taste-frontend`, `humanizer`, `meeting-summary-html`, `shuorenhua`, `grilling`, `ian-xiaohei-illustrations`, and Pi's generated `task-routing`.
- Article illustrations: [Ian Xiaohei Illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations), with its references and example assets. Set `disable-model-invocation: true`: its name, description and path are excluded from Pi's default startup Skill prompt; load it explicitly with `/skill:ian-xiaohei-illustrations`. Image generation requires a supported host tool and image model; installation does not verify generation.
- Fixed [Pi AGENTS.md](pi/AGENTS.md), [settings](pi/settings.json), router configuration, and non-sensitive plugin configurations in [pi/](pi/README.md).
- [pi-pretty configuration](pi/pi-pretty.json) using `toolStyle: "claudecode"` instead of `default`; restart Pi to apply the style.
- Interview Skill: `grilling`, for explicit use only. Both setup documents include the required `disable-model-invocation: true` setting for it and `meeting-summary-html`.
- Redacted [Sub2API configuration](pi/sub2api.json), preserving the relay URL and API mode with `YOUR_API_KEY` as the token placeholder.
- Lean subagent configuration in [pi/subagents.json](pi/subagents.json), including 50 background slots, model display, strict role dispatch, and native workflows.

- [Pi Sync configuration](pi/pi-sync-suite.json): manual-only session/mission sync. You must supply your own private repository's SSH URL and this computer's checkout path; see the [dedicated setup guide](pi/pi-sync-setup.md). No sync or private-data upload is performed by bootstrap.

Pi routing is opt-in through `/skill:task-routing` and uses `@gfgghgftgffg/pi-subagents-lean` from the maintained amox repository for direct subagents and native workflows. Search roles use `@gfgghgftgffg/pi-web-access-lean`'s `web_access` interface. Model availability and relay/search credentials must be checked on the new computer; no credentials or session data are stored here.

Edit [setup_for_pi.md](setup_for_pi.md) for installation behavior and the files in [pi/](pi/README.md) for personal Pi configuration. Codex and Pi have separate instruction templates and installation targets; do not overwrite one with the other's bundle.

## Pi Sync: Your Own Sessions Repository Is Required

Follow the [Pi Sync setup guide](pi/pi-sync-setup.md) before using synchronization. Create or choose a **private sessions repository you control**, then replace `YOUR_GITHUB_USERNAME` and `YOUR_PRIVATE_SESSIONS_REPO` in the template's `repoUrl`, and `{{SYNC_REPO_DIR}}` in `repoDir`. Do not use the author's personal repository or this bootstrap repository as the sync destination. Other computers use the same remote but their own local checkout paths; keep an already configured destination rather than overwriting it.

The guide covers SSH access, local configuration, manual-mode checks and cross-computer use. Missing repository details leave Pi Sync pending configuration, not ready to sync. Raw sessions can contain secrets. Do not run `/sync-setup` as a setup check: it performs an initial pull and push with automatic-mode defaults. Run `/sync-push` or `/sync-pull` only when you explicitly intend to transfer data.
