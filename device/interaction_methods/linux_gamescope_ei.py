import ctypes
import glob
import os
import time
from typing import Optional

from ok.device.interaction_methods.base import BaseInteraction
from ok.util.logger import Logger

logger = Logger.get_logger(__name__)

# Linux evdev key codes
KEY_MAP = {
    'a': 30, 'b': 48, 'c': 46, 'd': 32, 'e': 18, 'f': 33, 'g': 34, 'h': 35,
    'i': 23, 'j': 36, 'k': 37, 'l': 38, 'm': 50, 'n': 49, 'o': 24, 'p': 25,
    'q': 16, 'r': 19, 's': 31, 't': 20, 'u': 22, 'v': 47, 'w': 17, 'x': 45,
    'y': 21, 'z': 44,
    '0': 11, '1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 9, '9': 10,
    'space': 57, 'esc': 1, 'escape': 1, 'enter': 28, 'return': 28, 'tab': 15,
    'lshift': 42, 'rshift': 54, 'shift': 42,
    'lctrl': 29, 'rctrl': 97, 'ctrl': 29,
    'lalt': 56, 'ralt': 100, 'alt': 56,
    'f1': 59, 'f2': 60, 'f3': 61, 'f4': 62, 'f5': 63, 'f6': 64,
    'f7': 65, 'f8': 66, 'f9': 67, 'f10': 68, 'f11': 87, 'f12': 88,
}

BTN_MAP = {
    'left': 0x110,
    'right': 0x111,
    'middle': 0x112,
}

# libei constants
EI_EVENT_CONNECT = 1
EI_EVENT_SEAT_ADDED = 3
EI_EVENT_DEVICE_ADDED = 5
EI_EVENT_DEVICE_RESUMED = 8

EI_DEVICE_CAP_POINTER = 1 << 0
EI_DEVICE_CAP_POINTER_ABSOLUTE = 1 << 1
EI_DEVICE_CAP_KEYBOARD = 1 << 2
EI_DEVICE_CAP_TOUCH = 1 << 3
EI_DEVICE_CAP_SCROLL = 1 << 4
EI_DEVICE_CAP_BUTTON = 1 << 5

_libei = None
_libei_loaded = False


def _load_libei():
    global _libei, _libei_loaded
    if _libei_loaded:
        return _libei

    _libei_loaded = True
    for path in ["libei.so.1", "/usr/lib/libei.so.1", "/usr/lib64/libei.so.1", "libei.so"]:
        try:
            lib = ctypes.CDLL(path)
            lib.ei_new_sender.argtypes = [ctypes.c_void_p]
            lib.ei_new_sender.restype = ctypes.c_void_p

            lib.ei_setup_backend_socket.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            lib.ei_setup_backend_socket.restype = ctypes.c_int

            lib.ei_dispatch.argtypes = [ctypes.c_void_p]
            lib.ei_dispatch.restype = None

            lib.ei_get_event.argtypes = [ctypes.c_void_p]
            lib.ei_get_event.restype = ctypes.c_void_p

            lib.ei_event_unref.argtypes = [ctypes.c_void_p]
            lib.ei_event_unref.restype = ctypes.c_void_p

            lib.ei_event_get_type.argtypes = [ctypes.c_void_p]
            lib.ei_event_get_type.restype = ctypes.c_int

            lib.ei_event_get_seat.argtypes = [ctypes.c_void_p]
            lib.ei_event_get_seat.restype = ctypes.c_void_p

            lib.ei_event_get_device.argtypes = [ctypes.c_void_p]
            lib.ei_event_get_device.restype = ctypes.c_void_p

            lib.ei_seat_bind_capabilities.argtypes = [ctypes.c_void_p]

            lib.ei_device_ref.argtypes = [ctypes.c_void_p]
            lib.ei_device_ref.restype = ctypes.c_void_p

            lib.ei_device_unref.argtypes = [ctypes.c_void_p]
            lib.ei_device_unref.restype = ctypes.c_void_p

            lib.ei_device_start_emulating.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            lib.ei_device_start_emulating.restype = None

            lib.ei_device_stop_emulating.argtypes = [ctypes.c_void_p]
            lib.ei_device_stop_emulating.restype = None

            lib.ei_device_frame.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
            lib.ei_device_frame.restype = None

            lib.ei_device_keyboard_key.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_bool]
            lib.ei_device_keyboard_key.restype = None

            lib.ei_device_pointer_motion.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]
            lib.ei_device_pointer_motion.restype = None

            lib.ei_device_pointer_motion_absolute.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]
            lib.ei_device_pointer_motion_absolute.restype = None

            lib.ei_device_button_button.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_bool]
            lib.ei_device_button_button.restype = None

            lib.ei_device_scroll_discrete.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32]
            lib.ei_device_scroll_discrete.restype = None

            lib.ei_device_scroll_stop.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_bool]
            lib.ei_device_scroll_stop.restype = None

            lib.ei_now.argtypes = [ctypes.c_void_p]
            lib.ei_now.restype = ctypes.c_uint64

            lib.ei_unref.argtypes = [ctypes.c_void_p]
            lib.ei_unref.restype = ctypes.c_void_p

            _libei = lib
            logger.info(f"Loaded libei successfully from {path}")
            break
        except Exception:
            continue

    if _libei is None:
        logger.warning("libei library not found on system; Gamescope EI interaction disabled")
    return _libei


