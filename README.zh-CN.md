# amox-agent-bootstrap

[English](README.md) | 简体中文

![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![Hosts](https://img.shields.io/badge/hosts-Codex%20%7C%20Pi-blue?style=flat-square)
![Node](https://img.shields.io/badge/Node.js-%3E%3D22.19-3c873a?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12%20(codex)-3776ab?style=flat-square)

[快速开始](#快速开始) • [Pi 默认配置](#pi-默认配置) • [目录结构](#目录结构) • [维护与检查](#维护与检查)

面向 Windows、macOS 和 Linux 的个人 Codex 与 Pi 部署指南和配置模板。将对应的 setup 文档交给已安装的 Agent，即可检查当前环境、复用兼容软件、补齐缺失的包与 Skills 并完成验证，同时保留无关设置与本地凭据。

## 快速开始

先安装 Codex 或 Pi，再发送下面的提示词。对应的 setup 文档会继续处理 Miniforge/Conda、共享的 Python 3.12 `codex` 环境、Skills 与 Task Router。

### 配置 Codex

```text
阅读 https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup.md，
按照其中的说明配置这台电脑。完成安装、验证结果，
并说明还有哪些事项需要我提供信息或处理。
```

[setup.md](setup.md) 负责安装 Codex Skills、Task Router（`codex -p task-routing`）、`config.toml` 默认项与 Python 依赖，并将 [templates/AGENTS.md](templates/AGENTS.md) 渲染到 `CODEX_HOME`。

### 配置 Pi

```text
阅读 https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup_for_pi.md，
按照其中的说明配置这台电脑。获取文中引用的 pi/ 文件，
完成安装、验证结果，并说明还有哪些事项需要我提供信息或处理。
```

[setup_for_pi.md](setup_for_pi.md) 负责安装 Pi 扩展、Skills、Task Router、Python 依赖及 [pi/ 配置模板](pi/README.md)。Pi 需要兼容的 Node.js（当前包要求 `>=22.19`）和 Bash；Agent 会在安装前核对上游版本要求。

## Pi 默认配置

| 模块 | 默认设置 |
| --- | --- |
| 工具 | 通过 `defaultTools: ["+codemode"]` 在常规工具基础上启用内置 codemode |
| 自动可用 Skills | `create-readme`、`design-taste-frontend`、`humanizer` |
| 仅显式调用 Skills | `anti-defensive-writing`、`amox-grill-me`、`meeting-summary-html`、`ian-xiaohei-illustrations`、`de-ai` 及三个 `autoresearch-*` 包装文件 |
| 界面 | `pi-tidy` 启用消息边框、用户消息右对齐（`userMessageAlign: "right"`）与 `syntaxKeyword` 边框色，最终回复沿用包默认样式，并提供工具折叠与 diff；`pi-starline` 提供编辑器与可点击胶囊底栏 |
| 外观 | 将 Pi 和当前终端都设为 Catppuccin Mocha；使用者自行安装 Maple Mono NF CN 字体并设置 95% 终端不透明度（[外观指南](pi/appearance.zh-CN.md)） |
| 网页搜索 | 优先走 `exa`，遇到指定可恢复错误时回退到 `sub2api-gpt-only`（`gpt-6.2-sol`） |
| 回复摘要 | `amox-high-level`，通过 `/hl` 或 `+hl` 按需生成 |
| Task Router | 通过 `/skill:task-routing` 显式调用；共享规则位于 `<router-checkout>/AGENTS.md`，子角色启用 `skills: true` 与受限 `codemode`，不在 Pi 全局指令中写入 Router 区块 |
| 持久目标 | `pi-goal-x-lean` 配合 `pi-subagents-lean` 与工作流，仅在执行 `/goal` 时启动 |
| 会话同步 | `amox-pi-sync`，采用手动模式且仅同步 `sessions` 到[你自己的私有 SSH 仓库](pi/pi-sync-setup.zh-CN.md) |
| Autoresearch | `pi-autoresearch`（`skills: []`），通过仅显式调用的包装文件与 `/autoresearch` 命令暴露 |

包安装顺序、旧版界面扩展清理与 Skills 部署见 [setup_for_pi.md](setup_for_pi.md)；各模板目标路径与搜索回退细节见 [pi/README.md](pi/README.md)。

> [!IMPORTANT]
> 缺失的 API Key 和 SSH 仓库地址直接在本机文件中填写，不要发到聊天窗口。Bootstrap 会将缺少凭据或远端的组件记为待配置，不会执行同步传输、基准测试或付费模型与生图调用。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| [setup.md](setup.md) | Codex 自动部署与验收步骤 |
| [setup_for_pi.md](setup_for_pi.md) | Pi 自动部署、包迁移与验收步骤 |
| [templates/AGENTS.md](templates/AGENTS.md) | Codex 全局指令模板 |
| [pi/](pi/README.md) | Pi 配置模板、Catppuccin Mocha 主题、搜索密钥读取脚本及外观／同步指南 |
| [skills/amox-grill-me/](skills/amox-grill-me/SKILL.md) | 内置的仅显式调用方案追问 Skill |
| [skills/de-ai/](skills/de-ai/README.zh-CN.md) | 跨语系翻译链与确定性正则改写工具（支持 `.docx`、`.md`、`.txt`） |
| `tests/` | 基于 Node.js 的离线契约与配置测试 |

## 维护与检查

修改本仓库中的 setup 文档与模板文件即可更新后续部署。切勿将真实凭据、会话记录、同步副本、缓存和备份提交到 Git。

仅更新已安装的 Pi 扩展包（不升级 Pi 本体）：

```sh
pi update --extensions
```

修改配置或更新扩展后重载或重启 Pi。

在仓库根目录运行离线检查：

```sh
node --test tests/*.test.cjs
```

测试使用本地临时样本校验 JSON 模板、Skills 与 Router 契约、本地 Markdown 链接及凭据辅助脚本的失败保护，不访问在线搜索或真实模型接口。
