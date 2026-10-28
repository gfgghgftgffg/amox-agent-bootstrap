# Codex setup

Configure Codex on Windows, macOS or Linux using the settings below. Reuse compatible installations, back up changed files and preserve unrelated configuration. Respect `CODEX_HOME` (default `~/.codex`). Keep credentials local; do not make paid calls or upload files for installation checks.

## 1. Runtime and Python

- Reuse Conda, or install official Miniforge in a user-owned directory.
- Reuse the `codex` environment, or create it with Python 3.12. Use its interpreter for all Python scripts and dependencies; do not use system Python, base or `pip --user`.
- Install `pypdf` if absent and verify its import.
- Reuse compatible Node.js, Git and shell tools. Install missing dependencies required by the projects below, preferably through Conda or another user-level installation.

## 2. Projects and Skills

Install complete Skills with their scripts, references and assets into the effective global Skill directory. Reuse existing copies without duplicate registrations. Keep required source checkouts in stable user-owned directories.

| Project / Skill | Source | Configuration |
| --- | --- | --- |
| task-router | https://github.com/gfgghgftgffg/task-router | Install the Codex roles, `task-routing` profile and Skill through its native installer |
| meeting-summary-html | https://github.com/gfgghgftgffg/meeting-summary-html | Include preparation scripts; use the `codex` Python interpreter |
| shuorenhua | https://github.com/MrGeDiao/shuorenhua | Include the complete Skill and references |
| create-readme | https://github.com/github/awesome-copilot/tree/main/skills/create-readme | Install only `skills/create-readme/`, not the whole collection; leave `disable-model-invocation` absent or `false` |
| humanizer | https://github.com/blader/humanizer | Include the complete Skill |
| anti-defensive-writing | https://github.com/Kiterlin/anti-defensive-writing | Install only the root `SKILL.md` and license; set `disable-model-invocation: true` |
| taste-skill | https://github.com/Leonxlnx/taste-skill | Install only `skills/taste-skill/`, named `design-taste-frontend` |
| grilling | https://github.com/mattpocock/skills/blob/main/docs/productivity/grilling.md | Install the actual Skill at `skills/productivity/grilling/` |

Set `disable-model-invocation: true` in `anti-defensive-writing`, `grilling` and `meeting-summary-html`, including reused copies. Keep them available for explicit invocation; do not add automatic interview instructions.

Leave `disable-model-invocation` absent or `false` in `design-taste-frontend`, `humanizer` and `shuorenhua`. Do not install `humanizer-zh` as an additional default.

For README work, use `create-readme` for structure, then `humanizer` or `shuorenhua` for prose. Meeting text preparation needs no ASR key; audio/video transcription requires `DASHSCOPE_API_KEY`.

### Task Router

Read the current upstream installation instructions. All Router parents and roles read the live `<router-checkout>/AGENTS.md`. On first setup, initialize it from the rendered common rules in [templates/AGENTS.md](templates/AGENTS.md), excluding Router activation text and managed Router blocks. Render local Conda/Python paths. If the shared file is already customized or used by Pi, preserve it and merge only requested common-rule changes; do not reset it or mirror later global edits automatically. Keep the checkout stable; moving it requires reinstalling the generated absolute references.

From its stable checkout, run:

```sh
npm ci
node cli.mjs doctor
node cli.mjs install
node cli.mjs install --apply
```

Use the effective Codex home and a stable routing configuration (`--codex-home` / `--config` when needed). Preserve existing model choices, installer backups and exactly one managed Router block. Do not install the Pi bundle into Codex home.

Use V1 child communication: `multi_agent = true`, `multi_agent_v2 = false`. If a custom `model_catalog_json` is configured, its orchestrator and child models must also declare `"multi_agent_version": "v1"`. Report unsupported models/settings without substituting others.

Start the profile with `codex -p task-routing`; ordinary Codex sessions do not activate it automatically.

## 3. Global instructions

Deploy [templates/AGENTS.md](templates/AGENTS.md) to the effective Codex global instructions path. Substitute only verified absolute paths:

- `{{CONDA_PATH}}`: Conda executable.
- `{{PYTHON_PATH}}`: `codex` environment interpreter.
- `{{TASK_ROUTER_CONFIG_PATH}}`: routing configuration.
- `{{TASK_ROUTER_SOURCE_PATH}}`: Router checkout.

On existing installations, update the corresponding sections while preserving unrelated instructions and one installer-managed Router block. Respect `AGENTS.override.md`. Do not add a Skill inventory or automatic interview trigger.

## 4. Global config.toml

Merge these values into `<CODEX_HOME>/config.toml`, preserving unrelated settings, profiles and credentials:

```toml
[features]
memories = true
prevent_idle_sleep = true
multi_agent = true
multi_agent_v2 = false

[agents]
max_concurrent_threads_per_session = 30
default_subagent_model = "gpt-6-luna"
default_subagent_reasoning_effort = "medium"
```

On **Windows only**, also set `daemon_auto_start = false` under `[features]`. Keep the specified model and reasoning level; report unavailable settings or profile overrides.

## 5. Verification

- Verify the `codex` interpreter and `pypdf` import.
- All eight project / Skill entries and required resources must be present, with the three explicit-only flags set. Verify the shared Router `AGENTS.md` and generated references.
- Run Router's static checks and meeting preparation on a temporary local text fixture.
- Parse `config.toml`; check template values, rendered paths and one Router block.
- Report installed/reused/pending/failed components, effective paths and required restart/profile activation. Do not run paid model tests or media uploads.
