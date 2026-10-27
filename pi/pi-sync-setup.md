# Pi Sync setup

English | [简体中文](pi-sync-setup.zh-CN.md)

Install `npm:pi-sync-suite` on each computer. Use your own **private repository with SSH read/write access**, not this bootstrap repository.

## Configuration

Deploy [pi-sync-suite.json](pi-sync-suite.json) to `<agent-dir>/pi-sync-suite.json`, where `<agent-dir>` is `PI_CODING_AGENT_DIR` or `~/.pi/agent`.

| Field | Value |
| --- | --- |
| `repoUrl` | Your private repository's SSH URL; replace both `YOUR_*` placeholders |
| `repoDir` | Replace `{{SYNC_REPO_DIR}}` with a dedicated absolute checkout path, normally `<agent-dir>/sync-suite-repo` |
| Sync policy | Manual; only `sessions` and `missions` |
| Automatic chat sync / cleanup | Disabled |
| `syncLocalPackagePaths` | `false` |

Back up existing configuration and preserve its valid remote, checkout and timestamps. Each computer uses the same remote but its own local path. Keep all other template policy values unchanged. Missing repository details leave sync pending.

## Verification and use

Check repository privacy and write permission in GitHub settings. Test SSH/read access with `ssh -T git@github.com` and `git ls-remote <your-ssh-repo-url>`. Reload Pi and inspect `/sync-settings` → `View Status`.

- `/sync-push`: upload the source computer's selected snapshot.
- `/sync-pull`: apply the snapshot on another computer; files in scope can be replaced.

Review sessions for secrets and back up local data before transfers. Avoid simultaneous pushes. Bootstrap does not run transfers or cleanup; do not run `/sync-setup` for verification because it performs an initial pull/push. Keep credentials, sessions, checkouts and backups out of this repository.

[README](../README.md) · [Pi deployment](../setup_for_pi.md)
