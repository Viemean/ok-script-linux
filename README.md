# ok-script-linux

面向 Linux 环境（原生与 Proton/Wine 运行环境）的游戏自动化底层框架。

---

## 架构与技术实现

### 1. 画面捕获实现 (`ok/device/capture_methods/`)

- **Vulkan Layer 显存采集 (`linux_vulkan_capture.py` / `obs-vkcapture`)**：
  框架创建并监听 Linux Abstract Domain Socket (`\0/com/obsproject/vkcapture`)。当游戏进程挂载 `obs-vkcapture`（经由 Vulkan 驱动层）运行时，通过 UNIX 域套接字传递共享内存文件描述符（`SCM_RIGHTS` fd），Python 端使用 `mmap` 直接读取渲染纹理内存（BGRA），无需通过窗口管理器合成器或显示服务截屏。

  - **宿主依赖组件**：
    系统需安装 `obs-vkcapture`（提供 Vulkan Layer 共享库）：

    ```bash
    # Arch Linux / Manjaro
    sudo pacman -S obs-vkcapture

    # Fedora
    sudo dnf install obs-vkcapture
    ```

  - **游戏启动环境变量**：
    目标游戏进程必须注入 `OBS_VKCAPTURE=1` 环境变量以挂载 Vulkan 捕获层。
    - Steam 启动项：

      ```bash
      OBS_VKCAPTURE=1 %command%
      ```

    - Lutris / Heroic / 自定义脚本：
      在启动环境字典或包装脚本中导出 `export OBS_VKCAPTURE=1`。

- **X11 / XWayland 窗口采集 (`linux_capture.py` / `xshm/`)**：
  若 Vulkan Layer 未挂载，作为回退路径使用编译的 C 共享库 `ok-xshm-capture.so`（调用 `XShmCreateImage` 与 `XShmGetImage`），通过 X11 共享内存段拉取指定 X11 窗口几何区域像素。若 XSHM 不可用，顺序回退至 `python-xlib` 的 `ZPixmap` 读取或桌面截屏工具。

- **窗口生命周期管理 (`linux_window.py`)**：
  基于 `python-xlib` 轮询与监听根窗口属性（`_NET_ACTIVE_WINDOW`、`_NET_CLIENT_LIST`），根据配置的进程名与窗口标题正则表达式解析目标窗口 XID，计算窗口坐标与客户区尺寸。

### 2. 输入交互实现 (`ok/device/interaction_methods/`)

- **Wine Agent IPC 代理 (`wine_agent/` + `wine_agent_client.py`)**：
  针对运行在 Wine/Proton 环境中的 Windows 目标游戏，框架在运行时检查 `/proc/$PID/environ` 提取宿主 `WINEPREFIX` 与 Proton 运行时路径，启动并注入独立编译的 Win32 进程代理 `ok-wine-agent.exe`：
  - 宿主与代理进程通过本地 TCP Socket（默认端口 49152）进行二进制协议交互（魔数 `0x4F4B5757`）；
  - 由代理进程在 Wine 进程树内直接调用 Win32 API `PostMessageW`，向游戏主窗口 HWND 投递 `WM_KEYDOWN`、`WM_KEYUP`、`WM_MOUSEMOVE`、`WM_LBUTTONDOWN` 等消息，实现无需窗口置顶的后台输入；
  - 映射表包含 US 104 标准扫描码、扩展键标志（Bit 24，如方向键、小键盘除号、右 Alt/Ctrl）与鼠标按键（含 XButton1 / XButton2）。
- **Linux 内核输入模拟 (`linux_uinput.py`)**：
  通过 `/dev/uinput` 接口在 Linux 系统中注册虚拟输入设备（`evdev`），直接向 Linux 内核输入子系统写入 `EV_KEY` 与 `EV_REL` 事件。
- **全局快捷键 (`ok/ui/qt/start/StartCard.py`)**：
  通过 `pynput` 监听 X11/Linux 输入事件，绑定热键（默认 F9）触发任务执行器的启动与停止。

### 3. 音频流控制 (`ok/device/audio_methods/`)

- **PulseAudio / PipeWire 流控制 (`linux_audio.py`)**：
  基于 `pulsectl` 连接系统音频服务，遍历 `sink_input_list()`。根据配置项中的 `audio_targets` 匹配目标进程的 `application.process.binary` 或进程名属性，在游戏失去焦点时修改音频流静音状态（`mute=1` / `mute=0`）。

### 4. 业务解耦与配置驱动 (`ok/ui/qt/` & `ok/device/`)

- **无业务硬编码**：
  框架核心不包含特定游戏的固定字符串。通过外部字典 `config["windows"]` 接收目标程序参数：

  ```python
  "windows": {
      "exe": ["TargetGame.exe"],
      "title": r"TargetGameTitleRegex",
      "audio_targets": ["TargetGame.exe"],
      "interaction": [
          "ok.device.interaction_methods.linux_proton_post_message.LinuxProtonPostMessageInteraction",
          "ok.device.interaction_methods.wine_agent_client.WineAgentInteraction",
      ],
      "capture_method": ["LinuxWindowCaptureMethod"],
      "start_method": "linux_proton",
  }
  ```

---

## 接入方式

下游应用工程以 Git Submodule 形式引入本仓库：

```bash
git submodule add -b master git@github.com:Viemean/ok-script-linux.git ok
```

入口执行示例：

```python
#!/usr/bin/env -S uv run
from src.config import config
from ok import OK

if __name__ == '__main__':
    OK(config).start()
```

---

## 版本与上游同步策略

- **上游版本基线**：本项目底层基于 [ok-oldking/ok-script](https://github.com/ok-oldking/ok-script) 的 `v2.0.22` 版本构建。
- **UI 框架冻结**：上游自 `v3.0.0` 起重写了 UI 组件库（引入 Windows 专有 DWM/Mica 混合渲染与 Win32 消息循环），并移除了 `PySide6-Fluent-Widgets`。本项目永久冻结 UI 架构，不再跟随上游 3.x 及后续的 UI 重构。
- 上游核心调度将逻辑按需挑选。

---

## 移植指南

关于如何将基于 `ok-script` 的通用 Windows 游戏自动化项目移植到 Linux (Proton/Wine)，详见：

- [通用Linux 移植规范](docs/porting_guide.md)

---

## 开源协议

本项目基于 [ok-oldking/ok-script](https://github.com/ok-oldking/ok-script) 二次开发，遵循其开源许可证。
