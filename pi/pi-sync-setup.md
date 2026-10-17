# Pi Sync: configure your own sessions repository

English | [简体中文](pi-sync-setup.zh-CN.md)

Pi Sync is installed as `npm:pi-sync-suite`. Installation alone does not configure a destination. Each user must supply a **private sessions repository they control**, separate from this bootstrap repository and the extension's source repository. Do not use the bootstrap author's personal sessions repository.

## 1. Prepare your repository and SSH access

1. Create a dedicated private GitHub repository, or reuse your own private sessions repository. It must allow this computer to read and push. A new empty repository is sufficient; Pi Sync can clone it and create the first snapshot commit when you explicitly push.
2. Copy its SSH URL, in the form `git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git`. Replace both placeholder names. The repository name is your choice; it does not have to be `sessions`.
3. Set up this computer's SSH key with GitHub. Add only the **public key** to GitHub; never put the private key or access tokens in this project, the sessions repository, or a chat.
4. Check SSH authentication before syncing. These checks do not upload sessions:

   ```sh
   ssh -T git@github.com
   git ls-remote git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git
   ```

   Replace the placeholders before running the second command. GitHub's successful SSH greeting can still return exit code 1; read the message. An empty repository can produce no refs from `git ls-remote`; a successful exit indicates read access, not proof of write access or repository privacy. Check **Private** and your write permission in GitHub's repository settings. If you see `Permission denied (publickey)` or `Repository not found`, fix the key, account, URL or access permission first.

Pi Sync requires an SSH remote; it rejects HTTPS URLs. Do not add a token to the URL.

## 2. Adapt the local configuration

Use the full [pi-sync-suite.json](pi-sync-suite.json) template, not just the excerpt below. Its two machine/user-specific fields must be filled in:

| Field | Required value |
| --- | --- |
| `repoUrl` | Your private repository's actual SSH URL; replace `YOUR_GITHUB_USERNAME` and `YOUR_PRIVATE_SESSIONS_REPO` |
| `repoDir` | Replace `{{SYNC_REPO_DIR}}` with the absolute path to a dedicated local checkout, normally `<agent-dir>/sync-suite-repo` |

`<agent-dir>` is `PI_CODING_AGENT_DIR`, otherwise `~/.pi/agent`. Resolve it to an actual absolute path: do not leave `~`, environment-variable expressions or placeholders in `repoDir`. For Windows JSON, forward slashes avoid backslash escaping, for example `C:/Users/yourname/.pi/agent/sync-suite-repo`. Use your own home path on macOS or Linux.

For example, these are the fields to change, **not a complete configuration**:

```json
{
  "repoUrl": "git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git",
  "repoDir": "{{SYNC_REPO_DIR}}"
}
```

Back up an existing `<agent-dir>/pi-sync-suite.json` before editing. If it already points to your own repository, preserve `repoUrl`, `repoDir` and local sync timestamps; do not overwrite them with template values. A populated `repoDir` must belong to the intended remote. If it points elsewhere, stop and review it rather than reusing or deleting it. The checkout must not be this bootstrap directory or an unrelated working repository.

Save the completed configuration to `<agent-dir>/pi-sync-suite.json`, not into the public bootstrap repository. If the repository or path is not yet known, leave Pi Sync **pending configuration** and continue other installation work. Do not claim it is ready or run sync commands with placeholders.

## 3. Keep the manual session/mission policy

The full template selects only `sessions` and `missions`. It keeps `autoMode: "manual"`, enables raw session sync, and disables chat automation, environment-install prompts and automatic cleanup. Empty `safeRootFiles` and `safeDirs` mean it does not sync settings, Skills or the default configuration paths. Keep `syncLocalPackagePaths: false`; the maintained lean packages now install from portable npm sources on each computer, not synced local package directories.

Raw sessions and missions can contain prompts, model output, tool logs, file paths and secrets. A private repository and Pi Sync's secret scan do not guarantee that all sensitive data is excluded. Review what you intend to upload and keep the other sensitive-name exclusions intact.

Do **not** run `/sync-setup` as an inert installation check: upstream setup uses full-auto defaults and performs an initial pull and push, which can apply remote files and upload local data. This bootstrap instead deploys the completed manual-mode file directly. Bootstrap must not create a remote repository, change SSH keys, synchronize, or clean up data without a separate user request.

## 4. Check first, sync only when you intend to

After saving the configuration, restart Pi or run `/reload`. Open `/sync-settings` → `View Status` and check the remote, local checkout and manual mode without initiating a transfer.

Only after checking privacy, permissions, scope and local backups:

- On the source computer, explicitly run `/sync-push` to upload the selected snapshot. This is a real upload, not a verification command.
- On another computer, install the extensions separately and configure the **same remote**, but use that computer's own absolute `repoDir`. Back up its local data before explicitly running `/sync-pull`; applying a remote snapshot can replace local files within the selected scope.
- Avoid simultaneous uploads from multiple computers. If Git reports a conflict, inspect it; do not force-push or delete the checkout to bypass it.

The local `pi-sync-suite.json` is not synced. Configure each computer separately. Keep actual sessions, missions, checkout contents, private keys and backups out of this bootstrap repository.

[Back to README](../README.md) · [Pi installation instructions](../setup_for_pi.md)
