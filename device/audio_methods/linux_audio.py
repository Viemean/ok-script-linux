import threading
from typing import List, Optional
from ok.util.logger import Logger

logger = Logger.get_logger(__name__)


def _resolve_default_targets() -> List[str]:
    targets = ["wine64-preloader"]
    try:
        from ok import og
        if og and og.config:
            win_cfg = og.config.get("windows") or {}
            custom = win_cfg.get("audio_targets")
            if custom:
                if isinstance(custom, list):
                    targets.extend([str(c).lower() for c in custom if c])
                elif isinstance(custom, str):
                    targets.append(custom.lower())
            exe = win_cfg.get("exe")
            if exe:
                if isinstance(exe, list):
                    for item in exe:
                        stem = str(item).rsplit(".", 1)[0].lower()
                        targets.append(stem)
                elif isinstance(exe, str):
                    stem = exe.rsplit(".", 1)[0].lower()
                    targets.append(stem)
    except Exception:
        pass
    return list(dict.fromkeys(targets))


class LinuxAudioController:
    """Controls game audio stream mute state via PulseAudio/PipeWire."""

    def __init__(self, target_names: Optional[List[str]] = None):
        self._custom_targets = [n.lower() for n in target_names if n] if target_names else None
        self._lock = threading.Lock()

    @property
    def target_names(self) -> List[str]:
        if self._custom_targets is not None:
            return self._custom_targets
        return _resolve_default_targets()

    def _match_sink_input(self, sink_input) -> bool:
        app = str(sink_input.proplist.get("application.name", "")).lower()
        binary = str(sink_input.proplist.get("application.process.binary", "")).lower()
        media = str(sink_input.proplist.get("media.name", "")).lower()
        node = str(sink_input.proplist.get("node.name", "")).lower()
        for target in self.target_names:
            if target in app or target in binary or target in media or target in node:
                return True
        return False

    def get_mute_state(self) -> int:
        try:
            import pulsectl
            with self._lock, pulsectl.Pulse("ok-audio-query") as pulse:
                for si in pulse.sink_input_list():
                    if self._match_sink_input(si):
                        return 1 if si.mute else 0
        except Exception as e:
            logger.debug(f"get_mute_state failed: {e}")
        return 0

    def set_mute_state(self, mute: int) -> bool:
        try:
            import pulsectl
            with self._lock, pulsectl.Pulse("ok-audio-ctrl") as pulse:
                matched = False
                for si in pulse.sink_input_list():
                    if self._match_sink_input(si):
                        if bool(si.mute) != bool(mute):
                            pulse.sink_input_mute(si.index, int(mute))
                            logger.info(f"sink_input {si.index} ({si.name}) mute state changed: {si.mute} -> {int(mute)}")
                        matched = True
                return matched
        except Exception as e:
            logger.debug(f"set_mute_state failed: {e}")
            return False


linux_audio_controller = LinuxAudioController()


def get_mute_state(hwnd=None) -> int:
    return linux_audio_controller.get_mute_state()


def set_mute_state(hwnd=None, mute: int = 0) -> bool:
    return linux_audio_controller.set_mute_state(mute)
