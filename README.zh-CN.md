# amox-agent-bootstrap

[English](README.md) | 简体中文

个人 Codex 和 Pi 的部署说明及配置模板，支持 Windows、macOS 和 Linux。把对应的 setup 文档交给 Agent，它会检查电脑、复用兼容软件、安装缺少的组件并验证结果，同时保留无关配置和已有凭据。

## 开始使用

先安装要用的 Codex 或 Pi，再发送对应的提示词。其余依赖由 setup 文档安排，包括 Conda 和共享 Python `codex` 环境。

### Codex

```text
阅读 https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup.md，
按照其中的说明配置这台电脑。完成安装、验证结果，
并说明还有哪些事项需要我提供信息或处理。
```

[setup.md](setup.md) 包含 Skills、Task Router、Codex 设置和 Python 依赖；[templates/AGENTS.md](templates/AGENTS.md) 提供全局指令。

### Pi

```text
阅读 https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup_for_pi.md，
按照其中的说明配置这台电脑。获取文中引用的 pi/ 文件，
完成安装、验证结果，并说明还有哪些事项需要我提供信息或处理。
```

[setup_for_pi.md](setup_for_pi.md) 包含扩展、Skills、Task Router、Python 依赖和 [Pi 配置模板](pi/README.md)。Pi 需要兼容的 Node.js 和 Bash；Agent 会先核对当前上游要求，再决定是否安装。

## Pi 默认配置

| 组件 | 配置 |
| --- | --- |
| 工具 | 通过 `defaultTools: ["+codemode"]` 启用内置 codemode，保留常用工具 |
| Skills | `create-readme` 允许自动调用；`humanizer` 用于文字编辑 |
| 仅显式调用的 Skills | `anti-defensive-writing`、`amox-grill-me`、`meeting-summary-html` 和 `ian-xiaohei-illustrations` |
| 界面 | pi-tidy 负责工具折叠和 diff；pi-starline 最后加载，提供输入框、用户消息边框和可点击的胶囊底栏 |
| 外观 | Catppuccin Mocha、Maple Mono NF CN、终端背景 95% 不透明度 |
| 搜索 | 优先使用 Sub2API 转发的 Codex/OpenAI 搜索，遇到指定的可恢复故障时回退 Exa |
| Task Router | 通过 `/skill:task-routing` 显式启用；共享规则保存在 Router 仓库，子 Agent 可用 Skills 和受限 codemode，不在 Pi 全局指令中添加 Router 区块 |
| Pi Sync | 仅手动同步会话和任务，目标为用户自己的私有仓库 |
| Autoresearch | pi-autoresearch，配套三个仅显式调用的 Skill 包装文件；按要求启动实验循环 |

包顺序、界面替换和 Skills 安装见 [Pi 部署说明](setup_for_pi.md)；凭据路径与搜索路由见 [Pi 配置模板](pi/README.md)。Bootstrap 将 **Pi 和当前终端都设为 Catppuccin Mocha**。字体安装和不透明度由使用者设置，具体见[外观指南](pi/appearance.zh-CN.md)。

> [!IMPORTANT]
> 缺少的凭据在本机填写，不在聊天中传递。Pi Sync 需要[你自己的私有 SSH 仓库](pi/pi-sync-setup.zh-CN.md)。bootstrap 不执行同步或付费模型、生图测试；凭据或同步目标缺失时，对应组件保留为待配置。

## 维护与验证

修改对应的 setup 文档和模板，即可调整后续部署。真实凭据、会话、缓存和备份不入 Git。

使用 `pi update --extensions` 更新 Pi 扩展包，该命令不更新 Pi 本身。配置变更后重载或重启 Pi。安装与迁移要求见 [Pi 部署说明](setup_for_pi.md)。

在仓库根目录用 Node.js 运行离线检查：

```sh
node --test tests/*.test.cjs
```

检查会验证配置模板，并使用本地凭据测试样本，不调用搜索服务，也不验证真实模型的访问权限。
