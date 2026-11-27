from types import SimpleNamespace
from unittest.mock import MagicMock

from ok.ui.qt.shell import run_bar


def _make_dummy_runbar():
    dummy = SimpleNamespace()
    dummy.linux_hotkey_listener = None
    dummy.toggle_requested = SimpleNamespace(emit=MagicMock())
    return dummy


def test_rebind_hotkey_prefers_evdev_when_available(monkeypatch):
    dummy = _make_dummy_runbar()
    evdev_instance = MagicMock()
    evdev_cls = MagicMock(return_value=evdev_instance)
    pynput_cls = MagicMock()

    monkeypatch.setattr(run_bar, 'evdev', object())
    monkeypatch.setattr(run_bar, 'HOTKEY_EVDEV_CODES', {'F9': 67})
    monkeypatch.setattr(run_bar, '_EvdevHotkeyListener', evdev_cls)
    monkeypatch.setattr(run_bar.pynput_keyboard, 'GlobalHotKeys', pynput_cls)

    run_bar.RunBar._rebind_hotkey(dummy, 'F9')

    evdev_cls.assert_called_once_with(67, dummy.toggle_requested.emit)
    evdev_instance.start.assert_called_once_with()
    pynput_cls.assert_not_called()
    assert dummy.linux_hotkey_listener is evdev_instance


def test_rebind_hotkey_falls_back_to_pynput_when_evdev_denied(monkeypatch):
    dummy = _make_dummy_runbar()
    pynput_instance = MagicMock()
    pynput_cls = MagicMock(return_value=pynput_instance)

    monkeypatch.setattr(run_bar, 'evdev', object())
    monkeypatch.setattr(run_bar, 'HOTKEY_EVDEV_CODES', {'F9': 67})
    monkeypatch.setattr(run_bar, '_EvdevHotkeyListener', MagicMock(side_effect=PermissionError('denied')))
    monkeypatch.setattr(run_bar.pynput_keyboard, 'GlobalHotKeys', pynput_cls)

    run_bar.RunBar._rebind_hotkey(dummy, 'F9')

    pynput_cls.assert_called_once_with({'<f9>': dummy.toggle_requested.emit})
    pynput_instance.start.assert_called_once_with()
    assert dummy.linux_hotkey_listener is pynput_instance
