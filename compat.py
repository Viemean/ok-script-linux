"""Platform compatibility layer for ok-script on non-Windows systems."""
# [LINUX-PORT-CRITICAL] Linux runtime Win32 API stub and emulation layer
import ctypes
import platform
import sys
import threading

_pressed_vkeys = set()
_vkeys_lock = threading.Lock()
_listener_started = False

_SPECIAL_KEY_MAP = {
    'space': 0x20,
    'enter': 0x0D,
    'esc': 0x1B,
    'escape': 0x1B,
    'tab': 0x09,
    'backspace': 0x08,
    'shift': 0x10,
    'shift_l': 0xA0,
    'shift_r': 0xA1,
    'ctrl': 0x11,
    'ctrl_l': 0xA2,
    'ctrl_r': 0xA3,
    'alt': 0x12,
    'alt_l': 0xA4,
    'alt_r': 0xA5,
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
}


def _on_key_press(key):
    vkey = None
    if hasattr(key, 'char') and key.char:
        vkey = ord(key.char.upper())
    elif hasattr(key, 'name'):
        vkey = _SPECIAL_KEY_MAP.get(key.name.lower())
    if vkey is not None:
        with _vkeys_lock:
            _pressed_vkeys.add(vkey)
            if vkey in (0xA0, 0xA1):
                _pressed_vkeys.add(0x10)
            elif vkey in (0xA2, 0xA3):
                _pressed_vkeys.add(0x11)
            elif vkey in (0xA4, 0xA5):
                _pressed_vkeys.add(0x12)


def _on_key_release(key):
    vkey = None
    if hasattr(key, 'char') and key.char:
        vkey = ord(key.char.upper())
    elif hasattr(key, 'name'):
        vkey = _SPECIAL_KEY_MAP.get(key.name.lower())
    if vkey is not None:
        with _vkeys_lock:
            _pressed_vkeys.discard(vkey)
            if vkey in (0xA0, 0xA1):
                _pressed_vkeys.discard(0x10)
            elif vkey in (0xA2, 0xA3):
                _pressed_vkeys.discard(0x11)
            elif vkey in (0xA4, 0xA5):
                _pressed_vkeys.discard(0x12)


def _start_key_listener():
    global _listener_started
    if _listener_started or platform.system() == 'Windows':
        return
    _listener_started = True
    try:
        from pynput import keyboard
        listener = keyboard.Listener(on_press=_on_key_press, on_release=_on_key_release)
        listener.daemon = True
        listener.start()
    except Exception:
        pass


class _GetAsyncKeyStateStub:
    def __init__(self):
        self.restype = None
        self.argtypes = None

    def __call__(self, vkey):
        _start_key_listener()
        with _vkeys_lock:
            if vkey in _pressed_vkeys:
                return 0x8000
        return 0


class _User32Stub:
    def __init__(self):
        self.GetAsyncKeyState = _GetAsyncKeyStateStub()

    def __getattr__(self, name):
        if name == 'GetAsyncKeyState':
            return self.GetAsyncKeyState
        return _WindowsStub()

    def __call__(self, *args, **kwargs):
        return 0


class _WindowsStub:
    """A minimal fallback stub for Windows attributes."""

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        if name == 'user32':
            return _user32_instance
        return _WindowsStub()

    def __call__(self, *args, **kwargs):
        return 0

    def __int__(self):
        return 0

    def __bool__(self):
        return False

    def __iter__(self):
        return iter([])


_user32_instance = _User32Stub()


def init_platform_compat():
    """Initialize safe ctypes fallback on Linux runtime."""
    if not hasattr(ctypes, 'windll'):
        ctypes.windll = _WindowsStub()
    if not hasattr(ctypes, 'WinDLL'):
        ctypes.WinDLL = lambda *args, **kwargs: _WindowsStub()

