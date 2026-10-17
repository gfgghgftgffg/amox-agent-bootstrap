# Pi Sync 配置

[English](pi-sync-setup.md) | 简体中文

`npm:pi-sync-suite` 需要你自己的私有 sessions 仓库和 SSH 读写权限。不要使用本 bootstrap 仓库、插件源码仓库或作者的个人仓库。每台电脑分别安装插件。

## 配置

将完整的 [pi-sync-suite.json](pi-sync-suite.json) 部署到 `<agent-dir>/pi-sync-suite.json`。`<agent-dir>` 由 `PI_CODING_AGENT_DIR` 指定，默认 `~/.pi/agent`。

| 字段 | 应填写的值 |
| --- | --- |
| `repoUrl` | 你自己的私有仓库 SSH 地址，替换 `YOUR_GITHUB_USERNAME` 和 `YOUR_PRIVATE_SESSIONS_REPO`，不支持 HTTPS |
| `repoDir` | 将 `{{SYNC_REPO_DIR}}` 替换为专用本地副本的绝对路径，通常为 `<agent-dir>/sync-suite-repo` |

写入 JSON 前解析实际路径；Windows 使用转义反斜杠或正斜杠。先备份已有配置，保留有效远端、本地副本和同步时间戳。非空副本必须对应目标远端，不能是本项目或无关仓库。其他电脑使用同一远端，但填写各自本地路径。仓库或路径信息缺失时，Pi Sync 标记为待配置。

保留模板的手动策略：只同步原始 `sessions` 和 `missions`，不自动同步聊天或清理，`safeRootFiles`、`safeDirs` 为空，`syncLocalPackagePaths: false`。保留其他敏感名称排除规则。本机配置不参与同步，每台主机分别部署。维护中的 lean 包在每台电脑上从 npm 安装，不同步本地包目录。

## 验证

配置 SSH 权限，不暴露私钥。运行前替换占位符：

```sh
ssh -T git@github.com
git ls-remote git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git
```

GitHub 的 SSH 成功提示可能返回退出码 1。`git ls-remote` 只证明读取权限，不证明写权限或隐私；空仓库可能不返回 refs。在 GitHub 设置中确认 **Private** 和写权限。重启 Pi 或 `/reload`，通过 `/sync-settings` → `View Status` 查看状态，不传输数据。

## 手动使用

未经另行要求，bootstrap 不创建仓库、修改 SSH 密钥、同步或清理数据。不要用 `/sync-setup` 验证安装：它默认 full-auto，会执行首次拉取和推送。

明确传输前，检查所选数据并备份本地内容。原始会话和任务可能包含密钥，私有 Git 和敏感信息扫描都不能保证排除它们。

- `/sync-push` 上传源电脑的所选快照。
- `/sync-pull` 将快照应用到另一台电脑，可能替换同步范围内的本地文件。
- 避免同时上传。遇到冲突先审查，不通过强制推送或删除本地副本绕过。

真实凭据、会话、任务、本地仓库副本和备份不进入 bootstrap 仓库。

[README](../README.zh-CN.md) · [Pi 部署](../setup_for_pi.md)