def _find_gamescope_ei_socket() -> Optional[str]:
    custom = os.environ.get("GAMESCOPE_EI_SOCKET")
    if custom and os.path.exists(custom):
        return custom

    uid = os.getuid()
    run_dir = f"/run/user/{uid}"
    matches = sorted(glob.glob(os.path.join(run_dir, "gamescope-*-ei")))
    if matches:
        return matches[0]
    return None


class LinuxGamescopeEIInteraction(BaseInteraction):
    """Hardware-level virtual input device via Gamescope Emulated Input (libei)."""
    name = "libei"
    description = "Gamescope libei 硬件级虚拟输入（无注入标记，支持视角）"

    def __init__(self, capture, hwnd_window=None, socket_path=None):
        super().__init__(capture)
        self.hwnd_window = hwnd_window
        self.socket_path = socket_path
        self._ei = None
        self._device = None
        self._sequence = 0
        self._connected = False
        self._is_emulating = False
        self._lib = _load_libei()
        self._init_connection()

    def _init_connection(self):
        if not self._lib:
            return

        sock_path = self.socket_path or _find_gamescope_ei_socket()
        if not sock_path or not os.path.exists(sock_path):
            logger.warning(f"Gamescope EIS socket not found in {sock_path}")
            return

        try:
            self._ei = self._lib.ei_new_sender(None)
            if not self._ei:
                return

            res = self._lib.ei_setup_backend_socket(self._ei, sock_path.encode("utf-8"))
            if res != 0:
                logger.warning(f"Failed to setup libei backend socket {sock_path}: {res}")
                self.close()
                return

            start_t = time.time()
            while time.time() - start_t < 2.0:
                self._lib.ei_dispatch(self._ei)
                while True:
                    ev = self._lib.ei_get_event(self._ei)
                    if not ev:
                        break
                    ev_type = self._lib.ei_event_get_type(ev)
                    if ev_type == EI_EVENT_SEAT_ADDED:
                        seat = self._lib.ei_event_get_seat(ev)
                        self._lib.ei_seat_bind_capabilities(
                            seat,
                            ctypes.c_int(EI_DEVICE_CAP_POINTER),
                            ctypes.c_int(EI_DEVICE_CAP_POINTER_ABSOLUTE),
                            ctypes.c_int(EI_DEVICE_CAP_KEYBOARD),
                            ctypes.c_int(EI_DEVICE_CAP_TOUCH),
                            ctypes.c_int(EI_DEVICE_CAP_SCROLL),
                            ctypes.c_int(EI_DEVICE_CAP_BUTTON),
                            ctypes.c_void_p(None),
                        )
                    elif ev_type == EI_EVENT_DEVICE_ADDED:
                        dev = self._lib.ei_event_get_device(ev)
                        self._device = self._lib.ei_device_ref(dev)
                    elif ev_type == EI_EVENT_DEVICE_RESUMED:
                        self._connected = True
                    self._lib.ei_event_unref(ev)

                if self._connected and self._device:
                    logger.info(f"LinuxGamescopeEIInteraction connected to {sock_path}")
                    return
                time.sleep(0.02)

        except Exception as e:
            logger.error(f"Error connecting to Gamescope EIS socket: {e}")
            self.close()

    def _ensure_ready(self) -> bool:
        if not self._connected or not self._device or not self._lib or not self._ei:
            self._init_connection()
        return self._connected and self._device is not None

    def _start_emulating(self) -> bool:
        if not self._ensure_ready():
            return False
        if not self._is_emulating:
            self._sequence += 1
            self._lib.ei_device_start_emulating(self._device, self._sequence)
            self._is_emulating = True
        return True

    def _stop_emulating(self):
        if self._is_emulating and self._device and self._lib:
            try:
                self._lib.ei_device_stop_emulating(self._device)
                self._lib.ei_dispatch(self._ei)
            except Exception:
                pass
            self._is_emulating = False

    def _to_code(self, key):
        if isinstance(key, int):
            return key
        return KEY_MAP.get(str(key).lower())

    def send_key(self, key, down_time=0.02):
        super().send_key(key, down_time)
        code = self._to_code(key)
        if code and self._start_emulating():
            self._lib.ei_device_keyboard_key(self._device, code, True)
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._lib.ei_dispatch(self._ei)
            time.sleep(down_time)
            self._lib.ei_device_keyboard_key(self._device, code, False)
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._stop_emulating()

    def send_key_down(self, key):
        code = self._to_code(key)
        if code and self._start_emulating():
            self._lib.ei_device_keyboard_key(self._device, code, True)
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._lib.ei_dispatch(self._ei)

    def send_key_up(self, key):
        code = self._to_code(key)
        if code and self._start_emulating():
            self._lib.ei_device_keyboard_key(self._device, code, False)
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._stop_emulating()

    def move_rel(self, dx: float, dy: float):
        """Relative mouse movement for 3D camera rotation."""
        was_emulating = self._is_emulating
        if self._start_emulating():
            self._lib.ei_device_pointer_motion(self._device, float(dx), float(dy))
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._lib.ei_dispatch(self._ei)
            if not was_emulating:
                self._stop_emulating()

    def move(self, x: float, y: float):
        """Absolute pointer movement within window/screen."""
        was_emulating = self._is_emulating
        if self._start_emulating():
            self._lib.ei_device_pointer_motion_absolute(self._device, float(x), float(y))
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._lib.ei_dispatch(self._ei)
            if not was_emulating:
                self._stop_emulating()

    def mouse_down(self, x=-1, y=-1, name=None, key="left"):
        if x >= 0 and y >= 0:
            self.move(x, y)
        btn = BTN_MAP.get(str(key).lower(), 0x110)
        if self._start_emulating():
            self._lib.ei_device_button_button(self._device, btn, True)
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._lib.ei_dispatch(self._ei)

    def mouse_up(self, key="left"):
        btn = BTN_MAP.get(str(key).lower(), 0x110)
        if self._start_emulating():
            self._lib.ei_device_button_button(self._device, btn, False)
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._stop_emulating()

    def click(self, x=-1, y=-1, move_back=False, name=None, move=True, down_time=0.05, key="left"):
        if x >= 0 and y >= 0:
            self.move(x, y)
        self.mouse_down(key=key)
        time.sleep(down_time)
        self.mouse_up(key=key)

    def scroll(self, x, y, scroll_amount):
        if x >= 0 and y >= 0:
            self.move(x, y)
        was_emulating = self._is_emulating
        if self._start_emulating():
            # scroll_discrete: dy > 0 is scroll up, dy < 0 is scroll down
            self._lib.ei_device_scroll_discrete(self._device, 0, int(scroll_amount * 120))
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._lib.ei_device_scroll_stop(self._device, False, True)
            self._lib.ei_device_frame(self._device, self._lib.ei_now(self._ei))
            self._lib.ei_dispatch(self._ei)
            if not was_emulating:
                self._stop_emulating()

    def input_text(self, text: str):
        for ch in text:
            self.send_key(ch, down_time=0.01)
            time.sleep(0.01)

    def clickable(self) -> bool:
        return self.hwnd_window is not None and self.hwnd_window.exists

    def should_capture(self) -> bool:
        return True

    def on_run(self):
        pass

    def on_destroy(self):
        self.close()

    def close(self):
        self._stop_emulating()
        if self._device and self._lib:
            try:
                self._lib.ei_device_unref(self._device)
            except Exception:
                pass
            self._device = None
        if self._ei and self._lib:
            try:
                self._lib.ei_unref(self._ei)
            except Exception:
                pass
            self._ei = None
        self._connected = False
