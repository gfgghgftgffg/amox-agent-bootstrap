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

[setup_for_pi.md](setup_for_pi.md) 包含九个包、八个 Skills、Task Router、Python 依赖和 [Pi 配置模板](pi/README.md)。Pi 需要兼容的 Node.js 和 Bash；Agent 会先核对当前上游要求，再决定是否安装。

## Pi 默认配置

| 组件 | 配置 |
| --- | --- |
| 工具 | 通过 `defaultTools: ["+codemode"]` 启用内置 codemode，保留常用工具 |
| Skills | `create-readme` 允许自动调用；`humanizer` 和 `shuorenhua` 用于文字编辑 |
| 仅显式调用的 Skills | `grilling`、`meeting-summary-html` 和 `ian-xiaohei-illustrations` |
| 界面 | pi-pretty 使用 `claudecode` 工具样式；open-tui 最后加载，提供输入框和内联底栏 |
| 搜索 | 优先使用 Sub2API 转发的 Codex/OpenAI 搜索，遇到指定的可恢复故障时回退 Exa |
| Task Router | 通过 `/skill:task-routing` 显式启用 |
| Pi Sync | 仅手动同步会话和任务，目标为用户自己的私有仓库 |

`create-readme` 来自 [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/create-readme)，只安装该 Skill，不安装整个合集。Pi 启动时只加入它的名称、简短 description 和路径，完整指令按需读取。编写 README 时用它安排结构，再用 `humanizer` / `shuorenhua` 优化中英文表达。

保留 [settings.json](pi/settings.json) 中的插件顺序，open-tui 最后加载，避免承载内联底栏的输入框被 pretty 替换。[Open-tui 配置](pi/open-tui.json) 开启内联底栏、中文设置界面和会话名，隐藏扩展状态行，关闭单轮遥测费用，底栏累计费用仍显示。独立插件组件不受扩展状态行开关控制。

不默认安装 statusline。保留用户已有的安装，全部安装和验证完成后再询问是否删除；未经明确同意，不删除或禁用。

[搜索配置](pi/README.md#search-routing)使用独立于主对话的模型，读取本机现有 relay token，不另存一份密钥。部署时适配凭据脚本路径和网关地址，实测搜索须另行获得同意。

> [!IMPORTANT]
> 缺少的凭据在本机填写，不在聊天中传递。Pi Sync 需要[你自己的私有 SSH 仓库](pi/pi-sync-setup.zh-CN.md)。bootstrap 不执行同步或付费模型、生图测试；凭据或同步目标缺失时，对应组件保留为待配置。

## 维护与验证

修改对应的 setup 文档和模板，即可调整后续部署。Codex 与 Pi 使用独立的指令文件和安装目标；模板不是任何电脑的实时安装清单。真实凭据、会话、缓存和备份不入 Git。

三个 amox lean 包已在 npm 公开发布。安装时不固定包版本，按需执行 `pi update --extensions`，该命令不更新 Pi 本身。迁移已有本地来源须经同意，并替换原注册项，避免重复加载。配置变更后重载或重启 Pi，再检查工具和终端的实际表现。

在仓库根目录用 Node.js 运行离线检查：

```sh
node --test tests/*.test.cjs
```

检查会验证配置模板，并使用本地凭据测试样本，不调用搜索服务，也不验证真实模型的访问权限。
