# Appearance Setup

English | [简体中文](appearance.zh-CN.md)

Bootstrap applies Catppuccin Mocha to both Pi and the active terminal profile. Pi theme selection and terminal color-scheme selection are separate settings and must both be configured.

| Setting | Target value | Owner |
| --- | --- | --- |
| Pi theme | [catppuccin-mocha.json](themes/catppuccin-mocha.json) (`theme: "catppuccin-mocha"`) | Bootstrap |
| Terminal color scheme | Catppuccin Mocha from [official terminal ports](https://catppuccin.com/ports/) | Bootstrap |
| Font | Maple Mono NF CN (`MapleMono-NF-CN-unhinted.zip` from [Maple Font releases](https://github.com/subframe7536/maple-font/releases/latest)) | User |
| Background opacity | 95% (`0.95` on a `0–1` scale, 5% transparency) | User |

## Deploy themes (Bootstrap)

1. Copy [themes/catppuccin-mocha.json](themes/catppuccin-mocha.json) to `<agent-dir>/themes/catppuccin-mocha.json` and set `theme: "catppuccin-mocha"` in `<agent-dir>/settings.json`.
2. Identify the active terminal emulator, back up its configuration file, and import and activate Catppuccin Mocha on the active profile without altering unrelated terminal settings.

| Platform / terminal | Activation steps |
| --- | --- |
| Windows — Windows Terminal | Add the [Windows Terminal scheme](https://github.com/catppuccin/windows-terminal) to `schemes` and set the active profile's effective `colorScheme` to `Catppuccin Mocha` |
| macOS — iTerm2 | Import the [iTerm2 Mocha preset](https://github.com/catppuccin/iterm) and select it in the active profile |
| Linux — Kitty | Include or apply the [Kitty Mocha theme](https://github.com/catppuccin/kitty) in the active config |
| Ghostty, WezTerm, or other terminals | Apply the matching port from [https://catppuccin.com/ports/](https://catppuccin.com/ports/) and activate Mocha in the current profile |

Verify Pi and the terminal profile independently. Importing an unused scheme or changing only Pi is incomplete. When the local terminal profile cannot be reached from the current host (such as a remote SSH session), report the terminal theme as pending so the user can apply it on the client machine.

## Install font and set opacity (User)

1. Download `MapleMono-NF-CN-unhinted.zip` from [https://github.com/subframe7536/maple-font/releases/latest](https://github.com/subframe7536/maple-font/releases/latest) and install all `.ttf` weights and italics (Windows: right-click Install; macOS: Font Book; Linux: user font directory or font manager).
2. Restart the terminal, set the profile font to `Maple Mono NF CN`, and set background opacity to `95%` (`0.95`).
