# 外观配置

[English](appearance.md) | 简体中文

**Bootstrap 必须把 Pi 和当前终端都设为 Catppuccin Mocha。** 这是两项独立配置。

| 项目 | 设置 | 由谁配置 |
| --- | --- | --- |
| Pi 主题 | [catppuccin-mocha.json](themes/catppuccin-mocha.json) | Bootstrap |
| 终端配色 | **Catppuccin Mocha** — [官方终端适配列表](https://catppuccin.com/ports/) | Bootstrap |
| 字体 | **Maple Mono NF CN** — [GitHub 下载页](https://github.com/subframe7536/maple-font/releases/latest)，选择 `MapleMono-NF-CN-unhinted.zip` | 使用者 |
| 背景不透明度 | **95%**，即 5% 透明度；0–1 数值填 `0.95` | 使用者 |

## 主题部署

1. 部署 Pi 主题，在 Pi 设置中选用 `theme: "catppuccin-mocha"`。
2. 识别当前实际使用的终端，备份配置，导入并**选用**官方 Mocha 配色，保留其他配置项。

| 终端 | 配置方式 |
| --- | --- |
| Windows Terminal | 将[官方配色](https://github.com/catppuccin/windows-terminal)导入 `schemes`，使当前配置文件实际使用 `colorScheme: "Catppuccin Mocha"` |
| macOS 的 iTerm2 | 导入 [Mocha 预设](https://github.com/catppuccin/iterm)，并在当前配置文件中选用 |
| Linux 的 Kitty | 应用 [Mocha 配置](https://github.com/catppuccin/kitty) |
| Ghostty、WezTerm 或其他终端 | 从[官方列表](https://catppuccin.com/ports/)选择对应适配，在当前配置中选用 Mocha |

分别验证两项设置。只导入未选用，或只修改 Pi，都不算主题配置完成。无法访问终端配置时标记为待处理；SSH 远端不能代替客户端修改本地终端配置。

## 使用者操作

安装字体包内全部 `.ttf` 字重和斜体：Windows 选择“安装”，macOS 使用“字体册”，Linux 使用用户字体管理器或字体目录。重启终端，选择 **Maple Mono NF CN**，背景不透明度设为 **95%**。
