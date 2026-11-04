import time
from typing import Optional

from ok.device.capture_methods.base import BaseCaptureMethod
from ok.device.interaction_methods.base import BaseInteraction
from ok.device.interaction_methods.keys import vk_key_dict
from ok.device.interaction_methods.wine_agent_client import WineAgentClient
from ok.util.logger import Logger

logger = Logger.get_logger(__name__)

# Standard Win32 Window Messages
WM_ACTIVATE = 0x0006
WA_INACTIVE = 0
WA_ACTIVE = 1
WM_SETFOCUS = 0x0007
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C

MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002
MK_MBUTTON = 0x0010
MK_XBUTTON1 = 0x0020
MK_XBUTTON2 = 0x0040
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002
WHEEL_DELTA = 120

# Standard scan code mapping for typical US 104 keyboard
SCAN_CODE_MAP = {
    # Numbers 0 - 9
    0x30: 0x0B, 0x31: 0x02, 0x32: 0x03, 0x33: 0x04, 0x34: 0x05,
    0x35: 0x06, 0x36: 0x07, 0x37: 0x08, 0x38: 0x09, 0x39: 0x0A,
    # Letters A - Z
    0x41: 0x1E, 0x42: 0x30, 0x43: 0x2E, 0x44: 0x20, 0x45: 0x12,
    0x46: 0x21, 0x47: 0x22, 0x48: 0x23, 0x49: 0x17, 0x4A: 0x24,
    0x4B: 0x25, 0x4C: 0x26, 0x4D: 0x32, 0x4E: 0x31, 0x4F: 0x18,
    0x50: 0x19, 0x51: 0x10, 0x52: 0x13, 0x53: 0x1F, 0x54: 0x14,
    0x55: 0x16, 0x56: 0x2F, 0x57: 0x11, 0x58: 0x2D, 0x59: 0x15,
    0x5A: 0x2C,
    # Common Controls
    0x08: 0x0E,  # BACKSPACE
    0x09: 0x0F,  # TAB
    0x0D: 0x1C,  # ENTER
    0x14: 0x3A,  # CAPSLOCK
    0x1B: 0x01,  # ESCAPE
    0x20: 0x39,  # SPACE
    # Modifiers (General + Left/Right explicit)
    0x10: 0x2A, 0xA0: 0x2A, 0xA1: 0x36,  # SHIFT, LSHIFT, RSHIFT
    0x11: 0x1D, 0xA2: 0x1D, 0xA3: 0x1D,  # CTRL, LCTRL, RCTRL (extended)
    0x12: 0x38, 0xA4: 0x38, 0xA5: 0x38,  # ALT, LALT, RALT (extended)
    0x5B: 0x5B, 0x5C: 0x5C,              # LWIN, RWIN
    # Function keys F1 - F12
    0x70: 0x3B, 0x71: 0x3C, 0x72: 0x3D, 0x73: 0x3E,
    0x74: 0x3F, 0x75: 0x40, 0x76: 0x41, 0x77: 0x42,
    0x78: 0x43, 0x79: 0x44, 0x7A: 0x57, 0x7B: 0x58,
    # Navigation & Editing keys (Extended)
    0x21: 0x49, 0x22: 0x51, 0x23: 0x4F, 0x24: 0x47,  # PAGE_UP, PAGE_DOWN, END, HOME
    0x25: 0x4B, 0x26: 0x48, 0x27: 0x4D, 0x28: 0x50,  # LEFT, UP, RIGHT, DOWN
    0x2C: 0x37, 0x2D: 0x52, 0x2E: 0x53,              # PRINTSCREEN, INSERT, DELETE
    # OEM Symbol keys
    0xBA: 0x27,  # ;:
    0xBB: 0x0D,  # =+
    0xBC: 0x33,  # ,<
    0xBD: 0x0C,  # -_
    0xBE: 0x34,  # .>
    0xBF: 0x35,  # /?
    0xC0: 0x29,  # `~
    0xDB: 0x1A,  # [{
    0xDC: 0x2B,  # \|
    0xDD: 0x1B,  # ]}
    0xDE: 0x28,  # '"
    # Numpad keys
    0x60: 0x52, 0x61: 0x4F, 0x62: 0x50, 0x63: 0x51, 0x64: 0x4B,
    0x65: 0x4C, 0x66: 0x4D, 0x67: 0x47, 0x68: 0x48, 0x69: 0x49,
    0x6A: 0x37,  # NUMPAD *
    0x6B: 0x4E,  # NUMPAD +
    0x6D: 0x4A,  # NUMPAD -
    0x6E: 0x53,  # NUMPAD .
    0x6F: 0x35,  # NUMPAD / (extended)
    0x90: 0x45,  # NUMLOCK
    0x91: 0x46,  # SCROLLLOCK
}

