# Pi Sync setup

English | [简体中文](pi-sync-setup.zh-CN.md)

`npm:pi-sync-suite` needs your own private sessions repository with SSH read/write access. Do not use this bootstrap repository, the extension source or the author's personal repository. Install the package separately on every computer.

## Configuration

Deploy the full [pi-sync-suite.json](pi-sync-suite.json) to `<agent-dir>/pi-sync-suite.json`. `<agent-dir>` is `PI_CODING_AGENT_DIR`, otherwise `~/.pi/agent`.

| Field | Required value |
| --- | --- |
| `repoUrl` | Your private repository's SSH URL, replacing `YOUR_GITHUB_USERNAME` and `YOUR_PRIVATE_SESSIONS_REPO`; HTTPS is unsupported |
| `repoDir` | Replace `{{SYNC_REPO_DIR}}` with an absolute dedicated checkout path, normally `<agent-dir>/sync-suite-repo` |

Resolve paths before writing JSON; use escaped backslashes or forward slashes on Windows. Back up an existing configuration and preserve its valid remote, checkout and sync timestamps. A populated checkout must match the intended remote and must not be this project or an unrelated repository. Other computers use the same remote with their own local paths. Missing repository/path details leave Pi Sync pending configuration.

Keep the template's manual policy: only raw `sessions` and `missions`, no automatic chat sync or cleanup, empty `safeRootFiles`/`safeDirs`, and `syncLocalPackagePaths: false`. Preserve other sensitive-name exclusions. The local configuration is not synced and must be deployed separately on each host. Install the maintained lean packages from npm on each computer rather than syncing local package directories.

## Verification

Set up SSH access without exposing private keys. Replace placeholders before running:

```sh
ssh -T git@github.com
git ls-remote git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git
```

GitHub's successful SSH greeting may exit 1. `git ls-remote` verifies read access, not write permission or privacy; an empty repository may return no refs. Confirm **Private** and write permission in GitHub settings. Restart Pi or `/reload`, then inspect `/sync-settings` → `View Status` without transferring data.

## Manual use

Bootstrap must not create repositories, change SSH keys, synchronize or clean up data without a separate request. Do not run `/sync-setup` as verification: its full-auto defaults perform an initial pull and push.

Before an explicit transfer, review the selected data and take local backups. Raw sessions/missions may contain secrets; private Git and secret scanning cannot guarantee their exclusion.

- `/sync-push` uploads the source computer's selected snapshot.
- `/sync-pull` applies it on another computer and can replace local files in scope.
- Avoid simultaneous uploads. Review conflicts; do not force-push or delete the checkout to bypass them.

Keep populated credentials, sessions, missions, checkouts and backups out of this bootstrap repository.

[README](../README.md) · [Pi deployment](../setup_for_pi.md)
