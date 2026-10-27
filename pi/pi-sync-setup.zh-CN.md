# Pi Sync 配置

[English](pi-sync-setup.md) | 简体中文

每台电脑安装 `npm:pi-sync-suite`。使用你自己的**私有仓库和 SSH 读写权限**，不要使用本 bootstrap 仓库。

## 配置

将 [pi-sync-suite.json](pi-sync-suite.json) 部署到 `<agent-dir>/pi-sync-suite.json`。`<agent-dir>` 由 `PI_CODING_AGENT_DIR` 指定，默认 `~/.pi/agent`。

| 字段 | 设置 |
| --- | --- |
| `repoUrl` | 私有仓库 SSH 地址，替换两个 `YOUR_*` 占位符 |
| `repoDir` | 将 `{{SYNC_REPO_DIR}}` 替换为专用副本的绝对路径，通常为 `<agent-dir>/sync-suite-repo` |
| 同步策略 | 手动，仅 `sessions` 和 `missions` |
| 自动聊天同步／清理 | 关闭 |
| `syncLocalPackagePaths` | `false` |

先备份已有配置，保留有效远端、本地副本和时间戳。各电脑使用相同远端、各自的本地路径，其余策略沿用模板。仓库信息缺失时标记为待配置。

## 验证与使用

在 GitHub 设置中确认仓库为私有且有写权限。通过 `ssh -T git@github.com` 和 `git ls-remote <你的SSH仓库地址>` 检查 SSH／读取权限。重载 Pi，在 `/sync-settings` → `View Status` 查看状态。

- `/sync-push`：上传源电脑的所选快照。
- `/sync-pull`：在另一台电脑应用快照，可能替换同步范围内的文件。

传输前检查会话中的敏感内容并备份本地数据，避免多台电脑同时推送。Bootstrap 不执行同步或清理，也不用 `/sync-setup` 验证安装，因为它会执行首次拉取和推送。真实凭据、会话、本地副本和备份不进入本仓库。

[README](../README.zh-CN.md) · [Pi 部署](../setup_for_pi.md)