EXTENDED_KEYS = {
    0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E,
    0x5B, 0x5C, 0x6F, 0xA3, 0xA5
}


def make_lparam(vk_code: int, is_up: bool = False) -> int:
    scan = SCAN_CODE_MAP.get(vk_code, 0)
    lparam = (scan << 16) | 1
    if vk_code in EXTENDED_KEYS:
        lparam |= (1 << 24)
    if is_up:
        lparam |= (1 << 30) | (1 << 31)
    return lparam


def make_mouse_lparam(x: int, y: int) -> int:
    return ((int(y) & 0xFFFF) << 16) | (int(x) & 0xFFFF)


class LinuxProtonPostMessageInteraction(BaseInteraction):
    """Background input driver using Win32 PostMessage dispatched by in-Proton ok-wine-agent."""

    name = "ProtonPostMessage"
    description = "Linux Proton/Wine 内部后台静默输入 (无需前台)"

    def __init__(self, capture: BaseCaptureMethod, hwnd_window=None):
        super().__init__(capture)
        self.hwnd_window = hwnd_window
        self.mouse_pos = (0, 0)
        self.agent = WineAgentClient()
        self.agent.start()

    def get_key_code(self, key) -> int:
        if isinstance(key, int):
            return key
        key_str = str(key).upper()
        if key_str in vk_key_dict:
            code = vk_key_dict[key_str]
            if isinstance(code, int) and code > 0:
                return code
        if len(key_str) == 1:
            return ord(key_str)
        return 0

    def post(self, msg: int, wparam: int = 0, lparam: int = 0) -> bool:
        return self.agent.post_message(msg, wparam, lparam)

    def activate(self):
        self.post(WM_ACTIVATE, WA_ACTIVE, 0)
        self.post(WM_SETFOCUS, 0, 0)

    def deactivate(self):
        self.post(WM_ACTIVATE, WA_INACTIVE, 0)

    def try_activate(self):
        self.activate()

    def get_target_mouse_pos(self, x: int = -1, y: int = -1) -> tuple[int, int]:
        if x >= 0 and y >= 0:
            self.mouse_pos = (int(x), int(y))
            return self.mouse_pos
        if self.mouse_pos != (0, 0):
            return self.mouse_pos
        w = getattr(self.capture, "width", 0) or 1920
        h = getattr(self.capture, "height", 0) or 1080
        self.mouse_pos = (w // 2, h // 2)
        return self.mouse_pos

    def send_key_down(self, key, activate: bool = True):
        if activate:
            self.try_activate()
        vk = self.get_key_code(key)
        if vk:
            lparam = make_lparam(vk, is_up=False)
            self.post(WM_KEYDOWN, vk, lparam)

    def send_key_up(self, key):
        vk = self.get_key_code(key)
        if vk:
            lparam = make_lparam(vk, is_up=True)
            self.post(WM_KEYUP, vk, lparam)

    def send_key(self, key, down_time: float = 0.05):
        super().send_key(key, down_time)
        effective_down_time = max(down_time, 0.05)
        self.send_key_down(key)
        time.sleep(effective_down_time)
        self.send_key_up(key)

    def move(self, x: int, y: int, down_btn: int = 0):
        self.mouse_pos = (int(x), int(y))
        lparam = make_mouse_lparam(x, y)
        self.post(WM_MOUSEMOVE, down_btn, lparam)

    def click(self, x: int = -1, y: int = -1, move_back: bool = False, name: Optional[str] = None,
              move: bool = True, down_time: float = 0.05, key: str = "left"):
        super().click(x, y, name=name)
        self.try_activate()
        target_x, target_y = self.get_target_mouse_pos(x, y)
        effective_down_time = max(down_time, 0.05)
        logger.debug(f"ProtonPostMessage click {key} at ({target_x}, {target_y}) down_time={effective_down_time:.2f}s name={name}")
        lparam = make_mouse_lparam(target_x, target_y)

        k = str(key).lower()
        if k in ("left", "l"):
            down_msg, up_msg, down_wparam, up_wparam = WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON, 0
        elif k in ("right", "r"):
            down_msg, up_msg, down_wparam, up_wparam = WM_RBUTTONDOWN, WM_RBUTTONUP, MK_RBUTTON, 0
        elif k in ("middle", "m"):
            down_msg, up_msg, down_wparam, up_wparam = WM_MBUTTONDOWN, WM_MBUTTONUP, MK_MBUTTON, 0
        elif k in ("x1", "mouse4", "side1"):
            down_msg, up_msg = WM_XBUTTONDOWN, WM_XBUTTONUP
            down_wparam = (XBUTTON1 << 16) | MK_XBUTTON1
            up_wparam = (XBUTTON1 << 16)
        elif k in ("x2", "mouse5", "side2"):
            down_msg, up_msg = WM_XBUTTONDOWN, WM_XBUTTONUP
            down_wparam = (XBUTTON2 << 16) | MK_XBUTTON2
            up_wparam = (XBUTTON2 << 16)
        else:
            down_msg, up_msg, down_wparam, up_wparam = WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON, 0

        # Only send WM_MOUSEMOVE when explicit coordinates are passed
        if move and x >= 0 and y >= 0:
            self.post(WM_MOUSEMOVE, 0, lparam)
            time.sleep(0.01)

        self.post(down_msg, down_wparam, lparam)
        time.sleep(effective_down_time)
        self.post(up_msg, up_wparam, lparam)

    def right_click(self, x: int = -1, y: int = -1, move_back: bool = False, name: Optional[str] = None):
        self.click(x, y, move_back=move_back, name=name, key="right")

    def mouse_down(self, x: int = -1, y: int = -1, name: Optional[str] = None, key: str = "left"):
        self.try_activate()
        target_x, target_y = self.get_target_mouse_pos(x, y)
        logger.debug(f"ProtonPostMessage mouse_down {key} at ({target_x}, {target_y}) name={name}")
        lparam = make_mouse_lparam(target_x, target_y)
        k = str(key).lower()
        if k in ("left", "l"):
            self.post(WM_LBUTTONDOWN, MK_LBUTTON, lparam)
        elif k in ("right", "r"):
            self.post(WM_RBUTTONDOWN, MK_RBUTTON, lparam)
        elif k in ("middle", "m"):
            self.post(WM_MBUTTONDOWN, MK_MBUTTON, lparam)
        elif k in ("x1", "mouse4", "side1"):
            self.post(WM_XBUTTONDOWN, (XBUTTON1 << 16) | MK_XBUTTON1, lparam)
        elif k in ("x2", "mouse5", "side2"):
            self.post(WM_XBUTTONDOWN, (XBUTTON2 << 16) | MK_XBUTTON2, lparam)
        else:
            self.post(WM_LBUTTONDOWN, MK_LBUTTON, lparam)

    def mouse_up(self, key: str = "left"):
        target_x, target_y = self.get_target_mouse_pos()
        logger.debug(f"ProtonPostMessage mouse_up {key} at ({target_x}, {target_y})")
        lparam = make_mouse_lparam(target_x, target_y)
        k = str(key).lower()
        if k in ("left", "l"):
            self.post(WM_LBUTTONUP, 0, lparam)
        elif k in ("right", "r"):
            self.post(WM_RBUTTONUP, 0, lparam)
        elif k in ("middle", "m"):
            self.post(WM_MBUTTONUP, 0, lparam)
        elif k in ("x1", "mouse4", "side1"):
            self.post(WM_XBUTTONUP, (XBUTTON1 << 16), lparam)
        elif k in ("x2", "mouse5", "side2"):
            self.post(WM_XBUTTONUP, (XBUTTON2 << 16), lparam)
        else:
            self.post(WM_LBUTTONUP, 0, lparam)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: float = 200, settle_time: float = 0):
        self.move(x1, y1)
        time.sleep(0.02)
        self.mouse_down(x1, y1, key="left")
        steps = max(int(duration / 20), 1)
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        for i in range(1, steps + 1):
            self.move(int(x1 + i * dx), int(y1 + i * dy), down_btn=MK_LBUTTON)
            time.sleep(0.02)
        self.move(x2, y2, down_btn=MK_LBUTTON)
        if settle_time:
            time.sleep(settle_time)
        self.mouse_up(key="left")

    def scroll(self, x: int, y: int, scroll_amount: int):
        lparam = make_mouse_lparam(x, y)
        wparam = (scroll_amount * WHEEL_DELTA) << 16
        self.post(WM_MOUSEWHEEL, wparam, lparam)

    def input_text(self, text: str):
        for ch in text:
            self.post(WM_CHAR, ord(ch), 0)
            time.sleep(0.01)

    def clickable(self) -> bool:
        # Background clickable: does not require foreground focus
        return self.hwnd_window is not None and self.hwnd_window.exists

    def should_capture(self) -> bool:
        return True

    def on_destroy(self):
        if self.agent:
            self.agent.close()

    def close(self):
        self.on_destroy()
