# Virtual key code constants for Wine agent IPC protocol
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_CAPITAL = 0x14
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_PRIOR = 0x21
VK_NEXT = 0x22
VK_END = 0x23
VK_HOME = 0x24
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_SNAPSHOT = 0x2C
VK_INSERT = 0x2D
VK_DELETE = 0x2E
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_F1 = 0x70
VK_F2 = 0x71
VK_F3 = 0x72
VK_F4 = 0x73
VK_F5 = 0x74
VK_F6 = 0x75
VK_F7 = 0x76
VK_F8 = 0x77
VK_F9 = 0x78
VK_F10 = 0x79
VK_F11 = 0x7A
VK_F12 = 0x7B
VK_NUMLOCK = 0x90
VK_SCROLL = 0x91
VK_LSHIFT = 0xA0
VK_RSHIFT = 0xA1
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3
VK_LMENU = 0xA4
VK_RMENU = 0xA5

# Numpad keys
VK_NUMPAD0 = 0x60
VK_NUMPAD1 = 0x61
VK_NUMPAD2 = 0x62
VK_NUMPAD3 = 0x63
VK_NUMPAD4 = 0x64
VK_NUMPAD5 = 0x65
VK_NUMPAD6 = 0x66
VK_NUMPAD7 = 0x67
VK_NUMPAD8 = 0x68
VK_NUMPAD9 = 0x69
VK_MULTIPLY = 0x6A
VK_ADD = 0x6B
VK_SEPARATOR = 0x6C
VK_SUBTRACT = 0x6D
VK_DECIMAL = 0x6E
VK_DIVIDE = 0x6F

# OEM symbol keys
VK_OEM_1 = 0xBA        # ;:
VK_OEM_PLUS = 0xBB     # =+
VK_OEM_COMMA = 0xBC    # ,<
VK_OEM_MINUS = 0xBD    # -_
VK_OEM_PERIOD = 0xBE   # .>
VK_OEM_2 = 0xBF        # /?
VK_OEM_3 = 0xC0        # `~
VK_OEM_4 = 0xDB        # [{
VK_OEM_5 = 0xDC        # \|
VK_OEM_6 = 0xDD        # ]}
VK_OEM_7 = 0xDE        # '"

# Mouse buttons
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_XBUTTON1 = 0x05
VK_XBUTTON2 = 0x06

PYDIRECT_KEY_MAP = {}


def normalize_pydirect_key(key):
    return str(key)


