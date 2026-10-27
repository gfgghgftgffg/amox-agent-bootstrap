# Appearance setup

English | [简体中文](appearance.zh-CN.md)

**Bootstrap must apply Catppuccin Mocha to both Pi and the active terminal profile.** These are two separate settings.

| Setting | Value | Applied by |
| --- | --- | --- |
| Pi theme | [catppuccin-mocha.json](themes/catppuccin-mocha.json) | Bootstrap |
| Terminal scheme | **Catppuccin Mocha** — [official terminal ports](https://catppuccin.com/ports/) | Bootstrap |
| Font | **Maple Mono NF CN** — [GitHub releases](https://github.com/subframe7536/maple-font/releases/latest), `MapleMono-NF-CN-unhinted.zip` | User |
| Background opacity | **95%** (5% transparency; `0.95` on a 0–1 scale) | User |

## Theme deployment

1. Deploy the Pi theme and select `theme: "catppuccin-mocha"` in Pi settings.
2. Detect the actual terminal, back up its configuration, then import **and select** its official Mocha scheme. Preserve unrelated profile settings.

| Terminal | Scheme setup |
| --- | --- |
| Windows Terminal | Import the [official scheme](https://github.com/catppuccin/windows-terminal) into `schemes`; set the active profile's effective `colorScheme` to `Catppuccin Mocha` |
| iTerm2 on macOS | Import and select the [Mocha preset](https://github.com/catppuccin/iterm) in the active profile |
| Kitty on Linux | Apply the [Mocha configuration](https://github.com/catppuccin/kitty) |
| Ghostty, WezTerm or another terminal | Use its port from the [official catalog](https://catppuccin.com/ports/) and select Mocha in the active configuration |

Verify both settings separately. Importing an unused scheme or changing only Pi is incomplete. If the terminal profile is inaccessible, report terminal theme as pending; an SSH host cannot configure the client's local terminal profile.

## User steps

Install all `.ttf` weights/italics from the font archive: Windows **Install**, macOS **Font Book**, or a Linux user font manager/directory. Restart the terminal and select **Maple Mono NF CN**. Set background opacity to **95%**. Font size and supported blur effects are personal choices; bootstrap does not install system fonts.
