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
- The 10 configured Pi packages: seven npm packages (including Sub2API, retry, Pi Sync and UI packages) and three independently installed lean packages from [amox_pi_extensions_lean](https://github.com/gfgghgftgffg/amox_pi_extensions_lean). Installation sources and update steps are listed in [setup_for_pi.md](setup_for_pi.md).
- Six user Skills: `design-taste-frontend`, `humanizer`, `meeting-summary-html`, `shuorenhua`, `grilling`, and Pi's generated `task-routing`.
- Fixed [Pi AGENTS.md](pi/AGENTS.md), [settings](pi/settings.json), router configuration, and non-sensitive plugin configurations in [pi/](pi/README.md).
- Interview Skill: `grilling`, for explicit use only. Both setup documents include the required `disable-model-invocation: true` setting for it and `meeting-summary-html`.
- Redacted [Sub2API configuration](pi/sub2api.json), preserving the relay URL and API mode with `YOUR_API_KEY` as the token placeholder.
- Lean subagent configuration in [pi/subagents.json](pi/subagents.json), including 50 background slots, model display, strict role dispatch, and native workflows.

- [Pi Sync configuration](pi/pi-sync-suite.json): manual-only session/mission sync to the user's SSH repository, with a machine-local checkout path rendered during setup. No sync or private-data upload is performed by bootstrap.

Pi routing is opt-in through `/skill:task-routing` and uses `@gfgghgftgffg/pi-subagents-lean` from the maintained amox repository for direct subagents and native workflows. Search roles use `@gfgghgftgffg/pi-web-access-lean`'s `web_access` interface. Model availability and relay/search credentials must be checked on the new computer; no credentials or session data are stored here.

Edit [setup_for_pi.md](setup_for_pi.md) for installation behavior and the files in [pi/](pi/README.md) for personal Pi configuration. Codex and Pi have separate instruction templates and installation targets; do not overwrite one with the other's bundle.
