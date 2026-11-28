# Codex Setup Guide

Configure Codex on Windows, macOS, or Linux with the runtimes, Skills, Task Router profile, and settings below. Resolve `CODEX_HOME` (default `~/.codex`), reuse compatible installations, back up every file before editing it, and preserve unrelated configuration and credentials. Keep secrets on the local machine; do not run paid model calls or upload local files during installation checks.

## 1. Runtime and Python environment

- Reuse an existing Conda installation, or install official Miniforge in a user-owned directory.
- Reuse the `codex` Conda environment, or create it with Python 3.12. Run all Python scripts and package installs with its interpreter rather than system Python, `base`, or `pip --user`.
- Install `pypdf` in `codex` if missing and confirm `import pypdf` succeeds.
- Reuse compatible Node.js, Git, and shell tools. Install any missing user-level dependencies needed by the projects below.

## 2. Projects and Skills

Install each Skill with its complete scripts, references, and assets into the active global Codex Skill directory. Reuse existing copies without creating duplicate entries, and place required Git checkouts in stable user-owned directories.

| Project / Skill | Source | Installation rules |
| --- | --- | --- |
| `task-router` | https://github.com/gfgghgftgffg/task-router | Run its native installer to set up Codex roles, the `task-routing` profile, and the Skill |
| `meeting-summary-html` | https://github.com/gfgghgftgffg/meeting-summary-html | Install with preparation scripts; run Python scripts via the `codex` interpreter |
| `create-readme` | https://github.com/github/awesome-copilot/tree/main/skills/create-readme | Install only `skills/create-readme/` |
| `humanizer` | https://github.com/blader/humanizer | Install the full Skill directory |
| `anti-defensive-writing` | https://github.com/Kiterlin/anti-defensive-writing | Install only the root `SKILL.md` and license |
| `design-taste-frontend` | https://github.com/Leonxlnx/taste-skill | Install only `skills/taste-skill/` under the folder name `design-taste-frontend` |
| `amox-grill-me` | [skills/amox-grill-me/](skills/amox-grill-me/) in this repository | Copy the complete directory, including `LICENSE`, as `amox-grill-me` |
| `de-ai` | [skills/de-ai/](skills/de-ai/) in this repository | Copy the complete directory (`scripts/`, `references/`, `projects/`, `README.md`, `README.zh-CN.md`, `SKILL.md`, `LICENSE`); run scripts with the `codex` interpreter (`.docx`, `.md`, `.txt`) |

Apply these invocation and dependency rules:

- Set `disable-model-invocation: true` in `anti-defensive-writing`, `amox-grill-me`, `meeting-summary-html`, and `de-ai`, including reused copies.
- Leave `disable-model-invocation` absent or `false` in `create-readme`, `design-taste-frontend` and `humanizer`.
- Install `amox-grill-me` in place of upstream `grilling` or legacy `grill-me`. On existing setups, back up and remove those replaced Skill copies from active discovery paths while keeping unrelated Skills intact. Do not install or update the upstream copy alongside `amox-grill-me`.
- `meeting-summary-html` text preparation runs without an ASR key; audio or video transcription requires `DASHSCOPE_API_KEY`.
- For `de-ai`, install `skills/de-ai/scripts/requirements.txt` in the `codex` environment (`pypdf` is included). English targets also require `torch`, `transformers`, and cached `gpt2` weights; PDF export uses LibreOffice (or installed Microsoft Word on Windows). Invoke `de-ai` explicitly with a file path. Its translation chains send document text to third-party endpoints, and its default term replacement table is empty.

### Task Router setup

Check the upstream `task-router` README before installing. All Router parents and roles read the live `<router-checkout>/AGENTS.md`:

- Keep shared rules in `<router-checkout>/AGENTS.md` portable: reference the local Conda `codex` environment and resolve executable paths at runtime without hardcoding personal paths or leaving raw `{{...}}` placeholders. Exclude Router activation banners and managed Router blocks from [templates/AGENTS.md](templates/AGENTS.md). Render machine-specific Conda/Python paths only in the host-global `AGENTS.md`.
- If the shared file is already customized or used by Pi, preserve it and merge only requested common-rule updates rather than resetting it or mirroring later host-global edits.
- Keep `<router-checkout>` at a fixed path; moving it invalidates generated absolute references and requires reinstalling Router.

From the stable Router checkout, run:

```sh
npm ci
node cli.mjs doctor
node cli.mjs install
node cli.mjs install --apply
```

Pass `--codex-home` and `--config` when using non-default paths. Preserve existing model selections, installer backups, and a single managed Router block.

Keep V1 child communication (`multi_agent = true`, `multi_agent_v2 = false`). When a custom `model_catalog_json` is configured, orchestrator and child model entries must also specify `"multi_agent_version": "v1"`. Report unavailable models or unsupported settings rather than substituting alternatives.

Launch routed sessions explicitly with `codex -p task-routing`; standard Codex sessions do not enable routing automatically.

## 3. Global instructions

Render [templates/AGENTS.md](templates/AGENTS.md) into the active Codex global instructions file, replacing each placeholder with a verified absolute path:

- `{{CONDA_PATH}}`: Conda executable
- `{{PYTHON_PATH}}`: `codex` environment Python interpreter
- `{{TASK_ROUTER_CONFIG_PATH}}`: Task Router configuration file
- `{{TASK_ROUTER_SOURCE_PATH}}`: Task Router repository checkout

On existing installations, update the template-managed sections while preserving unrelated user rules, `AGENTS.override.md`, and the single installer-managed Router block.

## 4. Global `config.toml`

Merge the settings below into `<CODEX_HOME>/config.toml`, keeping existing profiles, credentials, and unrelated keys intact:

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

On Windows hosts only, also set `daemon_auto_start = false` under `[features]`. Keep `gpt-6-luna` and `"medium"` unchanged; report if a setting or model is unavailable or overridden by a profile.

## 5. Verification

- Confirm the `codex` Python interpreter runs and imports `pypdf`.
- Check all installed Skills, their bundled directories/files, and their `disable-model-invocation` front matter. Confirm replaced `grilling`/`grill-me` copies are out of active discovery paths.
- Check `<router-checkout>/AGENTS.md` and generated Router role references; run Router static checks and test `meeting-summary-html` text preparation against a temporary local text fixture.
- Parse `<CODEX_HOME>/config.toml` and check `<CODEX_HOME>/AGENTS.md` for rendered paths and a single Router block.
- Summarize installed, reused, pending, and failed items along with effective paths and any required restart or `codex -p task-routing` activation step.
