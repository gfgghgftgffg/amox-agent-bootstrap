# 外观配置指南

[English](appearance.md) | 简体中文

Bootstrap 会将 Pi 和当前终端都设为 Catppuccin Mocha。Pi 主题与终端配色相互独立，部署时需分别设置并验证。

| 配置项 | 目标值 | 负责方 |
| --- | --- | --- |
| Pi 主题 | [catppuccin-mocha.json](themes/catppuccin-mocha.json)（`theme: "catppuccin-mocha"`） | Bootstrap |
| 终端配色方案 | Catppuccin Mocha（见[官方终端适配目录](https://catppuccin.com/ports/)） | Bootstrap |
| 终端字体 | Maple Mono NF CN（从 [Maple Font 发布页](https://github.com/subframe7536/maple-font/releases/latest) 下载 `MapleMono-NF-CN-unhinted.zip`） | 使用者 |
| 背景不透明度 | 95%（0–1 比例填 `0.95`，即 5% 透明度） | 使用者 |

## 部署主题（Bootstrap）

1. 将 [themes/catppuccin-mocha.json](themes/catppuccin-mocha.json) 复制到 `<agent-dir>/themes/catppuccin-mocha.json`，并在 `<agent-dir>/settings.json` 中设置 `theme: "catppuccin-mocha"`。
2. 识别当前实际运行的终端程序，先备份其配置文件，再为当前生效的终端 Profile 导入并启用官方 Catppuccin Mocha 配色，保留其余终端设置。

| 系统／终端 | 配置方法 |
| --- | --- |
| Windows — Windows Terminal | 将 [Windows Terminal 配色](https://github.com/catppuccin/windows-terminal) 写入 `schemes`，并将当前 Profile 实际生效的 `colorScheme` 设为 `Catppuccin Mocha` |
| macOS — iTerm2 | 导入 [iTerm2 Mocha 预设](https://github.com/catppuccin/iterm)，并在当前 Profile 中选中 |
| Linux — Kitty | 在当前配置中引入并启用 [Kitty Mocha 配色](https://github.com/catppuccin/kitty) |
| Ghostty、WezTerm 或其他终端 | 从 [https://catppuccin.com/ports/](https://catppuccin.com/ports/) 获取对应适配，并在当前生效配置中启用 Mocha |

分别核验 Pi 与终端两处配置。仅导入而未在当前 Profile 中启用，或只修改了 Pi 主题，均不算完成。若当前主机无法访问客户端终端配置（例如通过 SSH 远程连接），将终端配色报告为待处理，由使用者在本地终端完成。

## 安装字体与设置不透明度（使用者）

1. 从 [https://github.com/subframe7536/maple-font/releases/latest](https://github.com/subframe7536/maple-font/releases/latest) 下载 `MapleMono-NF-CN-unhinted.zip`，安装压缩包内的全部 `.ttf` 字重与斜体（Windows 右键选择“安装”，macOS 使用“字体册”，Linux 放入用户字体目录或通过字体管理器安装）。
2. 重启终端，在当前 Profile 中将字体设为 `Maple Mono NF CN`，并将背景不透明度设为 `95%`（`0.95`）。
