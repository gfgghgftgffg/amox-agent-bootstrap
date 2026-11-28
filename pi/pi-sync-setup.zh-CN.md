# Pi Sync 配置指南

[English](pi-sync-setup.md) | 简体中文

在每台电脑上安装 `npm:@gfgghgftgffg/amox-pi-sync`，通过你自己的私有 SSH Git 仓库手动同步 Pi 会话文件。切勿将同步远端指向本 bootstrap 仓库。

若 `settings.json` 中仍注册着 `pi-sync-suite` 或本地路径版 `amox-pi-sync`，移除旧注册项并保留原有数据与备份目录，确保同时只加载一个同步扩展。

## 配置 `amox-pi-sync.json`

先备份已有同步配置，再将 [amox-pi-sync.json](amox-pi-sync.json) 部署到 `<agent-dir>/amox-pi-sync.json`（`<agent-dir>` 取 `PI_CODING_AGENT_DIR`，默认 `~/.pi/agent`）：

| 字段 | 取值与规则 |
| --- | --- |
| `repoUrl` | 个人私有会话仓库的 SSH 地址（替换 `YOUR_GITHUB_USERNAME` 与 `YOUR_PRIVATE_SESSIONS_REPO`） |
| `repoDir` | 专用本地同步副本路径；将 `{{SYNC_REPO_DIR}}` 替换为本机绝对路径（通常为 `<agent-dir>/amox-pi-sync-repo`） |
| `mode` | `"manual"`（Pi 启动时不自动联网拉取或推送） |
| `paths` | `["sessions"]`，相对于 `<agent-dir>` 解析 |
| `retention` | `<agent-dir>/amox-pi-sync-backups` 中超出 `20` 份或超过 `180` 天的备份会列为清理候选。清理须手动预览并确认 |

重跑部署时保留已配置的有效 `repoUrl`、`repoDir` 与运行参数；多台电脑共用同一个远端 `repoUrl`，各自使用本机独立的 `repoDir`。若尚未准备私有仓库，将该项记为待配置，不要虚构仓库地址。

### 从 `pi-sync-suite` 迁移

迁移时可复用 `pi-sync-suite.json` 中已确认的 SSH `repoUrl`，同时将 `repoDir` 指向新建的 `<agent-dir>/amox-pi-sync-repo`，不要复用旧的 `sync-suite-repo`。在 `amox-pi-sync.json` 尚未生成前，扩展可以只读兼容旧配置文件，保存设置时写入新的 `amox-pi-sync.json`。不要迁移旧版专有的 `chat`、`environment`、`policy` 或 `syncLocalPackagePaths` 字段。

## 验证与日常命令

1. 在 GitHub 仓库设置中确认仓库为私有并检查写入权限，再在本机验证 SSH 认证和远端读取权限。
   ```sh
   ssh -T git@github.com
   git ls-remote <你的SSH仓库地址>
   ```
2. 重载 Pi，运行 `/sync-status`（或点击 Starline 右侧的 `pi-sync` 胶囊）核对配置状态。手动模式下启动不会访问远端。

常用命令：

- `/sync-push` — 将配置的 `sessions` 文件推送到私有远端仓库。
- `/sync-pull` — 拉取远端文件；同名且内容不同的本地文件会先备份到 `amox-pi-sync-backups` 再替换，本地独有文件保留不变，当前活跃会话不会被覆盖。
- `/sync-settings` — 调整同步路径与模式、查看诊断信息、管理备份或执行手动清理。

推送或拉取前先检查会话中是否包含敏感信息并做好本地备份，避免多台设备同时推送。Bootstrap 期间不执行 `/sync-push`、`/sync-pull`、`/sync-setup` 或清理操作（`/sync-setup` 仅用于写入配置，验收无需调用）。切勿将真实凭据、会话记录、本地同步副本或备份提交到本仓库。

相关文档：[README](../README.zh-CN.md) · [Pi 部署说明](../setup_for_pi.md)