vk_key_dict = {
    'F1': VK_F1,
    'F2': VK_F2,
    'F3': VK_F3,
    'F4': VK_F4,
    'F5': VK_F5,
    'F6': VK_F6,
    'F7': VK_F7,
    'F8': VK_F8,
    'F9': VK_F9,
    'F10': VK_F10,
    'F11': VK_F11,
    'F12': VK_F12,
    'ESC': VK_ESCAPE,
    'CTRL': VK_CONTROL,
    'CONTROL': VK_CONTROL,
    'LCTRL': VK_LCONTROL,
    'RCTRL': VK_RCONTROL,
    'CTRL_L': VK_LCONTROL,
    'CTRL_R': VK_RCONTROL,
    'LCONTROL': VK_LCONTROL,
    'RCONTROL': VK_RCONTROL,
    'ALT': VK_MENU,
    'LALT': VK_LMENU,
    'RALT': VK_RMENU,
    'ALT_L': VK_LMENU,
    'ALT_R': VK_RMENU,
    'SHIFT': VK_SHIFT,
    'LSHIFT': VK_LSHIFT,
    'RSHIFT': VK_RSHIFT,
    'SHIFT_L': VK_LSHIFT,
    'SHIFT_R': VK_RSHIFT,
    'TAB': VK_TAB,
    'ENTER': VK_RETURN,
    'RETURN': VK_RETURN,
    'SPACE': VK_SPACE,
    'LEFT': VK_LEFT,
    'UP': VK_UP,
    'RIGHT': VK_RIGHT,
    'DOWN': VK_DOWN,
    'BACKSPACE': VK_BACK,
    'PAGEUP': VK_PRIOR,
    'PAGE_UP': VK_PRIOR,
    'PAGEDOWN': VK_NEXT,
    'PAGE_DOWN': VK_NEXT,
    'HOME': VK_HOME,
    'END': VK_END,
    'INSERT': VK_INSERT,
    'DELETE': VK_DELETE,
    'CAPSLOCK': VK_CAPITAL,
    'CAPS_LOCK': VK_CAPITAL,
    'NUMLOCK': VK_NUMLOCK,
    'NUM_LOCK': VK_NUMLOCK,
    'SCROLLLOCK': VK_SCROLL,
    'SCROLL_LOCK': VK_SCROLL,
    'PRINTSCREEN': VK_SNAPSHOT,
    'PRINT_SCREEN': VK_SNAPSHOT,
    'WIN': VK_LWIN,
    'WINDOWS': VK_LWIN,
    'COMMAND': VK_LWIN,
    'CMD': VK_LWIN,
    'CMD_L': VK_LWIN,
    'CMD_R': VK_RWIN,
    'META': VK_LWIN,
    # OEM Symbols
    '`': VK_OEM_3,
    '~': VK_OEM_3,
    'TILDE': VK_OEM_3,
    'GRAVE': VK_OEM_3,
    '-': VK_OEM_MINUS,
    'MINUS': VK_OEM_MINUS,
    '=': VK_OEM_PLUS,
    'EQUALS': VK_OEM_PLUS,
    'EQUAL': VK_OEM_PLUS,
    '[': VK_OEM_4,
    'LBRACKET': VK_OEM_4,
    ']': VK_OEM_6,
    'RBRACKET': VK_OEM_6,
    '\\': VK_OEM_5,
    'BACKSLASH': VK_OEM_5,
    ';': VK_OEM_1,
    'SEMICOLON': VK_OEM_1,
    "'": VK_OEM_7,
    'QUOTE': VK_OEM_7,
    'APOSTROPHE': VK_OEM_7,
    ',': VK_OEM_COMMA,
    'COMMA': VK_OEM_COMMA,
    '.': VK_OEM_PERIOD,
    'PERIOD': VK_OEM_PERIOD,
    '/': VK_OEM_2,
    'SLASH': VK_OEM_2,
    # Numpad Keys
    'NUMPAD0': VK_NUMPAD0, 'NUM0': VK_NUMPAD0,
    'NUMPAD1': VK_NUMPAD1, 'NUM1': VK_NUMPAD1,
    'NUMPAD2': VK_NUMPAD2, 'NUM2': VK_NUMPAD2,
    'NUMPAD3': VK_NUMPAD3, 'NUM3': VK_NUMPAD3,
    'NUMPAD4': VK_NUMPAD4, 'NUM4': VK_NUMPAD4,
    'NUMPAD5': VK_NUMPAD5, 'NUM5': VK_NUMPAD5,
    'NUMPAD6': VK_NUMPAD6, 'NUM6': VK_NUMPAD6,
    'NUMPAD7': VK_NUMPAD7, 'NUM7': VK_NUMPAD7,
    'NUMPAD8': VK_NUMPAD8, 'NUM8': VK_NUMPAD8,
    'NUMPAD9': VK_NUMPAD9, 'NUM9': VK_NUMPAD9,
    'NUMPAD_ADD': VK_ADD, 'NUMADD': VK_ADD,
    'NUMPAD_SUB': VK_SUBTRACT, 'NUMSUB': VK_SUBTRACT,
    'NUMPAD_MUL': VK_MULTIPLY, 'NUMMUL': VK_MULTIPLY,
    'NUMPAD_DIV': VK_DIVIDE, 'NUMDIV': VK_DIVIDE,
    'NUMPAD_DECIMAL': VK_DECIMAL, 'NUMDEC': VK_DECIMAL,
    # Mouse Buttons
    'MOUSE_LEFT': VK_LBUTTON, 'MOUSE_L': VK_LBUTTON,
    'MOUSE_RIGHT': VK_RBUTTON, 'MOUSE_R': VK_RBUTTON,
    'MOUSE_MIDDLE': VK_MBUTTON, 'MOUSE_M': VK_MBUTTON,
    'MOUSE4': VK_XBUTTON1, 'XBUTTON1': VK_XBUTTON1, 'MOUSE_SIDE1': VK_XBUTTON1,
    'MOUSE5': VK_XBUTTON2, 'XBUTTON2': VK_XBUTTON2, 'MOUSE_SIDE2': VK_XBUTTON2,
}

