# amox-agent-bootstrap

Give this file or repository to Codex on a new computer and ask:

> Read setup.md, configure this computer accordingly, verify the installation, and report the results.

This is a task brief for Codex on Windows, macOS, and Linux. Choose commands based on the actual OS, CPU architecture, shell, and current upstream documentation. Complete the setup rather than handing the user a list of commands to run.

## General Approach

- Check before installing. Reuse compatible installations and repair incomplete ones. Repeated runs should not duplicate environments, Skills, or instructions.
- Preserve existing Codex settings, credentials, unrelated Skills, and user instructions. Back up existing files before editing them.
- Prefer user-level installation. Request input only for missing credentials, required permissions, or decisions that cannot be resolved from the existing configuration; continue independent work meanwhile.
- Keep secrets out of this repository, global instructions, and reports. Limit upstream installation actions to the capabilities requested below.

## 1. Conda and Python

Find an existing Conda installation by checking PATH, the active environment, and common installation locations. A missing shell command alone does not mean Conda is absent.

If Conda is missing, install a compatible Miniforge release from its official source, verify the download, and use a user-owned installation directory. Select the correct OS and architecture without replacing system Python. Report unsupported platforms clearly.

Reuse the Conda environment named `codex`, or create it with Python 3.12 if absent. Keep an existing Python version if it satisfies the required tools.

**Install all Python libraries, Python CLI tools, and future Python dependencies for this setup into the `codex` environment.** Do not install them into system Python, Conda base, or with `pip --user`. Use the environment's interpreter for pip and scripts, for example `conda run -n codex python -m pip ...`.

Check whether `pypdf` imports successfully in this environment. Install it if missing and verify the import afterward.

For other dependencies, inspect the upstream requirements first. Reuse compatible Node.js, Git, and other non-Python tools. If missing, prefer installing them into the `codex` environment through Conda, falling back to an appropriate user-level installation when necessary. Install only what the projects below require.

## 2. Projects and Skills

Read each project's current README and installation instructions. Check for an existing installation, then install using a method supported by the current Codex version. Include referenced scripts, reference documents, and other runtime resources, not just `SKILL.md`.

Respect `CODEX_HOME` and existing global Skill locations. Avoid registering the same Skill in multiple directories. Keep required source checkouts in a stable user-owned directory so installation does not depend on this setup file or a temporary download folder remaining in place.

| Project / Skill | Source | Installation Notes |
| --- | --- | --- |
| task-router | https://github.com/gfgghgftgffg/task-router | Use the Codex native installer for roles, profile, global entry, and the `task-routing` Skill. Copying the Skill alone is insufficient; do not install the Pi bundle into Codex home. |
| meeting-summary-html | https://github.com/gfgghgftgffg/meeting-summary-html | Include its scripts and references. Run Python helpers through the `codex` environment. |
| shuorenhua | https://github.com/MrGeDiao/shuorenhua | Follow its Codex installation instructions and include the full Skill and reference files. |
| create-readme | https://github.com/github/awesome-copilot/tree/main/skills/create-readme | Install only the complete `skills/create-readme/` directory, not the whole collection. Preserve its short description and leave `disable-model-invocation` absent or `false` for automatic use. |
| humanizer | https://github.com/blader/humanizer | Install the complete Skill and its referenced resources. |
| taste-skill | https://github.com/Leonxlnx/taste-skill | Install the primary frontend design Skill, currently named `design-taste-frontend` in its frontmatter under `skills/taste-skill/`, with its referenced resources. Select this Skill explicitly; the repository also contains optional variants that are not required by this setup. |
| grilling | https://github.com/mattpocock/skills/blob/main/docs/productivity/grilling.md | This URL is documentation. Locate the actual Skill, currently `skills/productivity/grilling/`. |

After downloading `grilling` and `meeting-summary-html`, add `disable-model-invocation: true` below `description` in each installed `SKILL.md`, inside the opening `---` block. If the field already exists, set it to `true`.

For README work, use `create-readme` for structure, then `humanizer` or `shuorenhua` to edit English and Chinese prose while preserving technical facts, commands and links.

### Task Router

The project is now named `task-router` (formerly `codex-task-router`). Use the new repository URL above. Existing stable checkouts may retain their directory name; verify and update their Git remote without discarding local routing configuration. The Codex profile and Skill remain named `task-routing`; do not rename them to match the repository.

Read the current README and Codex configuration reference. From the stable source checkout, use `npm ci`, then `node cli.mjs doctor`, `node cli.mjs install` to preview, and `node cli.mjs install --apply` to apply. Codex is the default host; use the verified effective Codex home and stable source configuration when passing `--codex-home` or `--config`. Never apply a Pi bundle to this home.

Check the required Node.js version and dependencies. Follow the upstream check, preview, and installation workflow, retaining its backup and conflict protections. The current installer migrates the old `codex-task-router:start/end` AGENTS block in place to `task-router:start/end`. Keep exactly one router block, preserve the manifest and unrelated instructions, and do not remove protection records to bypass an update conflict.

