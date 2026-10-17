# Pi Sync：配置你自己的 sessions 仓库

[English](pi-sync-setup.md) | 简体中文

Pi Sync 的安装包是 `npm:pi-sync-suite`。装好插件不代表已经配置了同步目标。每位用户都需要准备一个**由自己控制的私有 sessions 仓库**，与本 bootstrap 仓库、插件源码仓库分开。不要使用 bootstrap 作者的个人 sessions 仓库。

## 1. 准备仓库和 SSH 访问权限

1. 在 GitHub 上新建一个专用的私有仓库，或使用你已有的私有 sessions 仓库。这台电脑需要有读取和推送权限。新建的空仓库也可以；你明确执行推送时，Pi Sync 可以克隆它并创建首次快照提交。
2. 复制仓库的 SSH 地址，格式为 `git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git`，替换其中的用户名和仓库名。仓库名由你决定，不一定要叫 `sessions`。
3. 为这台电脑配置 GitHub SSH 密钥。只把**公钥**添加到 GitHub；不要把私钥或访问令牌放进本项目、sessions 仓库或聊天中。
4. 同步前先检查 SSH 认证。以下检查不会上传会话：

   ```sh
   ssh -T git@github.com
   git ls-remote git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git
   ```

   第二条命令要先替换占位符。GitHub 的 SSH 认证成功提示也可能返回退出码 1，要看提示内容。空仓库的 `git ls-remote` 可能没有输出；成功退出只能说明有读取权限，不能证明有写入权限或仓库为私有。请在 GitHub 仓库设置中确认 **Private** 和你的写入权限。遇到 `Permission denied (publickey)` 或 `Repository not found`，先检查密钥、账号、地址和访问权限。

Pi Sync 要求使用 SSH 地址，不接受 HTTPS 地址。不要在地址里填访问令牌。

## 2. 修改本机配置

使用完整的 [pi-sync-suite.json](pi-sync-suite.json) 模板，不要只复制下方的片段。以下两个与用户和电脑有关的字段必须填写：

| 字段 | 应填写的值 |
| --- | --- |
| `repoUrl` | 你自己的私有仓库 SSH 地址；替换 `YOUR_GITHUB_USERNAME` 和 `YOUR_PRIVATE_SESSIONS_REPO` |
| `repoDir` | 将 `{{SYNC_REPO_DIR}}` 替换为专用本地仓库副本的绝对路径，通常是 `<agent-dir>/sync-suite-repo` |

`<agent-dir>` 由 `PI_CODING_AGENT_DIR` 指定，未设置时为 `~/.pi/agent`。填写时要解析成实际绝对路径，不要在 `repoDir` 中留下 `~`、环境变量表达式或占位符。Windows 的 JSON 路径可用正斜杠，避免反斜杠转义，例如 `C:/Users/yourname/.pi/agent/sync-suite-repo`。macOS 和 Linux 填写各自实际的用户目录。

例如，需要替换的是这两个字段，**这不是完整配置**：

```json
{
  "repoUrl": "git@github.com:YOUR_GITHUB_USERNAME/YOUR_PRIVATE_SESSIONS_REPO.git",
  "repoDir": "{{SYNC_REPO_DIR}}"
}
```

修改前先备份已有的 `<agent-dir>/pi-sync-suite.json`。如果它已经指向你自己的仓库，保留原有的 `repoUrl`、`repoDir` 和本机同步时间戳，不要用模板覆盖。非空的 `repoDir` 必须对应你打算使用的远端；如果指向别处，先停下来核对，不要直接复用或删除。仓库副本不能是本 bootstrap 目录，也不能是无关项目的工作目录。

把填好的配置保存到本机的 `<agent-dir>/pi-sync-suite.json`，不要写回公开的 bootstrap 仓库。如果还没有确定仓库或路径，将 Pi Sync 标记为**待配置**，继续其他安装步骤。不要声称它已经可用，也不要带着占位符执行同步命令。

## 3. 保留手动会话／任务同步策略

完整模板只选择 `sessions` 和 `missions`。它使用 `autoMode: "manual"`，启用原始会话同步，关闭聊天自动化、环境工具安装提示和自动清理。`safeRootFiles`、`safeDirs` 留空，因此不会同步 settings、Skills 或默认配置路径。保持 `syncLocalPackagePaths: false`；维护中的 lean 包现在使用可移植的 npm 来源，在每台电脑上安装，不同步本地包目录。

原始会话和任务记录可能含有提示词、模型输出、工具日志、文件路径和密钥。私有仓库和 Pi Sync 的敏感信息扫描都不能保证排除所有敏感数据。上传前检查要同步的内容，保留其他敏感名称的排除规则。

**不要把 `/sync-setup` 当成只检查、不传输数据的安装命令。** 上游设置流程默认使用 full-auto，并会执行首次拉取和推送，可能应用远端文件、上传本机数据。本 bootstrap 改为直接部署填好的手动模式配置。没有用户另行要求，bootstrap 不应创建远端仓库、修改 SSH 密钥、同步或清理数据。

## 4. 先检查，再按需同步

保存配置后，重启 Pi 或执行 `/reload`。打开 `/sync-settings` → `View Status`，只查看远端地址、本地副本路径和手动模式，不发起传输。

确认仓库隐私、权限、同步范围并做好本地备份后：

- 在源电脑上，手动执行 `/sync-push` 上传所选快照。这是真正的上传，不是验证命令。
- 在另一台电脑上，分别安装扩展，配置**同一个远端**，但 `repoDir` 要填那台电脑自己的绝对路径。先备份其本地数据，再手动执行 `/sync-pull`；应用远端快照可能替换同步范围内的本地文件。
- 避免多台电脑同时上传。Git 报冲突时先检查，不要用强制推送或删除本地仓库副本来绕过。

本机的 `pi-sync-suite.json` 不会被同步，每台电脑都要单独配置。不要把真实会话、任务记录、仓库副本内容、私钥或备份放进本 bootstrap 仓库。

[返回 README](../README.zh-CN.md) · [Pi 安装说明](../setup_for_pi.md)
