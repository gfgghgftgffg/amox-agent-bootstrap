# Pi Sync 配置

[English](pi-sync-setup.md) | 简体中文

每台电脑安装 `npm:@gfgghgftgffg/amox-pi-sync`。使用你自己的**私有仓库和 SSH 读写权限**，不要使用本 bootstrap 仓库。移除被替换的 `pi-sync-suite` 或本地 amox-pi-sync 注册，保留其文件和备份，只加载一个同步扩展。

## 配置

将 [amox-pi-sync.json](amox-pi-sync.json) 部署到 `<agent-dir>/amox-pi-sync.json`。`<agent-dir>` 由 `PI_CODING_AGENT_DIR` 指定，默认 `~/.pi/agent`。

| 字段 | 设置 |
| --- | --- |
| `repoUrl` | 私有仓库 SSH 地址，替换两个 `YOUR_*` 占位符 |
| `repoDir` | 将 `{{SYNC_REPO_DIR}}` 替换为专用副本的绝对路径，通常为 `<agent-dir>/amox-pi-sync-repo` |
| `mode` | `manual`，启动时不访问网络 |
| `paths` | `["sessions"]`，相对于 agent 数据目录 |
| `retention` | 保留最新 20 份、最长 180 天；清理需手动预览并确认 |

先备份已有配置，保留有效的 amox 远端、本地副本和运行时字段。各电脑使用相同远端、各自的本地路径。仓库信息缺失时标记为待配置。

从 `pi-sync-suite.json` 迁移时保留 SSH 远端，使用新的 `amox-pi-sync-repo` 副本，不复用旧 `sync-suite-repo`。新配置不存在时，扩展可读取旧文件而不改写它；保存时写入新文件。amox 配置不使用旧版的 `chat`、`environment`、`policy` 或 `syncLocalPackagePaths` 字段。备份存放在 `<agent-dir>/amox-pi-sync-backups`。

## 验证与使用

在 GitHub 设置中确认仓库为私有且有写权限。可通过 `ssh -T git@github.com` 和 `git ls-remote <你的SSH仓库地址>` 检查 SSH／读取权限。重载 Pi，查看 `/sync-status` 或点击 Starline 的 `pi-sync` 胶囊。手动模式启动时不连接远端。

- `/sync-push`：上传选中的原始 agent 文件。
- `/sync-pull`：应用远端文件，同路径内容不同时先备份再替换；保留本地独有文件，不得覆盖活跃会话。
- `/sync-settings`：设置路径和模式、管理备份、查看诊断及手动清理。

传输前检查会话中的敏感内容并备份本地数据，避免多台电脑同时推送。Bootstrap 不执行同步、setup 命令或清理。`/sync-setup` 只保存配置、不传输数据，bootstrap 验证无需调用它。真实凭据、会话、本地副本和备份不进入本仓库。

[README](../README.zh-CN.md) · [Pi 部署](../setup_for_pi.md)