The current Codex backend requires V1 child communication: keep `multi_agent = true` and `multi_agent_v2 = false` as requested below. If `model_catalog_json` points to a custom catalog, also verify that the orchestrator and every selectable child model declare `"multi_agent_version": "v1"`; the global switch does not override an explicit catalog V2 entry. Preserve other catalog metadata and report unsupported host versions. The router's static checks alone do not establish V1 communication compatibility.

Verify that the configured models, providers, and reasoning levels are compatible with this Codex installation. Do not assume the user has access to upstream default models or silently replace existing model preferences. Reuse compatible settings when available; otherwise complete independent setup steps and report the model information still needed.

The upstream profile currently starts with `codex -p task-routing`. Global installation does not automatically activate routing in every session. Follow current upstream documentation and host capabilities, and distinguish installed configuration from an active profile.

### Meeting Summary

Check the helpers' actual dependencies; the current preparation scripts use the Python standard library.

Text input requires no ASR credentials. Audio/video transcription requires `DASHSCOPE_API_KEY`. If absent, report transcription as pending configuration without blocking text summaries or other installations. Do not upload real media or make paid requests just to test the installation.

## 3. Fixed Global AGENTS.md Template

Locate the global instructions used by this Codex installation, normally under `CODEX_HOME` or `~/.codex`. Check whether `AGENTS.override.md` or host-specific settings affect which file is loaded.

Use [templates/AGENTS.md](templates/AGENTS.md) as the fixed source of global instructions. Fetch it from this repository if working from a downloaded copy of `setup.md` alone. It records the user's chosen instructions; do not generate, paraphrase, summarize, or expand them on each installation.

After installing the dependencies and Task Router, substitute only these placeholders with verified absolute paths on this computer:

- `{{CONDA_PATH}}` and `{{PYTHON_PATH}}`: the Conda executable and the `codex` environment's Python interpreter.
- `{{TASK_ROUTER_CONFIG_PATH}}` and `{{TASK_ROUTER_SOURCE_PATH}}`: the installed router configuration and its stable source directory.

Back up an existing global `AGENTS.md`. On a fresh installation, write the rendered template verbatim. On an existing installation, update the corresponding quality, Python, proxy, Requirement Alignment, Workflow, and router entries from the template, removing previous automatic interview instructions and preserving unrelated user instructions. Remove redundant Skill inventory entries previously added by this setup. Keep exactly one router block, using the template's wording after the upstream installer finishes. Do not add a bootstrap managed block or descriptions of automatically discovered Skills.

Keep `grilling` installed for explicit use; do not add an automatic interview trigger to global instructions.

If a required installation fails, report the blocker rather than rendering unresolved paths or claiming missing dependencies are installed. Installation status belongs in the final report, not in the template.

## 4. Global config.toml

Locate the global `config.toml` under the effective `CODEX_HOME` (normally `~/.codex`). Back up an existing file, then merge the following requested settings into its top-level `[features]` and `[agents]` tables. Create the file or tables if missing. Update these keys in place, preserving unrelated settings, provider credentials, profiles, and agent role definitions; do not append duplicate TOML tables or keys.

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

**Windows only:** also set `daemon_auto_start = false` inside `[features]`. On macOS and Linux, do not add or change that key as part of this setup.

These values are explicitly requested defaults and should replace existing values for the listed keys. Keep `gpt-6-luna` and `medium` as specified. Check support in the installed Codex version and report unsupported settings or unavailable models instead of silently substituting alternatives. If an active profile or Task Router role overrides these defaults, report the effective difference without rewriting its role configuration.

## 5. Verification and Report

Verify the following after installation:

1. Python runs from the `codex` environment and can import `pypdf`; confirm the interpreter's location.
2. All seven project / Skill entries and required resources are present, and `grilling` and `meeting-summary-html` have `disable-model-invocation: true`.
3. Task Router's installation checks pass. Distinguish static configuration checks, host support, and live model verification; do not make paid model calls for this check.
4. The meeting preparation helper processes a temporary text fixture locally without credentials or media uploads.
5. Global instructions match `templates/AGENTS.md` after path substitution, contain no unresolved placeholders or duplicate router blocks, and preserve unrelated user instructions. Verify no automatic interview trigger or automatic Skill inventory has been added.
6. Global `config.toml` parses successfully, contains the requested settings without duplicate tables or keys, and preserves unrelated configuration. Confirm the Windows-only setting was applied only on Windows. Distinguish saved values from settings actually supported and effective in the current host.

Report each item as newly installed, reused, pending configuration, or failed. Include key paths, sources, and installed versions or commit IDs. Explain any required new session, reload, or profile activation. For failures, give the specific cause and next step; do not report partial completion as full success.
