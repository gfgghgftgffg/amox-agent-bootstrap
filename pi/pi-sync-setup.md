# Pi Sync Setup

English | [简体中文](pi-sync-setup.zh-CN.md)

Install `npm:@gfgghgftgffg/amox-pi-sync` on each machine to manually sync Pi session files through your own private Git repository over SSH. Never point Pi Sync at this public bootstrap repository.

## Configure `amox-pi-sync.json`

Back up any existing sync config, then deploy [amox-pi-sync.json](amox-pi-sync.json) to `<agent-dir>/amox-pi-sync.json` (`PI_CODING_AGENT_DIR` or `~/.pi/agent`):

| Field | Value and rules |
| --- | --- |
| `repoUrl` | SSH URL of your private sessions repository (replace `YOUR_GITHUB_USERNAME` and `YOUR_PRIVATE_SESSIONS_REPO`) |
| `repoDir` | Dedicated local Git checkout path; replace `{{SYNC_REPO_DIR}}` with an absolute path (typically `<agent-dir>/amox-pi-sync-repo`) |
| `mode` | `"manual"` (no automatic pull or push on Pi startup) |
| `paths` | `["sessions"]`, resolved relative to `<agent-dir>` |
| `retention` | `keepBackups: 20`, `maxAgeDays: 180` under `<agent-dir>/amox-pi-sync-backups`; cleanup runs only after manual preview and confirmation |

Preserve valid existing `repoUrl`, `repoDir`, and timing settings across reruns; every machine shares the same SSH remote while using its own local `repoDir`. If the user has not created the private repository yet, leave `amox-pi-sync.json` pending rather than guessing a URL.

## Verify and run sync

1. Check repository visibility and write access in GitHub settings. Verify SSH authentication and remote read access locally.
   ```sh
   ssh -T git@github.com
   git ls-remote <your-ssh-repo-url>
   ```
2. Reload Pi and check `/sync-status` (or click the right-side `pi-sync` pill in Starline). Manual mode makes no network calls until you run a transfer command.

Available commands:

- `/sync-push` — push configured `sessions` files to the private remote.
- `/sync-pull` — pull remote files into `<agent-dir>`; conflicting local files are backed up to `amox-pi-sync-backups` before replacement, local-only files stay untouched, and active sessions are never overwritten.
- `/sync-settings` — edit paths or sync mode, inspect diagnostics, view backups, or run manual backup cleanup.

Check sessions for sensitive tokens and back up local data before pushing or pulling, and avoid pushing from two machines at once. Bootstrap never runs `/sync-push`, `/sync-pull`, `/sync-setup`, or cleanup (`/sync-setup` only writes config and is not needed to verify deployment). Keep real credentials, session files, sync checkouts, and backups out of this repository.

Related: [README](../README.md) · [Pi setup](../setup_for_pi.md)
