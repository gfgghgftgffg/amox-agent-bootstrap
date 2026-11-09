# Pi Sync setup

English | [简体中文](pi-sync-setup.zh-CN.md)

Install `npm:@gfgghgftgffg/amox-pi-sync` on each computer. Use your own **private repository with SSH read/write access**, not this bootstrap repository. Remove replaced `pi-sync-suite` or local amox-pi-sync registrations; keep their files and backups. Load only one sync extension.

## Configuration

Deploy [amox-pi-sync.json](amox-pi-sync.json) to `<agent-dir>/amox-pi-sync.json`, where `<agent-dir>` is `PI_CODING_AGENT_DIR` or `~/.pi/agent`.

| Field | Value |
| --- | --- |
| `repoUrl` | Your private repository's SSH URL; replace both `YOUR_*` placeholders |
| `repoDir` | Replace `{{SYNC_REPO_DIR}}` with a dedicated absolute checkout path, normally `<agent-dir>/amox-pi-sync-repo` |
| `mode` | `manual`; no startup network access |
| `paths` | `["sessions", "missions"]`, relative to the agent directory |
| `retention` | Keep the newest 20 backups for up to 180 days; cleanup requires manual preview/confirmation |

Back up existing configuration. Preserve a valid amox remote, checkout and runtime fields; each computer uses the same remote but its own local path. Missing repository details leave sync pending.

When migrating from `pi-sync-suite.json`, preserve the SSH remote but use a new `amox-pi-sync-repo` checkout, not the old `sync-suite-repo`. If the new configuration is absent, the extension can read the legacy file without changing it; saving writes the new file. The amox schema does not use the suite's `chat`, `environment`, `policy` or `syncLocalPackagePaths` fields. Backups live in `<agent-dir>/amox-pi-sync-backups`.

## Verification and use

Check repository privacy and write permission in GitHub settings. SSH/read access can be checked with `ssh -T git@github.com` and `git ls-remote <your-ssh-repo-url>`. Reload Pi and inspect `/sync-status` or click the Starline `pi-sync` pill. Manual mode does not contact the remote at startup.

- `/sync-push`: upload selected raw agent files.
- `/sync-pull`: apply remote files; different content at the same path is backed up before replacement. Local-only files remain; active sessions cannot be overwritten.
- `/sync-settings`: configure paths/mode, backups, diagnostics and manual cleanup.

Review sessions for secrets and back up local data before transfers. Avoid simultaneous pushes. Bootstrap does not run synchronization, setup commands or cleanup. `/sync-setup` saves configuration without transferring data; it is unnecessary for bootstrap verification. Keep credentials, sessions, checkouts and backups out of this repository.

[README](../README.md) · [Pi deployment](../setup_for_pi.md)
