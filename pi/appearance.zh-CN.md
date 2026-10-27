# 终端外观

[English](appearance.md) | 简体中文

| 项目 | 设置／下载 |
| --- | --- |
| Pi 主题 | [catppuccin-mocha.json](themes/catppuccin-mocha.json)，由 bootstrap 部署 |
| 终端配色 | **Catppuccin Mocha** — [官方终端适配列表](https://catppuccin.com/ports/) |
| 字体 | **Maple Mono NF CN** — [GitHub 下载页](https://github.com/subframe7536/maple-font/releases/latest)，选择 `MapleMono-NF-CN-unhinted.zip` |
| 背景不透明度 | **95%**，即 5% 透明度；使用 0–1 数值的终端填 `0.95` |

Windows、macOS 和 Linux 使用同一套 Mocha 色板。字体与终端设置由使用者自行完成：

- **Windows**：安装压缩包内的 `.ttf`，在 Windows Terminal → 设置 → 默认值 → 外观中选择 Maple Mono NF CN，导入 [Mocha 终端配色](https://github.com/catppuccin/windows-terminal)。
- **macOS**：通过“字体册”安装 `.ttf`，在终端配置中选择字体和 Mocha 配色。
- **Linux**：通过桌面字体管理器或用户字体目录安装，需要时刷新字体缓存，再在终端中选择字体和 Mocha 配色。

压缩包里的字重和斜体可以全部安装。安装后重启终端。字号和模糊效果按喜好设置；模糊效果取决于终端和桌面环境。Bootstrap 不安装系统字体，也不修改终端配置。
