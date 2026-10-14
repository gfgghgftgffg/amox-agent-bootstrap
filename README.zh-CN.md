# amox-agent-bootstrap

[English](README.md) | 简体中文

适用于 Windows、macOS 和 Linux 的个人 Codex 与 Pi 配置说明。把对应的配置文件交给你的 Agent，让它检查电脑、安装缺少的依赖，并配置工具和 Skills。

## Codex 使用方法

先安装 Codex，再发送以下提示词：

```text
阅读 https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup.md，
按照其中的说明配置这台电脑。完成安装、验证结果，
并说明还有哪些事项需要我提供信息或处理。
```

也可以下载或克隆本仓库，让 Codex 按照本地的 `setup.md` 操作。

## Codex 配置内容

- 检测 Conda，必要时安装 Miniforge。
- 使用共享的 `codex` 环境安装 Python 依赖，包括 `pypdf`。
- 任务路由：[task-router](https://github.com/gfgghgftgffg/task-router)（原名 `codex-task-router`）；profile 和 Skill 仍叫 `task-routing`。
- 会议总结：`meeting-summary-html`。
- 写作：`shuorenhua` 和 `humanizer`。
- 前端设计：`taste-skill`（`design-taste-frontend`）。
- 任务澄清：`grilling`，供手动调用。
- 固定的[全局 AGENTS.md 模板](templates/AGENTS.md)，只替换本机路径，不重复列出自动发现的 Skills。
- 全局 `config.toml` 中的记忆、防止空闲休眠和多 Agent 默认设置（30 个并发线程、`gpt-6-luna`、`medium` 思考强度），以及指定的 Windows 专用 daemon 设置。具体值见 [setup.md](setup.md)。

Codex 会选择适合当前平台的命令，复用兼容的安装，并保留现有配置。任务路由需要兼容的模型，并启用对应 profile；会议音视频转写需要 `DASHSCOPE_API_KEY`。纯文本会议材料的准备不需要 ASR 密钥。

修改 [setup.md](setup.md) 可自定义 Codex 的安装过程；修改 [templates/AGENTS.md](templates/AGENTS.md) 可调整其通用全局指令。

## Pi 使用方法

先安装 Pi，再发送以下提示词：

```text
阅读 https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup_for_pi.md，
按照其中的说明配置这台电脑。获取文中引用的 pi/ 文件，
完成安装、验证结果，并说明还有哪些事项需要我提供信息或处理。
```

也可以克隆本仓库，让 Pi 按照本地的 [setup_for_pi.md](setup_for_pi.md) 操作。这份说明以当前个人 Pi 安装为基准，并非将 Codex 配置直接转换而来。

## Pi 配置内容

- 共享的 `codex` Conda 环境和 `pypdf`。
- 10 个 Pi 包：7 个 npm 包（包括 Sub2API、retry、Pi Sync 和 UI 包），以及从 [amox_pi_extensions_lean](https://github.com/gfgghgftgffg/amox_pi_extensions_lean) 独立安装的 3 个 lean 包。安装来源和更新步骤见 [setup_for_pi.md](setup_for_pi.md)。
- 6 个用户 Skills：`design-taste-frontend`、`humanizer`、`meeting-summary-html`、`shuorenhua`、`grilling`，以及为 Pi 生成的 `task-routing`。
- 固定的 [Pi AGENTS.md](pi/AGENTS.md)、[settings](pi/settings.json)、路由配置，以及 [pi/](pi/README.md) 中不含敏感信息的插件配置。
- 访谈 Skill：`grilling`，仅供手动调用。两份配置说明都要求为它和 `meeting-summary-html` 设置 `disable-model-invocation: true`。
- 已脱敏的 [Sub2API 配置](pi/sub2api.json)，保留中转地址和 API 模式，以 `YOUR_API_KEY` 作为 token 占位符。
- [pi/subagents.json](pi/subagents.json) 中的 lean 子 Agent 配置，包括 50 个后台并发名额、模型显示、严格按角色派发和原生工作流。

- [Pi Sync 配置](pi/pi-sync-suite.json)：仅手动将会话和任务记录同步到用户的 SSH 仓库，配置时填入本机仓库副本的路径。bootstrap 不会执行同步或上传私人数据。

Pi 任务路由需要通过 `/skill:task-routing` 显式启用，使用维护中的 amox 仓库所提供的 `@gfgghgftgffg/pi-subagents-lean` 直接派发子 Agent 或运行原生工作流。搜索角色使用 `@gfgghgftgffg/pi-web-access-lean` 的 `web_access` 接口。新电脑上需要检查模型是否可用，以及中转和搜索服务的凭据；本仓库不保存凭据或会话数据。

修改 [setup_for_pi.md](setup_for_pi.md) 可调整安装行为；修改 [pi/](pi/README.md) 中的文件可调整个人 Pi 配置。Codex 和 Pi 各有独立的指令模板和安装目标，不要用一方的配置包覆盖另一方。