ADB_KEY_MAP = {
    'esc': 'KEYCODE_ESCAPE',
    'enter': 'KEYCODE_ENTER',
    'return': 'KEYCODE_ENTER',
    'space': 'KEYCODE_SPACE',
    'backspace': 'KEYCODE_DEL',
    'delete': 'KEYCODE_FORWARD_DEL',
    'tab': 'KEYCODE_TAB',
    'home': 'KEYCODE_HOME',
    'pageup': 'KEYCODE_PAGE_UP',
    'page_up': 'KEYCODE_PAGE_UP',
    'pagedown': 'KEYCODE_PAGE_DOWN',
    'page_down': 'KEYCODE_PAGE_DOWN',
    'up': 'KEYCODE_DPAD_UP',
    'down': 'KEYCODE_DPAD_DOWN',
    'left': 'KEYCODE_DPAD_LEFT',
    'right': 'KEYCODE_DPAD_RIGHT',
    'alt': 'KEYCODE_ALT_LEFT',
    'lalt': 'KEYCODE_ALT_LEFT',
    'alt_l': 'KEYCODE_ALT_LEFT',
    'ralt': 'KEYCODE_ALT_RIGHT',
    'alt_r': 'KEYCODE_ALT_RIGHT',
    'alt_gr': 'KEYCODE_ALT_RIGHT',
    'ctrl': 'KEYCODE_CTRL_LEFT',
    'control': 'KEYCODE_CTRL_LEFT',
    'lctrl': 'KEYCODE_CTRL_LEFT',
    'lcontrol': 'KEYCODE_CTRL_LEFT',
    'ctrl_l': 'KEYCODE_CTRL_LEFT',
    'rctrl': 'KEYCODE_CTRL_RIGHT',
    'rcontrol': 'KEYCODE_CTRL_RIGHT',
    'ctrl_r': 'KEYCODE_CTRL_RIGHT',
    'shift': 'KEYCODE_SHIFT_LEFT',
    'lshift': 'KEYCODE_SHIFT_LEFT',
    'shift_l': 'KEYCODE_SHIFT_LEFT',
    'rshift': 'KEYCODE_SHIFT_RIGHT',
    'shift_r': 'KEYCODE_SHIFT_RIGHT',
    'capslock': 'KEYCODE_CAPS_LOCK',
    'caps_lock': 'KEYCODE_CAPS_LOCK',
    'numlock': 'KEYCODE_NUM_LOCK',
    'num_lock': 'KEYCODE_NUM_LOCK',
    'scrolllock': 'KEYCODE_SCROLL_LOCK',
    'scroll_lock': 'KEYCODE_SCROLL_LOCK',
    'printscreen': 'KEYCODE_SYSRQ',
    'print_screen': 'KEYCODE_SYSRQ',
}

# Mouse button constants
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C
WM_XBUTTONDBLCLK = 0x020D
MK_XBUTTON1 = 0x0020
MK_XBUTTON2 = 0x0040

MOUSE_XBUTTON1 = 'mouse4'
MOUSE_XBUTTON2 = 'mouse5'

MOUSE_BUTTON_MAP = {
    'mouse4': XBUTTON1,
    'mouse5': XBUTTON2,
    'xbutton1': XBUTTON1,
    'xbutton2': XBUTTON2,
}


def is_mouse_button(key) -> bool:
    if not isinstance(key, str):
        return False
    return key.strip().lower() in MOUSE_BUTTON_MAP


def get_mouse_button(key) -> int:
    if not isinstance(key, str):
        return 0
    return MOUSE_BUTTON_MAP.get(key.strip().lower(), 0)

