"""Platform compatibility layer for ok-script on non-Windows systems."""
import sys
import ctypes
import types


class _WindowsStub:
    """A minimal fallback stub for Windows attributes."""

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        return _WindowsStub()

    def __call__(self, *args, **kwargs):
        return 0

    def __int__(self):
        return 0

    def __bool__(self):
        return False

    def __iter__(self):
        return iter([])


def init_platform_compat():
    """Initialize safe ctypes fallback on Linux runtime."""
    if not hasattr(ctypes, 'windll'):
        ctypes.windll = _WindowsStub()
    if not hasattr(ctypes, 'WinDLL'):
        ctypes.WinDLL = lambda *args, **kwargs: _WindowsStub()
