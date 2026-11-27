# ok-script-linux

面向 Linux（原生桌面与 Proton/Wine 容器）的游戏自动化底层框架。

---

## 核心技术组件

- **界面与架构（`ui/qt/kit/`）**：基于 **PySide6** 的 3.x 纯 Qt 组件体系，支持明暗主题、系统托盘与纯 Qt 调试悬浮窗（`OverlayWidget`）。
- **画面捕获（`device/capture_methods/`）**：
  - `Vulkan`（首选）：通过 `obs-vkcapture` 共享内存直读游戏画面。
  - `X11_Direct`（回退）：基于 X11 MIT-SHM 共享内存抓帧，不依赖 `obs-vkcapture`。
- **窗口与音频控制（`linux_window.py`, `linux_audio.py`）**：
  - 使用 `python-xlib` 与 Gamescope 窗口追踪匹配目标进程与窗口坐标。
  - 使用 `pulsectl`（PipeWire / PulseAudio）实现游戏失焦自动静音。
- **输入交互与热键（`device/interaction_methods/`, `ui/qt/shell/run_bar.py`）**：
  - 支持 `ProtonPostMessage`（Wine/Proton 后台消息代理 `agent-post.exe`）、`libei`（Gamescope 原生虚拟输入）与 `UInput`（Linux 内核虚拟设备，回退 `pynput`）。
  - 全局启停热键（F9–F12）优先使用 `evdev` 监听键盘事件，无设备权限时自动回退至 `pynput`。
- **视觉与扩展能力**：集成 OpenCV、ONNXRuntime / OpenVINO（OCR 与目标检测）、`git_updater` 检查以及 MCP 服务接口。

---

## 接入方式

下游工程以 Git Submodule 形式引入本仓库：

```bash
git submodule add -b master git@github.com:Viemean/ok-script-linux.git ok
```

配置入口仅需在 `config["windows"]` 中声明目标进程与默认捕获/交互方式：

```python
from src.config import config
from ok import OK

if __name__ == '__main__':
    OK(config).start()
```

---

## 版本与上游策略

- **上游基线**：跟随 [ok-oldking/ok-script](https://github.com/ok-oldking/ok-script) 3.x（已移除 `PySide6-Fluent-Widgets`）。
- **2.x 归档**：迁移前最后一个 2.x Linux 基线保留在标签 `v2.x-linux-final`。
- **平台边界**：保留 Linux 捕获/输入/热键/音频与纯 Qt 悬浮窗适配；屏蔽或移除 Windows 专有抓帧（WGC/DXGI/BitBlt）、计划任务、自动启动游戏及 `pyappify` 更新器等依赖。

---

## 开源协议

本项目基于 [ok-oldking/ok-script](https://github.com/ok-oldking/ok-script) 二次开发，遵循其开源许可证。
