# amox-agent-bootstrap

[English](README.md) | 简体中文

个人 Codex 和 Pi 的部署说明及配置模板，支持 Windows、macOS 和 Linux。Agent 检查电脑、复用兼容软件、安装缺少的组件并验证结果，保留无关配置和已有凭据。

## Codex

安装 Codex 后，发送以下提示词：

```text
阅读 https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup.md，
按照其中的说明配置这台电脑。完成安装、验证结果，
并说明还有哪些事项需要我提供信息或处理。
```

[setup.md](setup.md) 包含 Conda、共享 Python `codex` 环境、Skills、Task Router 和 Codex 设置；[templates/AGENTS.md](templates/AGENTS.md) 提供全局指令。

## Pi

安装 Pi 后，发送以下提示词：

```text
阅读 https://github.com/gfgghgftgffg/amox-agent-bootstrap/blob/main/setup_for_pi.md，
按照其中的说明配置这台电脑。获取文中引用的 pi/ 文件，
完成安装、验证结果，并说明还有哪些事项需要我提供信息或处理。
```

[setup_for_pi.md](setup_for_pi.md) 包含十个包、七个 Skills（包括仅显式调用的 `ian-xiaohei-illustrations`）、Task Router、Conda 和 [Pi 配置模板](pi/README.md)，pi-pretty 使用 `claudecode` 工具样式。三个 amox lean 包已在 npm 公开发布，采用不固定版本的来源，按需执行 `pi update --extensions`。迁移已有本地来源须经同意，替换原注册项，不重复添加。

任务路由通过 `/skill:task-routing` 显式启用。Pi Sync 仅手动同步会话和任务，需要[你自己的私有仓库](pi/pi-sync-setup.zh-CN.md)。bootstrap 不执行同步或付费模型、生图测试。

## 配置维护

修改对应的 setup 文档和模板即可调整部署。Codex 与 Pi 使用独立的指令文件和安装目标。模板不是任何电脑的实时安装清单。真实凭据、会话、缓存和备份不入 Git；缺少的密钥在本机填写，不在聊天中传递。
